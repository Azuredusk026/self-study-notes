# Forward、Deferred 与 Clustered 渲染

渲染路径的主要差别是：什么时候计算材质和光照，怎样找出影响当前表面或像素的光源，以及中间数据如何保存。

## Forward Rendering

Forward 在绘制物体时直接计算光照并输出最终颜色。

简化流程：

```text
Object → Vertex Shader → Rasterization → Material + Lights → Color
```

优点：

- 流程直接；
- 透明和自定义材质容易接入；
- MSAA 相对自然；
- 中间 Buffer 少，适合带宽敏感平台。

问题是要先决定每个物体受哪些灯影响。传统 Multi-pass Forward 可能对额外灯重复绘制物体；Single-pass Forward 会把灯列表传给 Shader，但列表长度和分支受限。

不能简单说 Forward 的复杂度是 $N^2$。实际成本取决于可见对象、每个对象重叠灯数、屏幕覆盖、Pass 和剔除策略。

## Deferred Rendering

Deferred 先把可见表面的属性写入 GBuffer，再在屏幕空间计算光照。

### Geometry Pass

典型 GBuffer 保存：

- Base Color；
- Normal；
- Roughness、Metallic、AO；
- Emissive 或材质分类；
- Depth；
- Motion Vector 常在独立 Buffer。

具体布局取决于引擎、平台和材质模型。每多一个通道都会增加显存和带宽。

一次像素着色同时写入多个颜色 Attachment 称为多渲染目标（Multiple Render Targets，MRT）。GBuffer 正是典型用法。MRT 减少重复几何绘制，但所有目标的总字节数都会进入颜色写带宽；平台还会限制目标数量、格式组合和混合能力。

HLSL 可以用多个 `SV_Target` 明确 GBuffer 写入。下面的布局只表达数据流，具体项目还需要压缩法线并选择可用格式：

```hlsl
struct GBufferOutput
{
    float4 baseColorMetallic : SV_Target0;
    float4 normalRoughness : SV_Target1;
    float4 emissiveAO : SV_Target2;
};

GBufferOutput WriteGBuffer(MaterialData m)
{
    GBufferOutput output;
    output.baseColorMetallic = float4(m.baseColor, m.metallic);
    output.normalRoughness = float4(normalize(m.normalVS) * 0.5 + 0.5,
                                    m.roughness);
    output.emissiveAO = float4(m.emissive, m.ao);
    return output;
}
```

存储观察空间位置通常需要较高带宽。常见做法是保存硬件深度，在 Lighting Pass 用逆投影矩阵重建：

```hlsl
float3 ReconstructPositionVS(float2 uv, float deviceDepth)
{
    float2 ndcXY = uv * 2.0 - 1.0;
    float4 positionH = mul(InvProjection,
                           float4(ndcXY, deviceDepth, 1.0));
    return positionH.xyz / positionH.w;
}
```

`deviceDepth` 的 NDC 范围、Y 轴和反向 Z 取决于 API 与引擎。重建函数必须和生成 Depth Buffer 的投影矩阵使用同一约定。

### Lighting Pass

读取 GBuffer，重建表面位置，再累加灯光。

有 100 盏灯时，不是“只读一次 GBuffer 就结束”。仍要计算影响像素的灯，只是材质和几何属性不必对每盏灯重复绘制。

## Deferred 中怎样画灯

### Fullscreen Pass

方向光影响全屏，可以画一个全屏三角形。每个像素读取 GBuffer 并计算方向光。

### Light Volume

点光源用球体、Spot Light 用锥体近似影响范围。只在 Volume 覆盖的像素计算该灯。

Depth/Stencil、Front/Back Face 和相机位于 Volume 内外时的状态需要正确设置，否则会漏算或重复计算。

#### 用模板精确圈定光体积

直接绘制光体积几何体有个问题：如何只对"真正位于光照范围内"的像素着色。相机在体积内外、几何体正反面都会影响判断，单靠深度测试容易漏算或重复计算。

模板缓冲提供了一个稳健的两步方案：

**第一步，标记**。绘制光体积几何体，关闭颜色输出，只在深度测试失败处翻转模板的标记位：

