# GBuffer布局

延迟光照要从GBuffer取出表面参数。如果给每个参数单独分配通道，布局很快会变大；若过度压缩，法线、分类或遮罩的误差又会改变光照。我们先看字段由谁消费，再用编码和复用减少成本。

## 先算带宽账

一张 1080p 的 RGBA8 纹理约 8 MB。几何阶段写一次、光照阶段读一次，每帧就是 16 MB 的流量；60 帧就是接近 1 GB/s。这是完整读写的逻辑字节量，不包含缓存、附件压缩和片上驻留；实际外部流量由平台测量。减少附件的收益取决于当前瓶颈。

布局数量由材质字段、渲染路径和消费者决定。两张GBuffer可以作为受限材质集合的设计目标，但不是所有桌面或移动管线的标准。压缩手段主要有三类：编码降维、位域打包、通道复用。

## 字段编码

### 八面体法线

世界空间法线是单位向量，只有两个自由度，用三个通道存储是浪费。

最朴素的做法是只存 XY、由 $z=\sqrt{1-x^2-y^2}$ 推算。它有两个硬伤：$z$ 接近 0 时导数发散、精度崩塌；且丢失符号，无法表达背向的法线。

八面体映射（Octahedral Encoding）把球面先投影到八面体，再展开成正方形，用两个数覆盖整个球面方向。它的精度分布远比半球投影均匀，且不丢符号：

```hlsl
float2 EncodeNormal(float3 normal)
{
    normal /= abs(normal.x) + abs(normal.y) + abs(normal.z);
    float2 f = normal.xy;
    if (normal.z < 0.0)
        f = (1.0 - abs(f.yx)) * float2(f.x >= 0 ? 1 : -1,
                                      f.y >= 0 ? 1 : -1);
    return f * 0.5 + 0.5;
}
```

完整编码/解码见 [Packing.hlsl](../examples/gbuffer/Packing.hlsl)。输入是非零单位法线，解码后归一化；下半球折叠保存符号。省下的一个通道可以安置 Smoothness 或 Metallic。8 位量化下八面体编码的角度误差通常在可接受范围内，但低粗糙度的镜面反射对法线精度敏感，需要实测确认——高光在光滑表面上出现阶梯状色带就是精度不足的典型信号。

存储格式必须是 UNorm 而非 SRGB。法线是数据不是颜色，走 sRGB 传递函数会引入非线性误差。

### 一个字节装两个字段

当两个量各自都不需要完整 8 位时，可以切分同一个字节。例如用高 3 位存一个 $0\sim7$ 的整数、低 5 位存一个 $[0,1]$ 的浮点：

输入浮点遮罩位于0–1，类别为0–7。先量化遮罩到0–31，再组成一个字节，写入R8_UNORM。读取时点采样，先恢复字节，再拆类别与遮罩：

```hlsl
uint q = (uint)floor(saturate(mask) * 31.0 + 0.5);
float packed = ((identifier & 7u) * 32u + q) / 255.0;
uint byteValue = (uint)floor(saturate(packed) * 255.0 + 0.5);
uint restoredId = byteValue / 32u;
float restoredMask = (byteValue % 32u) / 31.0;
```

这里的0.5是恢复整数时的半步偏移，量化误差由字段位宽决定。不能把打包值当颜色线性过滤：相邻类别混合会生成第三个类别。MSAA resolve、贴花和后处理都要保持这个字段契约。示例使用float计算，半精度行为在目标编译器和GPU上另测。

[reference.py](../examples/gbuffer/reference.py)遍历8种类别与32级遮罩，并检查端点和过滤反例，264项CPU检查通过。该结果支持R8_UNORM点读模型，不支持任意精度与过滤方式。5位遮罩误差上限约为1/(2×31)，是否满足AO或阴影用途由画面对照决定。

## 字段复用

### 互斥属性共用位置

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

复用的前提是当前着色模型确实不同时需要这些属性。示例中的头发和植被模型选择了互斥参数；其他材质体系可能同时需要它们。GBuffer 布局设计的典型思路就是先找出互斥的属性集合，再让它们共用通道。

代价是可读性。同一个通道的语义随材质分类变化，阅读与调试成本上升，必须在代码注释与文档中写明每种分类下的通道含义。

### 不同执行阶段复用字段

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

同样地，通道语义随执行阶段变化会显著增加维护成本。值得为每个复用点记录“从哪个 Pass 开始语义改变”。

## Framebuffer Fetch 与 Subpass

前面所有压缩手段都在减少数据量。移动端还有一条更彻底的路径：减少GBuffer的外部内存往返。

Tile-Based 架构的中间结果驻留在片上 Tile Memory 中，只在 Render Pass 结束时写回主存。如果几何阶段与光照阶段能合并成同一个 Render Pass 的多个 Subpass，GBuffer就有机会留在Tile Memory里，实际驻留由附件大小、设备和驱动决定。

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

局部附件读取可以减少外部读写，但仍有执行与片上访问成本。Shader签名是具体项目的表达示例，不能据此断言所有平台零成本。

约束也很明确：

- 只能读取**当前像素位置**的数据，无法采样邻域。需要模糊、扩散的效果不能放进 Subpass 链；
- 两个阶段必须在同一 Render Pass 内，中间不能插入需要完整画面的操作；
- Tile Memory 容量有限，GBuffer 总字节数必须严格控制——这反过来加强了前面压缩手段的必要性；
- Shader 需要维护两套签名，增加维护成本。

### Load 与 Store 操作

Subpass 的收益不只来自“数据留在片上”，还来自显式声明的 Load/Store 行为。每个 Attachment 在 Render Pass 开始与结束时各有一个操作：

