# Deferred Rendering

多个灯反复需要同一表面参数，可以先把最近表面的材质写进GBuffer，再在光照阶段读取。这样减少某些重复几何工作，却增加附件与光照消费成本。我们从写入和解码追到光体积与局部列表，再看透明、平台和自定义模型在哪些地方需要另一条路径。

## Deferred Rendering

Deferred 先把可见表面的属性写入 GBuffer，再在屏幕空间计算光照。

### 几何通道

典型 GBuffer 保存：

- 基础色；
- 法线；
- 粗糙度、金属度、AO；
- 自发光或材质分类；
- 深度；
- 运动向量常在独立缓冲。

具体布局取决于引擎、平台和材质模型。每多一个通道都会增加显存和带宽。

一次像素着色同时写入多个颜色附件称为多渲染目标（Multiple Render Targets，MRT）。GBuffer 正是典型用法。MRT 减少重复几何绘制，但所有目标的总字节数都会进入颜色写带宽；平台还会限制目标数量、格式组合和混合能力。

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

存储观察空间位置通常需要较高带宽。常见做法是保存硬件深度，在光照 Pass 用逆投影矩阵重建：

```hlsl
float3 ReconstructPositionVS(float2 uv, float deviceDepth)
{
    float2 ndcXY = uv * 2.0 - 1.0;
    float4 positionH = mul(InvProjection,
                           float4(ndcXY, deviceDepth, 1.0));
    return positionH.xyz / positionH.w;
}
```

`deviceDepth` 的 NDC 范围、Y 轴和反向 Z 取决于 API 与引擎。重建函数必须和生成深度缓冲的投影矩阵使用同一约定。

### 光照通道

读取 GBuffer，重建表面位置，再累加灯光。

有 100 盏灯时，不是“只读一次 GBuffer 就结束”。仍要计算影响像素的灯，只是材质和几何属性不必对每盏灯重复绘制。

## 延迟光照的绘制范围

### 全屏通道

方向光影响全屏，可以画一个全屏三角形。每个像素读取 GBuffer 并计算方向光。

### 光体积

点光源用球体、Spot 光源用锥体近似影响范围。只在 Volume 覆盖的像素计算该灯。

深度/Stencil、Front/Back Face 和相机位于 Volume 内外时的状态需要正确设置，否则会漏算或重复计算。

#### 光体积与场景位置判断

光体积网格先限制屏幕覆盖，片元阶段再重建场景位置并判断它是否真正位于解析光范围。以点光源为例，输入 GBuffer 深度、世界位置重建结果 P、灯位置 C 和半径 r：

```hlsl
float3 toLight = lightPositionWS - surfacePositionWS;
if (dot(toLight, toLight) > lightRadius * lightRadius) discard;
float3 contribution = EvaluatePointLight(surface, toLight);
```

这是几何范围判断片段，`EvaluatePointLight` 的 BRDF、衰减和阴影由直接光照专篇给出。关闭深度写入，用加法混合累计灯光；覆盖网格选择不会漏掉球投影的外接体。相机位于体积内部或体积被近裁剪面切开时，可切换全屏三角形并保留相同范围判断，先确保正确，再优化覆盖。

模板可进一步减少无效片元，但需要成对处理闭合体积的前后面、深度比较及近面裁剪。单次“深度失败”只说明该片元在场景后面，不能证明场景点位于体积内部。模板计数与对象分类共用时，还要分配独立位域，避免增减计数污染分类。

#### 聚光灯几何体的顶点变形

点光用球体近似，聚光灯的圆锥则有一个实际问题：每盏灯的张角与长度不同，为每种参数准备一个网格不现实。

可以复用一个闭合的 N 边锥体网格：局部轴取 +Z，顶点在原点，底面位于 z=1，底面顶点在单位圆上。灯的轴向长度为 L、外半角为 θ，且 `0 < θ < π/2`、`N >= 3`。理想底面半径是 `L*tan(θ)`，正 N 边形外接圆半径需再乘 `1/cos(π/N)`，其边中点才能落在理想圆外缘。

```hlsl
float outerRadius = axialLength * tan(outerHalfAngle) / cos(PI / sideCount);
positionOS.xy *= outerRadius;
positionOS.z *= axialLength;
```

该片段已由[独立检查脚本](../examples/revision_09_15/README.md)抽取并编译，仅验证类型与语法。片段输入上述单位锥体顶点，角度使用弧度，输出为灯局部空间；随后用灯变换送到世界与裁剪空间。锥尖、侧面和底盖共同形成闭合外接体。若灯的实际距离按球面半径截断，轴向锥体只负责保守覆盖，片元仍要做距离及角度判断。相机位于体积内或近面切开体积时，沿用前述全屏回退。

