# PBR材质

同一材质换了环境以后金属感消失，可能是参数语义、颜色导入或光照输入发生变化。PBR把这些参数与能量关系联系起来，让变化有明确原因。我们从非金属和金属的响应开始，再检查粗糙度、遮罩与纹理，最后用固定曝光的标定场景验证。

## 反射语义

### Metalness/Roughness 工作流

常见输入：

- Base Color；
- Metallic；
- Roughness 或 Smoothness；
- Normal；
- Ambient Occlusion；
- Emissive；
- 其他项目 Mask。

同名贴图在不同引擎中可能有不同通道和反向约定。资产规范必须记录语义，而不只是命名和打包方式。

### Dielectric 和 Metal

#### 非金属

Base Color 主要描述漫反射颜色。正视角镜面反射率 $F_0$ 通常较低，常见实时模型把默认值设在约 0.04 附近，但真实材料会变化。

剩余能量进入表面并形成漫反射或更复杂的次表面传输。

#### F0 从哪里来

$F_0$ 不是任意调出来的参数，它由折射率决定。非金属用标量折射率 $n$：

$$
F_0=\left(\frac{n-1}{n+1}\right)^2
$$

常见材料的对应关系：水 $n\approx1.33$ 得 $F_0\approx0.02$，玻璃 $n\approx1.5$ 得 $0.04$，皮肤 $n\approx1.4$ 得 $0.028$，多数电介质落在 0.02 到 0.06 之间。这就是“默认 0.04”的来历——它是玻璃与常见塑料附近的取值。

金属的折射率是复数，虚部为消光系数，$F_0$ 因此带颜色，且需要按 RGB 三个波长分别查表。铜的偏红、金的偏黄都来自各自的测量值。

这条关系的实用价值在于校验：美术给的材质 $F_0$ 若明显超出已知材料的物理范围，通常是数据错误或工作流混淆，例如把高光强度当成了 $F_0$。

#### 金属

金属几乎没有普通漫反射。Base Color 用来描述有色镜面反射，$F_0$ 可以是彩色。

Metallic 通常应接近 0 或 1。中间值主要用于抗锯齿、脏污混合或复合材质边界，不表示一种自然的“半金属原子”。

### 漫反射和镜面反射如何分配

简化实时模型常写成：

$$
k_s=F,\qquad k_d=(1-k_s)(1-metallic)
$$

$k_s$ 是镜面部分，$k_d$ 是漫反射部分。Fresnel 增强时，漫反射相应减少，避免两部分相加超过入射能量。

#### 能量守恒从哪来

这个分配公式的依据是半球积分。表面反射的总能量不能超出入射能量，写出来是：

$$
\int_{\Omega} f_r(\omega_i,\omega_o)\,(\mathbf{n}\cdot\omega_i)\,d\omega_i\leq 1
$$

对每个出射方向 $\omega_o$ 都要成立。镜面反射率先从半球中拿走份额 $F$，剩下的 $1-F$ 才轮到漫反射——这就是 $k_d$ 里那个 $(1-k_s)$ 的来源，不是调出来的经验系数。

严格地说，微表面模型还存在多次散射能量损失：粗糙表面上光在微面之间多次反弹，单次散射近似会丢掉这部分能量，表现为高粗糙度材质整体偏暗。主流引擎用补偿项（Kulla-Conty 一类）把损失的能量加回去。如果自己的实现里粗糙材质比参考渲染明显偏暗，先查这一项。

## 纹理参数

### Base Color 的边界

Base Color 不应包含：

- 烘焙高光；
- 固定方向的阴影；
- 环境 AO 造成的大面积黑边；
- Tone Mapping 后的画面颜色。

否则材质换到新灯光下会重复计算这些效果。

Base Color 是颜色纹理，通常按 sRGB 读取并在线性空间参与光照。Metallic、Roughness、AO 和 Mask 是数据，不应做 sRGB 解码。

### Roughness

Roughness 描述微表面法线分布的宽度，不是“高光强度”。

- 低 Roughness：高光集中，反射清晰；
- 高 Roughness：高光展开，反射模糊；
- 总反射能量不应仅因高光变宽就凭空消失。

把 Roughness 调高后画面变暗，可能来自 NDF、几何项、IBL 预过滤、单次散射能量损失或曝光，而不是 Roughness 本来就代表更少反射。

### Ambient Occlusion

AO 近似局部几何对环境光的遮挡。它通常不应直接乘到所有直接光上。

常见做法：

- 影响间接漫反射；
- 使用 Specular Occlusion 近似间接镜面遮挡；
- 与屏幕空间或烘焙 AO 组合时避免重复变黑。

