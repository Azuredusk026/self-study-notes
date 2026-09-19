# NPR 材质与分层光照

非真实感渲染（Non-Photorealistic Rendering，NPR）不是把 PBR 简化成几档颜色。它先定义视觉规则，再让光照、材质、阴影、描边和后处理共同遵守这些规则。

## 先定义风格空间

同一套 Toon Shader 可能需要表达：

- 明暗分几层，边界是硬切还是软过渡；
- 阴影颜色是否受材质、环境和时间影响；
- 皮肤、布料、金属、头发是否使用不同层级；
- 主光、附加光、环境光和阴影如何组合；
- 角色和场景是否共享同一 Color Script；
- 描边、Bloom、Fog 和 Tone Mapping 是否改变色块。

这些规则应成为美术可调参数和资产规范。只给每个材质自由调 Ramp，最终会产生互不一致的角色和场景。

## 从 NdotL 到明暗坐标

Lambert 漫反射使用：

$$
x=\operatorname{saturate}(\mathbf{N}\cdot\mathbf{L})
$$

Toon Shader 可以对 $x$ 做硬阈值：$w=\operatorname{step}(t,x)$，再用 $w$ 在暗色和亮色间插值。

硬 `step` 在低分辨率、法线变化和动画中容易闪烁。常用 `smoothstep(t-w,t+w,x)` 保留窄过渡带，过渡宽度还可结合 `fwidth(x)` 做屏幕空间抗锯齿。

明暗坐标也不一定直接使用 $N\cdot L$。可先加入：

- Shadow Attenuation；
- AO 或材质 Mask；
- Light Wrap；
- Artist-authored Threshold Offset；
- 角色局部空间方向修正。

运算顺序会改变含义。把实时阴影乘进 $N\cdot L$ 后再 Ramp，与先 Ramp 再乘阴影不是同一个结果。

## Ramp Texture

Ramp 用明暗坐标采样一维或二维 LUT。与写死 `step` 相比，它能直接控制层数、颜色和过渡宽度。

常见布局：

- U 表示明暗坐标；
- V 表示材质区域、时间段或风格 Variant；
- 不同角色共享 Ramp Atlas 的行；
- Base Map/ID Map 决定采用哪一行。

导入时要注意：

- 作为颜色 Ramp 时确认 sRGB 语义；
- 禁止无意的 Wrap；
- 小 LUT 的 Bilinear 与 Mipmap 可能污染相邻行；
- 阶梯边界需要 Point/Linear 与抗锯齿策略配合；
- 压缩会在硬边产生色块和泄漏。

## 分层颜色

一种常见结构是把 Base Color 拆为亮部、一级阴影和二级阴影：

$$
C=w_0C_{light}+w_1C_{shadow1}+w_2C_{shadow2}
$$

$w_i$ 由 Ramp、Shadow Map、AO 和区域 Mask 决定，且和为 1。

阴影色不应简单乘黑。可使用暖冷偏移、固定色板或感知颜色空间调整，但最终要在项目输出 Color Space 与 Tone Mapping 后检查。

多层边界应有明确优先级。例如实时 Shadow Map 应当能把亮部压入阴影层，但 AO 不应把整个材质无限变暗。

## 材质 ID 与区域控制

角色常用 ID Map 或通道打包区分皮肤、布料、金属、装饰和发光区域。每类区域可选择：

- Ramp 行与阈值；
- Specular 形状与颜色；
- Rim Light；
- Shadow Tint；
- Outline 宽度；
- SSS/MatCap/Emission 等附加项。

ID 边界会经过纹理过滤。若希望离散分类，应使用合适的通道值、Padding 和阈值，避免 Mipmap 后类别混合。

## 风格化高光

连续 PBR 高光常与大色块冲突。可以保留 $N\cdot H$ 或微表面 NDF 作为形状基础，再对结果做阈值或 Ramp：

$$
s=\operatorname{smoothstep}(t-w,t+w,f(\mathbf{N},\mathbf{L},\mathbf{V},r))
$$

