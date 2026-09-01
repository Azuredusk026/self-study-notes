# PBR 材质与能量守恒

PBR 不是一种固定 Shader。它是一组约定：材质参数有稳定语义，光照尽量遵守能量关系，材质在不同光照环境下仍保持可预测。

## Metalness/Roughness 工作流

常见输入：

- Base Color；
- Metallic；
- Roughness 或 Smoothness；
- Normal；
- Ambient Occlusion；
- Emissive；
- 其他项目 Mask。

同名贴图在不同引擎中可能有不同通道和反向约定。资产规范必须记录语义，而不只是命名和打包方式。

## Dielectric 和 Metal

### 非金属

Base Color 主要描述漫反射颜色。正视角镜面反射率 $F_0$ 通常较低，常见实时模型把默认值设在约 0.04 附近，但真实材料会变化。

剩余能量进入表面并形成漫反射或更复杂的次表面传输。

### 金属

金属几乎没有普通漫反射。Base Color 用来描述有色镜面反射，$F_0$ 可以是彩色。

Metallic 通常应接近 0 或 1。中间值主要用于抗锯齿、脏污混合或复合材质边界，不表示一种自然的“半金属原子”。

## 漫反射和镜面反射如何分配

简化实时模型常写成：

$$
k_s=F,\qquad k_d=(1-k_s)(1-metallic)
$$

$k_s$ 是镜面部分，$k_d$ 是漫反射部分。Fresnel 增强时，漫反射相应减少，避免两部分相加超过入射能量。

## Base Color 的边界

Base Color 不应包含：

- 烘焙高光；
- 固定方向的阴影；
- 环境 AO 造成的大面积黑边；
- Tone Mapping 后的画面颜色。

否则材质换到新灯光下会重复计算这些效果。

Base Color 是颜色纹理，通常按 sRGB 读取并在线性空间参与光照。Metallic、Roughness、AO 和 Mask 是数据，不应做 sRGB 解码。

## Roughness

Roughness 描述微表面法线分布的宽度，不是“高光强度”。

- 低 Roughness：高光集中，反射清晰；
- 高 Roughness：高光展开，反射模糊；
- 总反射能量不应仅因高光变宽就凭空消失。

把 Roughness 调高后画面变暗，可能来自 NDF、几何项、IBL 预过滤、单次散射能量损失或曝光，而不是 Roughness 本来就代表更少反射。

## Ambient Occlusion

AO 近似局部几何对环境光的遮挡。它通常不应直接乘到所有直接光上。

常见做法：

- 影响间接漫反射；
- 使用 Specular Occlusion 近似间接镜面遮挡；
- 与屏幕空间或烘焙 AO 组合时避免重复变黑。

AO 是几何可见性近似，不是材质脏污颜色。

## Emissive

Emissive 表示表面自己发出的 Radiance。它是否真正照亮其他物体，取决于 GI 系统。只把像素写得很亮，通常只会影响自身颜色和 Bloom。

HDR Emissive 应在线性空间保存和计算。最终画面亮度还会受曝光和 Tone Mapping 影响。

## 贴图通道打包

把 AO、Roughness、Metallic 打进一张 ORM 纹理可以减少资源绑定和采样次数，但需要权衡：

- 三个通道是否需要相同分辨率；
- 是否一起使用 Mipmap；
- 压缩格式对各通道的误差；
- 资产更新时是否产生无关通道重打包；
- Alpha 通道会不会改变压缩格式大小。

打包是工程策略，不是 PBR 的定义。

## PBR 资产检查

### 语义

- Base Color 是否去除了光照和高光？
- Metallic 是否符合材质类型？
- Roughness 是否使用正确正反方向？
- Normal 使用 DirectX 还是 OpenGL Y 方向？

### 导入

- 颜色纹理和数据纹理的 sRGB 标记；
- Normal Map 导入类型；
- 压缩格式；
- Mipmap 和 Streaming；
- 通道打包和平台 Override。

### 范围

不要只用统一 Min/Max 暴力裁剪所有资产。合理范围与材质类型、扫描来源和项目美术风格有关。验证工具最好先报告异常，再允许有依据的例外。

## 材质标定场景

一个稳定的材质检查场景应包含：

- 中性灰背景；
- 已知强度和色温的主光；
- 可控 HDRI；
- 灰球、镜面球和 Roughness/Metallic 阶梯；
- 固定曝光；
- 与目标平台一致的 Tone Mapping。

材质只在一个电影式灯光里好看，不代表参数正确。

## 相关主题

- [[04_光照模型与PBR/经典光照、BRDF与微表面模型]]
- [[06_纹理技术/纹理采样、过滤、Mipmap与压缩]]
- [[07_颜色与后处理/颜色空间、Alpha、HDR与曝光]]
- [[15_资产与工具管线/资产导入、验证与发布]]

## 参考资料

- Google Filament, *Material System* and *Physically Based Rendering in Filament*.
- Adobe Substance 3D, *PBR Guide*.
- Epic Games, *Physically Based Materials*.