| 操作 | 含义 | 带宽 |
|---|---|---|
| `LOAD_OP_LOAD` | 保留已有内容 | 可能增加加载，具体由实现决定 |
| `LOAD_OP_CLEAR` | 清成常量 | 可采用快速清除，实际计量 |
| `LOAD_OP_DONT_CARE` | 允许丢弃旧内容 | 不要求保留加载 |
| `STORE_OP_STORE` | 保留附件结果 | 可能增加存储，具体由实现决定 |
| `STORE_OP_DONT_CARE` | 允许丢弃结果 | 不要求保留存储 |

开始操作取决于是否完整写入或需要初始背景；结束操作取决于后续消费者。若同一渲染范围内光照已消费全部字段，范围外没有SSR、SSAO、贴花、调试或回读消费者，就可以丢弃对应附件。需要后续读取时保留STORE。

这是移动端最容易被忽略、收益却极高的一处。默认配置往往是 `LOAD` + `STORE`，仅仅把 GBuffer 的 Store 改成 `DONT_CARE`，就能省下每帧数张全屏纹理的写带宽。深度附件同理：不需要在后续 Pass 采样时，应当丢弃。

### 依赖声明

Subpass 之间的关系必须显式声明：后一个 Subpass 读取哪些 Attachment 作为 Input Attachment，以及两者之间的执行与内存依赖。

依赖声明不准确有两种后果。声明过松会出现竞态——光照阶段可能读到尚未写完的 GBuffer；声明过严则会引入不必要的同步，抵消合并的收益。

Input Attachment 在着色器中是独立的资源类型，读取时不经过采样器，只能取当前片元位置的值。这是 input attachment 接口的局部读取语义，适合片上保留附件。具体是否驻留 Tile Memory 由实现决定，普通邻域采样需要对应的纹理读取路径。

### 移动端的真实收益边界

Subpass 常被当作移动端延迟渲染的万能解，实际收益取决于几个条件，不满足时优势会大幅缩水：

**附件预算影响片上驻留**。格式、样本数、附件数量和设备的Tile组织都会影响片上压力。驱动如何拆分或溢出并不统一，用平台计数器和捕获核对结果，不能只按一个固定KB上限推断。

**中间不能插入需要完整画面的操作**。屏幕空间反射、屏幕空间阴影、任何需要采样邻域或整屏的效果都会打断 Subpass 链。真实管线中这类需求很常见，能够合并的往往只是链条的一段。

**驱动实现质量参差**。同样的声明在不同厂商、不同驱动版本上未必都能合并。是否真正生效必须用帧捕获或厂商工具确认，不能只看代码写法。

**与 MSAA 的交互复杂**。多采样 Attachment 占用的 Tile Memory 成倍增加，更容易超标；Resolve 时机也会影响能否合并。

因此“用了 Subpass 所以移动端更快”是一个需要验证的假设，而非结论。收益成立时非常可观，但前置条件不少。

### 从 Subpass 到 Dynamic Rendering

Vulkan 的 Render Pass 与 Subpass 对象需要提前声明完整的 Attachment 结构与依赖关系，样板代码多、与引擎的动态管线组织方式不契合，实践中被广泛认为难用。

后续版本引入的 Dynamic Rendering 取消了预先声明的 Render Pass 对象，改为在录制命令时直接指定 Attachment。它大幅简化了 API 使用，但最初并不具备 Subpass 的核心能力——读取同一位置的前序输出。

随后补充的 Local Read 一类扩展把这个能力带回了 Dynamic Rendering 路径，使得既能享受简化的 API，又能保留 Tile 内数据复用。

对使用者的意义是：**“Subpass 被取代”这个说法需要分开看**。被取代的是笨重的 Render Pass 对象声明方式；而“同一 Render Pass 内多阶段共享 Tile Memory”这个底层能力并未消失，只是换了表达形式。判断某个 API 路径是否可用，应当确认目标版本与驱动对相应扩展的支持，而不是看名词的新旧。

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

移动端还有一层收益来自精度限定。`real`等别名由项目宏、包版本和编译目标定义，不是硬件通用类型规则。检查预处理结果后再确认实际使用half还是float。

半精度在支持有效窄精度执行的目标上可能减少寄存器或ALU成本，对颜色、遮罩、法线这类值通常足够。但位置、深度、累加量需要全精度——半精度在大数值范围上的精度损失会直接表现为可见的跳变。

## 字段预算与方案选择

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
- 结合API捕获、图合并信息与厂商外部流量计数器，检查驻留和读写收益。
- 检查贴花绘制后目标像素的分类标记是否保持不变。

## 相关主题

- [[13_渲染架构/渲染路径与光源组织]]
- [[22_渲染引擎实现/Unreal自定义Mesh Pass]]
- [[02_GPU与光栅化管线/光栅化可见性导读]]
- [[04_光照模型与PBR/皮肤次表面散射]]
- [[14_性能分析与优化/移动端渲染优化]]
- [[13_渲染架构/渲染命令的组织方式]]

## 参考资料

- Zina Cigolle et al., *A Survey of Efficient Representations for Independent Unit Vectors*.
- Krzysztof Narkowicz, *Octahedron normal vector encoding*.
- Arm, *Mali GPU Best Practices*, Transaction Elimination and Framebuffer Fetch.
- Khronos, *Vulkan Specification*, Render Pass and Subpass Input Attachments.
- Apple, *Metal Programming Guide*, Programmable Blending.

核验范围：CPU打包参考检查和API中立HLSL编译已执行，完整GBuffer管线与目标GPU流量未运行验证。