$r$ 是 Roughness 或美术控制量。金属可用更硬、更有色的高光；皮肤和布料使用更柔和、受 Mask 控制的层。

并非所有 NPR 都要删除 Fresnel。Fresnel 是否保留取决于视觉目标。若保留，应控制它不会在暗部制造无法管理的亮边；若移除，也要用 Rim/Specular 规则补回轮廓可读性。

## 皮肤 Ramp 与 SSS 近似

皮肤可在明暗交界加入一条偏暖的窄色带，近似次表面散射的视觉结果。这不是物理 SSS，只是风格化层。

可以使用 Thickness/Curvature/区域 Mask 控制耳朵、鼻翼和面颊强度。若只依赖 $N\cdot L$，所有物体都会出现相同暖边，看起来像统一描边而不是皮肤。

## MatCap 与视角空间细节

MatCap 用 View Space Normal 映射二维材质球，适合提供固定高光、金属或手绘反射。它不随世界光源正确变化，因此更像艺术层。

可把 MatCap 与光照权重、Mask 和 Fresnel 混合，避免角色转动时图案完全粘在屏幕上。相机 FOV 与 View Space 约定改变时也要检查。

## 多光源

把每盏光分别 Ramp 后相加，会快速把画面推白，也会产生多组互相冲突的硬边。常见控制方式：

- 只有主方向光决定大明暗；
- 附加光只贡献受限的 Specular/Rim；
- 按亮度选主光，但对切换做平滑；
- 把局部光汇总成连续补光，再由统一曲线限制；
- 对关键角色使用 Lighting Channel 或专用 Light Rig。

这属于风格设计，不是物理正确性问题，但规则必须稳定且可解释。

## 与 PBR 的结合路线

传统赛璐璐渲染的局限在于材质表达力：减少色阶带来了卡通感，也同时抹掉了区分金属、布料、皮革的信息。业界由此发展出几条与 PBR 结合的路线。

**降色阶化**。以完整 PBR 光照为底，在输出端减少色阶。保留了 PBR 的材质区分能力，但压缩后金属感往往变弱，整体偏厚重，更适合美漫风而非日漫风。

**写实手办风**。基本保持 PBR 光照，只对漫反射项做局部变形（例如提升暗部饱和度），卡通感主要来自建模造型与材质参数的风格化，而非光照模型。

**分区并存**。角色主体用传统 Toon 材质，金属、宝石、皮革等需要质感的部件走 PBR 或混合模型。这是实践中最常见的选择，因为它把"要色块"和"要质感"的区域分开处理，不必在一套模型里妥协。

选择依据是画面目标而非技术先进性。是否使用 IBL、保留哪些 BRDF 项、在哪个环节降色阶，都应当先由美术目标确定。

## 参数放在光源还是材质

这是工程设计上一个容易被忽略却影响深远的决策：一个风格化参数，应该存在 GBuffer 里（属于物体），还是存在光源上（属于光照）？

以明暗过渡的软硬度为例：

```hlsl
float level   = 0.5 - toonLightOffset;
float toonNoL = smoothstep(level - smoothness * 0.5,
                           level + smoothness * 0.5, ndotl);
```

如果 `smoothness` 来自 GBuffer，那么同一个物体被任何光源照射时软硬度都一致——无法做到"一盏很硬的背光加一盏很软的补光"这种美术常用的打光手法。

反过来，高光的软硬度更适合放在物体上，因为它直接表达材质属性，不同部位需要不同取值。

一个实践中的划分是：**漫反射的过渡软硬度放在光源，高光的软硬度放在物体**。这种不对称初看割裂，但它对应了真实的需求差异——前者是打光意图，后者是材质属性。

这个判断可以推广：参数的归属取决于它表达的是"光怎么打"还是"物体是什么"。归错位置的后果不是效果错误，而是美术需要的某类表达根本无法实现。

## 二值化的固有问题

对光照做硬二值化时，明暗交界线常出现锯齿状的不规则边缘。原因有两层：