```text
ColorMask 0
compare = NotEqual, readMask = 对象类别掩码
zFail   = IncrementWrap, writeMask = 标记位
```

深度测试失败意味着该处已有更近的几何——也就是说，场景表面位于光体积的这一部分之内。翻转操作把这些像素标记出来。读掩码同时限定只处理需要光照的对象类别，天空等被排除。

**第二步，着色**。只对刚标记的像素执行光照，着色完把标记清零：

```text
compare = Equal, reference = 标记位
pass    = Zero
```

清零让同一个标记位可以被下一盏灯复用。这很关键——模板位宽紧张，几十盏灯不可能各占一位。

#### 聚光灯几何体的顶点变形

点光用球体近似，聚光灯的圆锥则有一个实际问题：每盏灯的张角与长度不同，为每种参数准备一个网格不现实。

做法是在顶点着色器中把统一的半球网格现场变形为所需的锥体：先按参数缩放偏移，归一化后乘以长度，再做一次轻微外扩以保证多面体网格能完全包住解析的圆锥形状：

```hlsl
positionOS = spotLightBias.xyz + lightSpotScale.xyz * positionOS;
positionOS = normalize(positionOS) * lightSpotScale.w;
// 轻微膨胀，确保离散网格包住解析锥体
positionOS = (positionOS - float3(0, 0, guard.w)) * guard.xyz + float3(0, 0, guard.w);
```

外扩不可省略：网格是有限面数的多面体，内接于理想锥体时边缘会漏掉一部分本应受光的像素。

还有一个容易出错的细节——**三维光体积的屏幕 UV 必须在片元着色器中从屏幕坐标现算**，不能在顶点着色器算好再插值。光体积是三维几何，插值会经过透视校正，得到的 UV 与实际屏幕位置不符。全屏四边形没有这个问题，因为它本就贴在屏幕上。
### Tiled Deferred

先把屏幕分成 Tile，例如 16x16。Compute Shader 计算每个 Tile 与哪些灯相交，再让像素只遍历该 Tile 的灯列表。

它减少大量小 Light Volume Draw，也提高同 Tile 线程读取光源数据的局部性。

## Forward+

Forward+ 保留 Forward 材质阶段，但先用 Tiled/Clustered Culling 建立灯列表。Pixel Shader 只遍历当前区域的灯。

它结合了：

- Forward 对透明、MSAA 和复杂材质的适应；
- 屏幕分区对大量灯的筛选能力。

代价是需要构建灯列表，且不透明和透明阶段可能使用不同列表或深度信息。

## Clustered Rendering

二维 Tile 无法区分同一屏幕区域内近处和远处的灯。Clustered Rendering 再沿深度划分，把视锥变成三维 Cluster。

### 二维 Tile 与 Z Bin 分离

Clustered 的一种实现方式是把 XY 与 Z 两个维度**分开预计算**，而非直接构建三维 Cluster 列表。

屏幕切成若干 Tile，深度范围切成若干 Bin，分别计算各自影响的灯光集合并存为位掩码。着色时取当前像素所在 Tile 的掩码与所在 Bin 的掩码求交：

$$
\text{lights} = \text{mask}_{XY} \;\&\; \text{mask}_{Z}
$$

相比直接存三维 Cluster 列表，这种分离的存储量从 $N_x \times N_y \times N_z$ 降到 $N_x \times N_y + N_z$。代价是求交结果偏保守——某盏灯可能同时命中某个 Tile 和某个 Bin，实际却不在两者的交叉区域内。

这个保守性在多数场景下可以接受，因为多算几盏灯的成本远低于存储与构建完整三维列表。深度跨度极大或灯光分布极不均匀时需要实测确认。

两个剔除 Kernel 的工作方式不同：XY 方向对 Tile 视锥的角射线做求交测试，Z 方向用前后两个平面做包含测试。前者可以让相邻 Tile 共享角点的计算结果。

优势：

- 深度跨度大的场景中灯列表更短；
- 透明物体可以根据自身深度选择 Cluster；
- 适合大量局部灯、Decal 和 Probe。

问题：

