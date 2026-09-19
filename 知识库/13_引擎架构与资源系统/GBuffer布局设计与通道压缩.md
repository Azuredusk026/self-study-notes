# GBuffer 布局设计与通道压缩

延迟渲染把光照成本从"物体数 × 灯数"降到"屏幕像素数 × 灯数"，代价是每帧要写入并读回若干张全屏纹理。在带宽受限的平台上，这份代价直接决定方案可行与否——每多一张全屏 RT 就多一份读写带宽。

因此 GBuffer 布局不是"把需要的属性列出来各占一个通道"，而是一道约束优化题：在有限的字节数内，装下光照阶段真正需要的全部信息。

## 先算带宽账

一张 1080p 的 RGBA8 纹理约 8 MB。几何阶段写一次、光照阶段读一次，每帧就是 16 MB 的流量；60 帧就是接近 1 GB/s。四张 GBuffer 与两张的差距，在移动端往往就是能否达标的分界。

桌面端的典型延迟管线用四到六张 GBuffer。移动优先的方案可以压到两张，加上深度与着色累加区共四个 Attachment。压缩手段主要有三类：编码降维、位域打包、通道复用。

## 编码降维：八面体法线

世界空间法线是单位向量，只有两个自由度，用三个通道存储是浪费。

最朴素的做法是只存 XY、由 $z=\sqrt{1-x^2-y^2}$ 推算。它有两个硬伤：$z$ 接近 0 时导数发散、精度崩塌；且丢失符号，无法表达背向的法线。

八面体映射（Octahedral Encoding）把球面先投影到八面体，再展开成正方形，用两个数覆盖整个球面方向。它的精度分布远比半球投影均匀，且不丢符号：

```hlsl
float2 PackNormalWS(float3 normalWS)
{
    float2 oct = PackNormalOctQuadEncode(normalWS);
    return saturate(oct * 0.5 + 0.5);   // [-1,1] 映射到 [0,1] 以便存入 UNorm 通道
}

float3 UnpackNormalWS(float2 packed)
{
    return UnpackNormalOctQuadEncode(packed * 2.0 - 1.0);
}
```

省下的一个通道正好安置 Smoothness 或 Metallic。8 位量化下八面体编码的角度误差通常在可接受范围内，但低粗糙度的镜面反射对法线精度敏感，需要实测确认——高光在光滑表面上出现阶梯状色带就是精度不足的典型信号。

存储格式必须是 UNorm 而非 SRGB。法线是数据不是颜色，走 sRGB 传递函数会引入非线性误差。

## 位域打包：一个字节装两个值

当两个量各自都不需要完整 8 位时，可以切分同一个字节。例如用高 3 位存一个 $0\sim7$ 的整数、低 5 位存一个 $[0,1]$ 的浮点：

```hlsl
static const half t1 = 31.0 / 255.0;   // 5 位量化步长
static const half t2 = 32.0 / 255.0;   // 3 位进位步长

half PackFloat5UInt3(half floatPart, uint uintPart)
{
    return t1 * floatPart + t2 * half(uintPart);
}

uint UnpackUIntPart(half value)
{
    return uint((value / t2) + rcp(255.0));   // 补偿项不可省略
}

half UnpackFloatPart(half value, uint uintPart)
{
    return saturate((-t2 * half(uintPart) + value) / t1);
}
```

`rcp(255.0)` 这个补偿项是实现的关键。通道值经过量化与插值后是浮点数，理应为 3 的整数部分可能实际存成 2.9999，直接截断会得到 2，整个材质分类随之出错。加上半个量化步长的偏移可以把值推回正确区间。

不能改用 `round()` 代替：`round` 在不同平台的舍入行为与精度不完全一致，而这里需要的是确定性的向下取整加固定偏移。

这类打包的代价是精度：5 位意味着浮点部分只有 32 个可分辨等级。适合 AO、遮罩这类容差大的量，不适合直接参与高频计算的值。

## 通道复用：互斥属性共用位置

延迟渲染的经典缺陷是材质模型单一——GBuffer 字段固定，皮肤的次表面散射、头发的各向异性高光这类专用参数无处安放。

解法是给每个像素打一个材质分类标记，光照阶段按分类走不同的 BRDF 分支。前面的 3 位整数正是用于此：

```text
0 = Lit        普通 PBR
1 = Terrain    地形
2 = Plant      植被，需要透光
3 = Character  角色，布料等
4 = Skin       皮肤，需要次表面散射
5 = Hair       头发，需要各向异性高光
```

有了分类，同一个通道就可以在不同材质下表达不同含义：

```hlsl
if (isLit || isCharacter || isSkin)
    surfaceData.metallic = gbuffer1.a;
else if (isHair)
    surfaceData.anisotropicSpecularMask = gbuffer1.a;   // 同一通道
else if (isPlant)
    surfaceData.translucency = gbuffer1.a;              // 又不同
```

复用的前提是**属性互斥**：头发不需要金属度，植被不需要各向异性高光。GBuffer 布局设计的典型思路就是先找出互斥的属性集合，再让它们共用通道。