其一，模型本质是多边形，法线在三角形内插值，有限面数无法表现连续曲面，阈值恰好落在插值区间时边界就会沿着三角形边呈锯齿状。

其二，更根本的是——画师绘制光照时按画面好看来画，很多理想的明暗分布与三维结构本就不对应。这不是精度问题，无法靠提高面数解决。

主流应对是修改法线：调整法线朝向、用简模法线替换高模法线，让明暗边界服从美术意图而非几何结构。这是资产侧的工作，引擎传入 GBuffer 的法线不需改动。

引擎侧也可以提供运行时的法线调整手段，代价是可控性不如离线编辑，且难以处理复杂造型。两者通常并存：主要角色走离线法线编辑，次要角色用运行时近似。
## 阴影与环境光

Shadow Map 的结果是可见性，不应直接等同于最终阴影颜色。可以用 Visibility 在亮/暗层之间选择，再由 Ramp 和材质定义颜色。

环境光、Light Probe 或 IBL 能防止暗部完全扁平。NPR 通常对其做压缩或色板映射，保留体积同时不破坏色块。

场景 Fog、Exposure 和 Tone Mapping 会改变层级对比。调材质时必须经过最终后处理链，而不是只看未 Tone Map 的中间 Buffer。

## 风格一致性与质量档

建议把以下参数放入共享 Profile，而不是散落在材质实例：

- Ramp/Color Palette；
- 主光方向与 Shadow Tint；
- 全局阈值、过渡宽度；
- Rim/Specular 上限；
- Outline 与距离缩放；
- Fog、Exposure 和 Tone Mapping 配置。

低质量档可减少附加光、MatCap 层、额外 Mask 和屏幕空间效果，但应尽量保持同一色板与层级关系。

## 验证方法

- 输出原始 $N\cdot L$、Ramp UV、Layer Weight、Shadow Visibility 和 Material ID 调试视图。
- 用固定灯光旋转角色，检查边界连续性和法线接缝。
- 在不同 FOV、距离、HDR 曝光和 Tone Mapping 下比较色块。
- 检查主光切换、多光源重叠、Light Probe 和实时阴影组合。
- 用灰球、标准角色和场景资产共享一套 Profile 做风格回归。

### Ramp 分层采样

输入法线和光方向处于同一空间。`halfLambert` 把 $N\cdot L$ 映射到 $[0,1]$，材质行选择一条 Ramp：

```hlsl
float ndotl = dot(normalize(normalWS), normalize(lightDirWS));
float halfLambert = ndotl * 0.5 + 0.5;
float2 rampUv = float2(saturate(halfLambert), materialRowUv);
float3 ramp = LightRamp.SampleLevel(PointClamp, rampUv, 0).rgb;
float shadow = lerp(shadowTint, 1.0.xxx, visibility);
float3 litColor = baseColor * ramp * shadow;
```

Point 采样适合保留硬分层，Linear 采样适合平滑过渡；两者都要关闭不期望的 Mip 混合或准备专用 Ramp Mip。把场景阴影直接乘黑会丢掉阴影层的艺术控制，示例用 `shadowTint` 保留色相。验证时分别显示 `halfLambert`、Ramp 和 Visibility，避免把法线、Ramp 与 Shadow Map 问题混在一起。

## 相关主题

- [[04_光照模型与PBR/经典光照、BRDF与微表面模型]]
- [[05_光照阴影与GI/阴影贴图、PCF与PCSS]]
- [[11_NPR与风格化渲染/角色面部、头发与阴影]]
- [[11_NPR与风格化渲染/描边、Billboard与场景风格化]]
- [[13_引擎架构与资源系统/Unreal网格绘制与自定义Pass]]

## 参考资料

- Gooch et al., *A Non-Photorealistic Lighting Model for Automatic Technical Illustration*.
- Unity and Unreal Engine documentation on custom lighting and material functions.
- Arc System Works and miHoYo technical presentations on stylized character rendering.
