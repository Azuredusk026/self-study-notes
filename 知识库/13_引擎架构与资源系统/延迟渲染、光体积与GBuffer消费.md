# 延迟渲染、光体积与 GBuffer 消费

延迟渲染先保存可见表面的材质属性，再执行光照。GBuffer 字节、光体积覆盖和附件读写决定其主要成本。

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

直接绘制光体积几何体有个问题：如何只对“真正位于光照范围内”的像素着色。相机在体积内外、几何体正反面都会影响判断，单靠深度测试容易漏算或重复计算。

模板缓冲提供了一个稳健的两步方案：

**第一步，标记**。绘制光体积几何体，关闭颜色输出，只在深度测试失败处翻转模板的标记位：

```text
ColorMask 0
compare = NotEqual, readMask = 对象类别掩码
zFail   = IncrementWrap, writeMask = 标记位
```

深度测试失败说明该处已有更近的几何，即场景表面位于光体积的这一部分之内。翻转操作把这些像素标记出来。读掩码同时限定只处理需要光照的对象类别，天空等被排除。

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

解法是把 Geometry 与 Lighting 合并进同一个 Render Pass，让 GBuffer 始终留在 Tile Memory 中不落主存。Vulkan 的 Subpass 与 Metal 的 Programmable Blending 提供了这个能力，引擎侧对应的是各类“移动端延迟渲染”路径。

片上路径受附件容量和通道合并约束。GBuffer 写入与光照读取需要处于兼容的 API 执行范围，采样完整画面可能使数据写回主存。传统 input attachment 读取当前片元位置，不提供普通纹理的任意邻域采样。

这解释了为什么移动端延迟路径的 GBuffer 布局通常比桌面端精简得多，也解释了为什么某些屏幕空间效果在移动端延迟路径下不可用。

### 自定义着色模型的接入难度

延迟路径下，材质只负责把数据写进 GBuffer，光照由统一的 Lighting Pass 计算。想要一种新的着色方式，就必须让 Lighting Pass 知道如何处理它。

两条路：在 GBuffer 中编码材质分类 ID，让 Lighting Pass 分支到不同着色函数；或者扩展 GBuffer 携带额外参数。前者受限于分类位宽，后者增加带宽。

这是延迟路径与前向路径在扩展性上的本质差异：前向路径下每个材质自带完整光照代码，加一种着色方式只需写一个新 Shader；延迟路径下必须改动引擎的光照阶段。

Unity URP 通过 `LightMode` 选择 GBuffer 材质通道。片元阶段编码材质属性及相应照明数据，再写入配置要求的附件。准确目标数量、格式与相机颜色关系需核对目标 URP 包、渲染层和阴影设置。想插入自定义着色，要么在写入前修改这批数据，要么改动管线的解包与光照代码。

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

- 逐目标查看 GBuffer 与材质解码结果。
- 分别测量几何写入、灯光绘制和附件带宽。
- 在相机进入光体积时检查深度模板状态及剔除方向。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[05_光照阴影与GI/光源与直接光照]]
- [[13_引擎架构与资源系统/GBuffer布局]]
- [[13_引擎架构与资源系统/Render Pass、Command Buffer与Render Graph]]
- [[14_性能分析与优化/帧时间、瓶颈与GPU成本]]

- [[13_引擎架构与资源系统/渲染路径与光源组织]]

## 参考资料

- Ola Olsson et al., *Clustered Deferred and Forward Shading*.
- Johan Andersson, *Tiled Deferred Shading*.
- Unity and Unreal documentation on Forward+, Deferred and mobile renderers.
- LearnOpenGL, `src/5.advanced_lighting/8.1.deferred_shading`.