AO 是几何可见性近似，不是材质脏污颜色。

### Emissive

Emissive 表示表面自己发出的 Radiance。它是否真正照亮其他物体，取决于 GI 系统。只把像素写得很亮，通常只会影响自身颜色和 Bloom。

HDR Emissive 应在线性空间保存和计算。最终画面亮度还会受曝光和 Tone Mapping 影响。

### 贴图通道打包

把 AO、Roughness、Metallic 打进一张 ORM 纹理可以减少资源绑定和采样次数，但需要权衡：

- 三个通道是否需要相同分辨率；
- 是否一起使用 Mipmap；
- 压缩格式对各通道的误差；
- 资产更新时是否产生无关通道重打包；
- Alpha 通道会不会改变压缩格式大小。

打包是工程策略，不是 PBR 的定义。

## 资产与标定

### PBR 资产检查

#### 语义

- Base Color 是否去除了光照和高光？
- Metallic 是否符合材质类型？
- Roughness 是否使用正确正反方向？
- Normal 使用 DirectX 还是 OpenGL Y 方向？

#### 导入

- 颜色纹理和数据纹理的 sRGB 标记；
- Normal Map 导入类型；
- 压缩格式；
- Mipmap 和 Streaming；
- 通道打包和平台 Override。

#### 范围

不要只用统一 Min/Max 暴力裁剪所有资产。合理范围与材质类型、扫描来源和项目美术风格有关。验证工具最好先报告异常，再允许有依据的例外。

### 材质标定场景

一个稳定的材质检查场景应包含：

- 中性灰背景；
- 已知强度和色温的主光；
- 可控 HDRI；
- 灰球、镜面球和 Roughness/Metallic 阶梯；
- 固定曝光；
- 与目标平台一致的 Tone Mapping。

材质只在一个电影式灯光里好看，不代表参数正确。

## 验证方法

- 用灰球与镜面球对比参考实现，球面是最敏感的材质标定工具。
- 把 Metallic 在 0 与 1 之间扫一遍，中间值区域不应出现大面积异常发亮或发暗。
- 单独输出 $k_d$ 与 $k_s$，确认掠射角处漫反射趋近于零。
- 高粗糙度材质对比有无多次散射补偿的版本，整体亮度应有可察觉差异。
- 换 HDRI 环境重测：只在单一灯光下好看的材质，参数多半不可靠。
- 用折射率反查 $F_0$，超出 0.02 到 0.06 范围的非金属材质要给出依据。
- 检查 sRGB 标记：Base Color 走 sRGB，其余数据纹理不走，反了会整体偏亮或偏灰。

### 漫反射与镜面能量分配

输入颜色已经从 sRGB 解码到线性空间，`metallic` 和 `roughness` 位于 $[0,1]$。下面只展示能量分配，实际 BRDF 还需要 NDF、Geometry 和光照积分：

```hlsl
float3 F0 = lerp(0.04.xxx, baseColor, metallic);
float3 F = FresnelSchlick(saturate(dot(H, V)), F0);
float3 kSpecular = F;
float3 kDiffuse = (1.0 - kSpecular) * (1.0 - metallic);
float3 diffuse = kDiffuse * baseColor / PI;
float3 specular = EvaluateMicrofacetSpecular(N, V, L, F0, roughness);
float3 result = (diffuse + specular) * radiance * saturate(dot(N, L));
```

金属把 Base Color 用作 $F_0$，漫反射权重收敛到零；电介质保留漫反射，并由 Fresnel 把掠射角能量移向镜面。把 `kDiffuse` 固定为 1 会重复计算镜面反射已经占用的能量，常表现为材质整体过亮。

## 相关主题

- [[04_光照模型与PBR/BRDF与微表面模型]]
- [[04_光照模型与PBR/皮肤次表面散射]]
- [[06_纹理技术/纹理采样与过滤]]
- [[07_颜色与后处理/颜色空间]]、[[07_颜色与后处理/Alpha表示]]、[[07_颜色与后处理/HDR与曝光]]
- [[15_资产与工具管线/资产构建与发布]]

示例与验证范围：代码按文中前提解释机制，完整类型、资源和项目状态需由接入工程补齐。完整目标引擎运行与GPU性能为UNVERIFIED；正文给出的机制与实际实验范围分别记录。

## 参考资料

- Google Filament, *Material System* and *Physically Based Rendering in Filament*.
- Adobe Substance 3D, *PBR Guide*.
- Epic Games, *Physically Based Materials*.
