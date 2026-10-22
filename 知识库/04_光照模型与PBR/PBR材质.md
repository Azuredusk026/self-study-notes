# PBR材质

同一材质换了环境以后金属感消失，可能是参数语义、颜色导入或光照输入发生变化。PBR把这些参数与能量关系联系起来，让变化有明确原因。材质的反射类型决定 Base Color 和镜面参数的含义，颜色导入、遮罩打包与标定场景共同约束这些数据的使用。

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

#### 正入射反射率

对于无吸收电介质，入射介质与透射介质的折射率分别为 $\eta_i$、$\eta_t$，垂直入射时

$$
F_0=\left(\frac{\eta_t-\eta_i}{\eta_t+\eta_i}\right)^2.
$$

空气中取 $\eta_i\approx1$，若材料 $\eta_t=1.5$，则 $F_0=0.04$。这个算例解释常见默认值，但默认值不代表所有电介质；高折射率材料需要自己的参数。

金属使用包含消光系数的复折射率。光谱反射率经过光源光谱、色匹配函数和工作色域转换后才能得到 RGB；RGB 三通道并不是三个固定波长的测量值。
这条关系的实用价值在于校验：美术给的材质 $F_0$ 若明显超出已知材料的物理范围，通常是数据错误或工作流混淆，例如把高光强度当成了 $F_0$。

#### 金属

金属几乎没有普通漫反射。Base Color 用来描述有色镜面反射，$F_0$ 可以是彩色。

Metallic 通常应接近 0 或 1。中间值主要用于抗锯齿、脏污混合或复合材质边界，表达像素覆盖的有效混合，而不是一种独立的均匀材料分类。

### 漫反射与镜面反射分配

简化实时模型常写成：

$$
k_s=F,\qquad k_d=(1-k_s)(1-metallic)
$$

$F$ 是当前微面入射角的 Fresnel 反射率，$k_d$ 用它衰减漫反射。它体现反射和透入表面的竞争关系，但不是完整半球能量的精确分配。

#### 半球能量约束

固定一个入射方向 $\omega_i$，把所有出射方向的反射能量相加，必须满足

$$
E(\omega_i)=\int_{\Omega}f_r(\omega_i,\omega_o)
(\mathbf N\cdot\omega_o)d\omega_o\le1.
$$

$E$ 是方向到半球的反射率。满足互易性时，也可固定出射方向、对入射方向积分进行白炉检查。Lambert 的 $f_d=\rho/\pi$ 给出 $E=\rho$，因为余弦半球积分等于 $\pi$。

微表面模型的 $E$ 还依赖粗糙度、视角、遮蔽和多次散射，不能用某一对方向的 $F(V\cdot H)$ 替代。$(1-F)$ 因而是便于实时计算的局部分配近似；严格的层模型需要处理光透入、内部散射和再次穿出界面的能量，或根据半球积分建立补偿表。
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
- 积分后的能量由整个反射模型决定，需区分波瓣变宽与单次散射损失。

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
- 单独输出 $k_d$ 与 $F$，在微面入射角趋于掠射时检查其变化；宏观 $N\cdot V$ 不能替代 $V\cdot H$。
- 高粗糙度材质对比有无多次散射补偿的版本，整体亮度应有可察觉差异。
- 换 HDRI 环境重测：只在单一灯光下好看的材质，参数多半不可靠。
- 用资产采用的折射率或测量数据反查 $F_0$，记录入射介质、色域和近似条件。
- 检查 sRGB 标记：Base Color 走 sRGB，其余数据纹理不走，反了会整体偏亮或偏灰。

### 漫反射与镜面能量分配

下列 HLSL 调用片段使用 [[04_光照模型与PBR/BRDF与微表面模型]] 中展开的 `EvaluateDirectResponse`。输入颜色已在线性空间，方向已归一化，`incidentContribution` 包含光源强度与距离衰减，`visibility` 为 $[0,1]$ 的可见性。

```hlsl
float3 dielectricF0 = 0.04.xxx; // 本资产约定 etaIncident=1，etaTransmitted=1.5
float3 F0 = lerp(dielectricF0, baseColor, metallic);
float3 response = EvaluateDirectResponse(
    N, V, L, baseColor, metallic, roughness, F0);
float3 result = response * incidentContribution * visibility;
```

`metallic=1` 时，漫反射权重归零，Base Color 控制镜面颜色；`metallic=0` 时，Base Color 控制漫反射，镜面正入射值由电介质参数控制。函数已经乘过入射余弦。仅看最终画面很难判断重复乘法，验证时应同时保存参数值、直接光响应和白炉积分值。

本页的数值依据与 BRDF 共用 [光照模型检查](../examples/revision/test_lighting.py)。它检验所声明的单次散射模型，不代表完整材质、资产导入或目标引擎已运行。

## 相关主题

- [[04_光照模型与PBR/BRDF与微表面模型]]
- [[04_光照模型与PBR/皮肤次表面散射]]
- [[06_纹理技术/纹理采样与过滤]]
- [[07_颜色与后处理/颜色空间]]、[[07_颜色与后处理/Alpha表示]]、[[07_颜色与后处理/HDR与曝光]]
- [[15_资产与工具管线/资产构建与发布]]

示例与验证范围：代码按文中前提解释机制，完整类型、资源和项目状态需由接入工程补齐。完整目标引擎运行与GPU性能为UNVERIFIED；正文给出的机制与实际实验范围分别记录。

## 参考资料

- [Google Filament：Material system](https://google.github.io/filament/main/filament.html#materialsystem)，核对材料参数及能量损失。
- Adobe Substance 3D, *PBR Guide*.
- Epic Games, *Physically Based Materials*.