代价是可读性。同一个通道的语义随材质分类变化，阅读与调试成本上升，必须在代码注释与文档中写明每种分类下的通道含义。

## 时间维度的复用

除了按材质复用，还可以按**生命周期**复用：如果某个通道的数据在某个阶段之后不再需要，就可以拿它存别的东西。

一个实用案例是环境光与主光之间复用 Occlusion 通道：

```hlsl
// 环境光阶段末尾：AO 已经用完，写入主光阴影
surfaceData.occlusion = mainLightShadow;
gbuffer0 = real4(gbuffer0.rgb, PackFloat5UInt3(surfaceData.occlusion, identifier));
```

```hlsl
// 主光阶段：直接读出，无需额外的全屏阴影纹理
Light mainLight = GetMainLight();
mainLight.shadowAttenuation = surfaceData.occlusion;
```

这省掉了一张全屏阴影 RT。前提是严格确认后续没有任何 Pass 还需要原始 AO 值——这类复用一旦判断错误，表现为某些效果在特定材质上莫名失真，且极难定位。

同样地，通道语义随执行阶段变化会显著增加维护成本。值得为每个复用点记录"从哪个 Pass 开始语义改变"。

## Framebuffer Fetch 与 Subpass

前面所有压缩手段都在减少数据量。移动端还有一条更彻底的路径：让 GBuffer **根本不落显存**。

Tile-Based 架构的中间结果驻留在片上 Tile Memory 中，只在 Render Pass 结束时写回主存。如果几何阶段与光照阶段能合并成同一个 Render Pass 的多个 Subpass，GBuffer 就可以全程留在 Tile Memory 里。

Vulkan 的 Subpass 与 Metal 的 Framebuffer Fetch 提供这个能力。Shader 侧的表现是同一个 Attachment 既是输入又是输出：

```hlsl
#if _FRAME_BUFFER_FETCH_ENABLED
    inout real4 shadingColor    : CoLoR0,   // inout：读写同一块 Tile 内存
    inout real4 geometryBuffer0 : CoLoR1,
#else
    out   real4 shadingColor    : SV_Target0,  // 常规 MRT 输出
    out   real4 geometryBuffer0 : SV_Target1,
#endif
```

启用后，读取上一个 Subpass 的结果是零成本的——数据本来就在寄存器或片上内存中；未启用时则需要通过专门的 Framebuffer Input 指令加载。

约束也很明确：

- 只能读取**当前像素位置**的数据，无法采样邻域。需要模糊、扩散的效果不能放进 Subpass 链；
- 两个阶段必须在同一 Render Pass 内，中间不能插入需要完整画面的操作；
- Tile Memory 容量有限，GBuffer 总字节数必须严格控制——这反过来加强了前面压缩手段的必要性；
- Shader 需要维护两套签名，增加维护成本。

### Load 与 Store 操作

Subpass 的收益不只来自"数据留在片上"，还来自显式声明的 Load/Store 行为。每个 Attachment 在 Render Pass 开始与结束时各有一个操作：

| 操作 | 含义 | 带宽 |
|---|---|---|
| `LOAD_OP_LOAD` | 从主存读入已有内容 | 一次全屏读 |
| `LOAD_OP_CLEAR` | 清成常量 | 无 |
| `LOAD_OP_DONT_CARE` | 内容未定义 | 无 |
| `STORE_OP_STORE` | 写回主存 | 一次全屏写 |
| `STORE_OP_DONT_CARE` | 丢弃 | 无 |

GBuffer 的正确配置是 `CLEAR`/`DONT_CARE` 进、`DONT_CARE` 出——它只是中间数据，光照阶段用完就不再需要，写回主存纯属浪费。只有最终的着色结果需要 `STORE`。

这是移动端最容易被忽略、收益却极高的一处。默认配置往往是 `LOAD` + `STORE`，仅仅把 GBuffer 的 Store 改成 `DONT_CARE`，就能省下每帧数张全屏纹理的写带宽。深度附件同理：不需要在后续 Pass 采样时，应当丢弃。

### 依赖声明

Subpass 之间的关系必须显式声明：后一个 Subpass 读取哪些 Attachment 作为 Input Attachment，以及两者之间的执行与内存依赖。

依赖声明不准确有两种后果。声明过松会出现竞态——光照阶段可能读到尚未写完的 GBuffer；声明过严则会引入不必要的同步，抵消合并的收益。

Input Attachment 在着色器中是独立的资源类型，读取时不经过采样器，只能取当前片元位置的值。这个限制不是实现偷懒，而是硬件本质：Tile Memory 中只有当前 Tile 的数据，邻域可能根本不在片上。

### 移动端的真实收益边界

Subpass 常被当作移动端延迟渲染的万能解，实际收益取决于几个条件，不满足时优势会大幅缩水：

**GBuffer 必须装得进 Tile Memory**。片上内存通常只有几十到上百 KB，按每像素字节数折算，GBuffer 总位宽超标时驱动会退回普通多 Pass 路径——代码照常运行，收益悄然消失。这正是前面各种压缩手段的意义所在。

**中间不能插入需要完整画面的操作**。屏幕空间反射、屏幕空间阴影、任何需要采样邻域或整屏的效果都会打断 Subpass 链。真实管线中这类需求很常见，能够合并的往往只是链条的一段。