还有一个容易出错的细节——**三维光体积的屏幕 UV 可以在片元着色器中由屏幕坐标计算**，若在顶点阶段准备屏幕参数，需要保留正确的齐次分量并在片元阶段除法，或使用适当插值约定。直接插值已经除过 w 的 UV 又使用默认透视校正，会与实际屏幕位置不符。全屏四边形没有这个问题，因为它本就贴在屏幕上。

### Tiled Deferred

先把屏幕分成 Tile，例如 16x16。计算着色器计算每个 Tile 与哪些灯相交，再让像素只遍历该 Tile 的灯列表。

它减少大量小光体积 Draw，也提高同 Tile 线程读取光源数据的局部性。

## Deferred 的限制

- GBuffer 带宽和内存大；
- 多材质模型需要编码分类或额外数据；
- 透明通常仍走 Forward；
- MSAA 成本和 Resolve 更复杂；
- 移动端分块式 GPU 可能不适合把大 GBuffer 写回外部内存；
- 每像素只保留最前表面，不适合多层材质。

### 移动端的特殊路径

最后两条在移动端需要单独展开。TBDR 架构把渲染分块进行，满足附件预算与驱动合并条件时，Tile 的中间结果可以驻留在片上内存；溢出、执行范围拆分或其他依赖可能触发提前存储与重新加载。

朴素的延迟渲染在这里代价极高：GBuffer 写回主存、光照 Pass 再从主存读回，一来一回的带宽可能成为移动端瓶颈。

解法是把 Geometry 与光照合并进同一个 Render Pass，为 GBuffer 留在片上创造条件，实际驻留由附件预算、设备与驱动决定。Vulkan 的 Subpass 与 Metal 的 Programmable Blending 提供了这个能力，引擎侧对应的是各类“移动端延迟渲染”路径。

片上路径受附件容量和通道合并约束。GBuffer 写入与光照读取需要处于兼容的 API 执行范围，采样完整画面可能使数据写回主存。传统 input attachment 读取当前片元位置，不提供普通纹理的任意邻域采样。

这解释了为什么移动端延迟路径的 GBuffer 布局通常比桌面端精简得多，也解释了为什么某些屏幕空间效果在移动端延迟路径下不可用。

### 自定义着色模型的接入难度

延迟路径下，材质只负责把数据写进 GBuffer，光照由统一的光照 Pass 计算。想要一种新的着色方式，就必须让光照 Pass 知道如何处理它。

两条路：在 GBuffer 中编码材质分类 ID，让光照 Pass 分支到不同着色函数；或者扩展 GBuffer 携带额外参数。前者受限于分类位宽，后者增加带宽。

这是延迟路径与前向路径在扩展性上的本质差异：前向路径下每个材质自带完整光照代码，加一种着色方式只需写一个新着色器；要纳入统一的延迟光照，需要让光照阶段识别相应材质参数与 BRDF，可通过引擎扩展接口或源码实现。特殊材质也可选择单独的前向通道，并承担额外绘制成本。

Unity URP 通过 `LightMode` 选择 GBuffer 材质通道。片元阶段编码材质属性及相应照明数据，再写入配置要求的附件。准确目标数量、格式与相机颜色关系需核对目标 URP 包、渲染层和阴影设置。想插入自定义着色，要么在写入前修改这批数据，要么改动管线的解包与光照代码。

## 成本与方案选择

大量小灯、复杂不透明材质时可能占优。灯很少、分辨率高、带宽有限或透明很多时，Forward/Forward+ 可能更合适。

比较应记录：

- Geometry 和光照 Pass GPU 时间；
- GBuffer 字节/像素；
- 平均每 Tile/Cluster 灯数；
- 光源 List 构建成本；
- 透明和后处理占比；
- 目标 GPU 的带宽和 Tile 架构。

## 验证方法

- 逐目标查看 GBuffer 与材质解码结果。
- 分别测量几何写入、灯光绘制和附件带宽。
- 在相机进入光体积时检查深度模板状态及剔除方向。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[05_光照阴影与GI/直接光照]]
- [[13_渲染架构/GBuffer布局]]
- [[13_渲染架构/渲染命令的组织方式]]
- [[14_性能分析与优化/帧瓶颈诊断]]

- [[13_渲染架构/渲染路径与光源组织]]

示例与验证范围：代码按文中前提解释机制，完整类型、资源和项目状态需由接入工程补齐。完整目标引擎运行与GPU性能为UNVERIFIED；正文给出的机制与实际实验范围分别记录。

## 参考资料

- [Khronos：Subpasses](https://docs.vulkan.org/samples/latest/samples/performance/subpasses/README.html)：延迟光照示例和片上驻留条件；正文光体积判据由球方程独立推导。