- Cluster 尺寸和深度切分需要调节；
- 灯列表需要前缀和、原子或固定上限；
- 超大灯会进入很多 Cluster；
- 列表溢出必须有明确行为。

## Deferred 的限制

- GBuffer 带宽和内存大；
- 多材质模型需要编码分类或额外数据；
- 透明通常仍走 Forward；
- MSAA 成本和 Resolve 更复杂；
- 移动端 Tile-based GPU 可能不适合把大 GBuffer 写回外部内存；
- 每像素只保留最前表面，不适合多层材质。

### 移动端的特殊路径

最后两条在移动端需要单独展开。TBDR 架构把渲染分块进行，每个 Tile 的中间结果驻留在片上内存（Tile Memory）中，只在 Pass 结束时写回主存。

朴素的延迟渲染在这里代价极高：GBuffer 写回主存、Lighting Pass 再从主存读回，一来一回的带宽在移动端是致命的。

解法是把 Geometry 与 Lighting 合并进同一个 Render Pass，让 GBuffer 始终留在 Tile Memory 中不落主存。Vulkan 的 Subpass 与 Metal 的 Programmable Blending 提供了这个能力，引擎侧对应的是各类"移动端延迟渲染"路径。

约束随之而来：Tile Memory 容量有限，GBuffer 通道数与格式必须严格压缩；两个阶段必须在同一 Pass 内，中间不能插入需要完整画面的操作；只能读取当前像素位置的 GBuffer，无法采样邻域。

这解释了为什么移动端延迟路径的 GBuffer 布局通常比桌面端精简得多，也解释了为什么某些屏幕空间效果在移动端延迟路径下不可用。

### 自定义着色模型的接入难度

延迟路径下，材质只负责把数据写进 GBuffer，光照由统一的 Lighting Pass 计算。想要一种新的着色方式，就必须让 Lighting Pass 知道如何处理它。

两条路：在 GBuffer 中编码材质分类 ID，让 Lighting Pass 分支到不同着色函数；或者扩展 GBuffer 携带额外参数。前者受限于分类位宽，后者增加带宽。

这是延迟路径与前向路径在扩展性上的本质差异：前向路径下每个材质自带完整光照代码，加一种着色方式只需写一个新 Shader；延迟路径下必须改动引擎的光照阶段。

以 Unity URP 为例，Lit Shader 的 GBuffer Pass 通过 `LightMode` 标签标识，片元阶段先求出标准的 BRDF 数据与全局光照，再统一打包写入四个目标——其中一个同时承担相机颜色附件的职责。想插入自定义着色，要么在写入前修改这批数据，要么改动管线的解包与光照代码。

## Deferred 并不一定更快

大量小灯、复杂不透明材质时可能占优。灯很少、分辨率高、带宽有限或透明很多时，Forward/Forward+ 可能更合适。

比较应记录：

- Geometry 和 Lighting Pass GPU 时间；
- GBuffer 字节/像素；
- 平均每 Tile/Cluster 灯数；
- Light List 构建成本；
- 透明和后处理占比；
- 目标 GPU 的带宽和 Tile 架构。

## 验证方法

- 在 Frame Capture 中找 Geometry Pass 和每个 Lighting Event。
- 单独查看 GBuffer 通道和材质分类。
- 统计每 Tile/Cluster 灯数、最大值和溢出。
- 用 100 个重叠灯和 100 个不重叠灯分别测试。
- 检查 Directional Fullscreen Pass、Point Light Volume 或 Compute Lighting 的实际执行。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[05_光照阴影与GI/光源与直接光照]]
- [[13_引擎架构与资源系统/GBuffer布局设计与通道压缩]]
- [[13_引擎架构与资源系统/Render Pass、Command Buffer与Render Graph]]
- [[14_性能分析与优化/帧时间、瓶颈与GPU成本]]

## 参考资料

- Ola Olsson et al., *Clustered Deferred and Forward Shading*.
- Johan Andersson, *Tiled Deferred Shading*.
- Unity and Unreal documentation on Forward+, Deferred and mobile renderers.
- LearnOpenGL, `src/5.advanced_lighting/8.1.deferred_shading`.