**驱动实现质量参差**。同样的声明在不同厂商、不同驱动版本上未必都能合并。是否真正生效必须用帧捕获或厂商工具确认，不能只看代码写法。

**与 MSAA 的交互复杂**。多采样 Attachment 占用的 Tile Memory 成倍增加，更容易超标；Resolve 时机也会影响能否合并。

因此"用了 Subpass 所以移动端更快"是一个需要验证的假设，而非结论。收益成立时非常可观，但前置条件不少。

### 从 Subpass 到 Dynamic Rendering

Vulkan 的 Render Pass 与 Subpass 对象需要提前声明完整的 Attachment 结构与依赖关系，样板代码多、与引擎的动态管线组织方式不契合，实践中被广泛认为难用。

后续版本引入的 Dynamic Rendering 取消了预先声明的 Render Pass 对象，改为在录制命令时直接指定 Attachment。它大幅简化了 API 使用，但最初并不具备 Subpass 的核心能力——读取同一位置的前序输出。

随后补充的 Local Read 一类扩展把这个能力带回了 Dynamic Rendering 路径，使得既能享受简化的 API，又能保留 Tile 内数据复用。

对使用者的意义是：**"Subpass 被取代"这个说法需要分开看**。被取代的是笨重的 Render Pass 对象声明方式；而"同一 Render Pass 内多阶段共享 Tile Memory"这个底层能力并未消失，只是换了表达形式。判断某个 API 路径是否可用，应当确认目标版本与驱动对相应扩展的支持，而不是看名词的新旧。
## 特殊 Pass：贴花

贴花是 GBuffer 阶段的一个特例。它不应改变深度，因此不输出深度；而它需要与已有 GBuffer 内容混合，而非覆盖。

当 Alpha 通道已被占用（存放 Occlusion 与分类标记）时，硬件混合无法直接使用，需要把 Alpha 挪作混合权重并手动混合：

```hlsl
half4 DecalBlendManually(half4 dst, half4 src)
{
    return half4(lerp(dst.xyz, src.xyz, src.w), dst.w);   // 保留 dst 的 Alpha
}
```

注意结果保留了 `dst.w`——目标的分类标记与 AO 不能被贴花破坏，否则该像素的光照分支会走错。

## 精度类型

移动端还有一层收益来自精度限定。`real` 一类的抽象类型在移动平台展开为 `half`（16 位）、桌面端为 `float`（32 位）。

半精度减少寄存器占用与 ALU 开销，对颜色、遮罩、法线这类值通常足够。但位置、深度、累加量需要全精度——半精度在大数值范围上的精度损失会直接表现为可见的跳变。

## 设计取舍总览

| 收益 | 代价 |
|---|---|
| 光照与几何解耦，多光源成本可控 | 半透明无法进 GBuffer，需单独前向通道 |
| 压到两张 GBuffer，带宽友好 | 属性精度受限，法线 16 位、AO 仅 5 位 |
| 分类标记支持多种 BRDF | 光照 Shader 出现分支，需要压平 |
| Subpass 让 GBuffer 不落显存 | Shader 维护两套签名，且无法采样邻域 |
| 通道二次复用省下整张 RT | 通道语义随阶段变化，阅读与调试成本高 |

这些取舍没有普适答案。桌面端带宽充裕，过度压缩只会徒增复杂度与精度损失；移动端则可能必须付出全部这些代价才能达标。

## 验证方法

- 逐张输出 GBuffer 内容为可视化颜色，确认每个通道在各类材质上取值合理。
- 单独验证打包与解包：对分类标记从 0 到 7 逐个写入再读出，确认往返一致，尤其检查边界值。
- 用一个粗糙度极低的金属球检查八面体编码精度，高光出现阶梯色带说明位数不足。
- 统计 GBuffer 总字节数与每帧读写带宽，与目标平台的可用带宽对比。
- 开关 Framebuffer Fetch 两条路径分别验证，两者结果应当一致。
- 在帧捕获中确认 Subpass 确实合并，GBuffer 未被写回主存。
- 检查贴花绘制后目标像素的分类标记是否保持不变。

## 相关主题

- [[13_引擎架构与资源系统/Forward、Deferred与Clustered渲染]]
- [[13_引擎架构与资源系统/Unreal网格绘制与自定义Pass]]
- [[02_GPU与光栅化管线/光栅化、插值与深度模板]]
- [[04_光照模型与PBR/次表面散射与皮肤渲染]]
- [[14_性能分析与优化/渲染优化验证与移动端实践]]
- [[13_引擎架构与资源系统/Render Pass、Command Buffer与Render Graph]]

## 参考资料

- Zina Cigolle et al., *A Survey of Efficient Representations for Independent Unit Vectors*.
- Krzysztof Narkowicz, *Octahedron normal vector encoding*.
- Arm, *Mali GPU Best Practices*, Transaction Elimination and Framebuffer Fetch.
- Khronos, *Vulkan Specification*, Render Pass and Subpass Input Attachments.
- Apple, *Metal Programming Guide*, Programmable Blending.
