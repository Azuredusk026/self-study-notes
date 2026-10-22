# IBL

镜面能直接看见环境图，粗糙表面却同时接收许多方向。IBL把昂贵方向积分的一部分预先保存，再让运行时根据法线、视线和粗糙度查询。预过滤图与BRDF LUT必须来自相同约定，才能保持亮度和粗糙度响应。

## Image-Based Lighting

IBL 使用环境图表示各方向入射光。材质需要计算：

- Diffuse Irradiance；
- Specular Reflection。

直接每像素对整个环境半球积分太贵，所以通常预计算。

## Diffuse Irradiance

Lambert 漫反射对环境光做余弦加权半球积分。结果变化平滑，可以：

- 卷积到低分辨率 Irradiance Cubemap；
- 用低阶 SH 保存；
- 在 Probe 中保存并插值。

若保存的是辐照度 $E(N)=\int L_i(L)\max(N\cdot L,0)d\omega_L$，运行时 Lambert 结果为 $\rho E/\pi$；若烘焙端已除以 $\pi$，运行时只乘 $\rho$。常量环境 $L_i=C$ 应得到 $E=\pi C$、漫反射结果 $\rho C$，这个算例可以识别重复或遗漏的 $\pi$。

这里保存的是低频光照，不适合镜面反射。

## Specular Prefilter

镜面反射依赖视线、法线和 Roughness。常见 Split-sum Approximation 把环境项和 BRDF 项近似拆开：

1. 对 Environment Cubemap 按不同 Roughness 预过滤；
2. 把 Roughness 映射到不同 Mip；
3. 预计算 BRDF LUT，输入通常是 $N\cdot V$ 和 Roughness；
4. 运行时组合 Prefiltered Environment、$F_0$ 和 LUT。

Roughness 高时使用更模糊的 Mip。这不是普通图片缩小，而是按微表面分布对入射方向做积分近似。

预过滤时按 GGX 分布采样半向量，再把样本方向转换为入射方向。样本的概率密度函数决定一个样本代表的立体角；环境图纹素也有自己的立体角。用两者比值选择源 Cubemap 的 Mip，可以减少高亮环境在粗糙表面上的闪烁。

常见伪影及原因：

- Roughness 接近 0 时样本锥很窄，样本数不足会漏掉高亮点；
- Cubemap 面边界没有无缝采样或跨面 Mip，会出现接缝；
- 直接用 `roughness * mipCount`，却没有匹配烘焙器的分布和 Mip 数，会让模糊速度错误；
- LUT 烘焙参数位于纹素中心，却在运行时按端点格点解释，会产生半纹素偏移；地址映射必须与烘焙约定相同；
- 低分辨率预过滤图会让强小光源在相邻 Mip 间突然消失。

### 半向量采样与积分权重

取法线 $N=(0,0,1)$，两维均匀样本为 $u_1,u_2$，以 $\alpha=\max(roughness^2,0.002)$ 表示 GGX 宽度，与 BRDF 篇的有限波瓣下限一致。按 NDF 采样半向量时

$$
\phi=2\pi u_2,\quad
\cos\theta_H=\sqrt{\frac{1-u_1}{1+(\alpha^2-1)u_1}},\quad
p_H(H)=D(H)(N\cdot H).
$$

由 $L=2(V\cdot H)H-V$ 得到光线方向。反射变换的雅可比给出 $p_L(L)=p_H(H)/(4|V\cdot H|)$。在 $V\cdot H\le0$ 或 $N\cdot L\le0$ 时，该样本对上半球积分贡献为零，仍计入总样本数。若只除以有效样本数，会把估计量人为抬高。

预过滤环境常进一步取 $N=V=R$，按粗糙度采样后累加 $L_i(L)(N\cdot L)$，再除以余弦权重总和。归一化使常量环境保持常量；这个加权平均是分离近似的一部分，并不是任意视角的完整 BRDF 积分。

### BRDF 积分表

把 Schlick 写成 $F=F_0(1-F_c)+F_c$，其中 $F_c=(1-V\cdot H)^5$。代入 Monte Carlo 权重后，$D$ 与半向量密度中的 $D$ 抵消，得到

$$
g=\frac{G(L,V)(V\cdot H)}{(N\cdot V)(N\cdot H)},\qquad
A=\frac1M\sum (1-F_c)g,\quad B=\frac1M\sum F_cg.
$$

运行时使用 $F_0A+B$。完整 CPU 循环见 [lighting_models.py 的 integrate_lut](../examples/revision/lighting_models.py)，采用与 BRDF 篇相同的可分离 Smith 项、Hammersley 样本和拒绝规则。LUT 端点采用纹素中心处的参数，$N\cdot V$ 与 $\alpha$ 均保持正值，避免退化除法。

样本代表的立体角约为 $\Omega_s=1/(M p_L)$。边长为 $W$ 的 Cubemap 每纹素平均立体角约为 $\Omega_t=4\pi/(6W^2)$，因此源图级别可取 $lod=\tfrac12\log_2(\Omega_s/\Omega_t)$ 并限制到有效范围。每升一级，纹素面积约变为四倍，这是二分之一系数的来源。各面实际立体角不均匀，该公式使用平均值，工程还可加入经过测量的过滤偏置。

BRDF LUT 保存上述两个系数，输入限定在 $[0,1]^2$。它依赖固定的 NDF、Geometry 项和采样约定，更换 BRDF 后需要重新积分，不能把任意 LUT 与任意材质模型混用。

## Split-sum 的限制

- 假设环境在 BRDF 积分中可以按近似方式分离；
- 对高频环境、粗糙表面和复杂可见性会有误差；
- 普通 Probe 不知道局部遮挡和精确视差；
- Box Projection 只能近似修正室内反射位置；
- Specular Occlusion 仍需额外估计。

## Probe 和 Reflection Capture

Reflection Probe 保存某个位置周围的环境。物体远离 Probe 中心后，简单按反射方向采样会产生“反射贴在无限远”的感觉。

常见处理：

- 多 Probe 混合；
- Box Projection/Parallax Correction；
- 屏幕空间反射补局部细节；
- 光追反射处理动态和离屏信息。

## Split-sum求值

HLSL机制片段中，N、V与环境方向同在世界空间，粗糙度到mip的映射与烘焙端一致。颜色使用线性HDR。

```hlsl
float3 R = reflect(-V, N);
float3 environment = Prefiltered.SampleLevel(LinearClamp, R, roughness * maxMip).rgb;
float2 parameter = float2(saturate(dot(N,V)), roughness);
// 本片段的 LUT 在每个纹素中心按 parameter=(index+0.5)/size 烘焙。
float2 lutUV = clamp(parameter, 0.5 / lutSize, 1.0 - 0.5 / lutSize);
float2 terms = BrdfLut.SampleLevel(LinearClamp, lutUV, 0).rg;
float3 specular = environment * (F0 * terms.x + terms.y);
```

`lutSize` 是 LUT 的二维纹素数，`maxMip=mipCount-1`。本片段的每个环境 mip 对应均匀分布的感知粗糙度；使用其他烘焙分布时应换成对应映射。资源为线性 HDR Cubemap 与双通道线性 LUT，可见性未包含，漫反射另从辐照度求值。Split-sum是分离近似，高频环境和局部遮挡仍有误差。

## 验证方法

白色常量环境检查能量，粗糙度阶梯检查mip映射与LUT响应，镜面球核对环境方向。位置离开捕获中心时检查视差误差，与同位置参考积分对照。

[数值检查](../examples/revision/test_lighting.py) 将 LUT 的 `A+B` 与独立半球积分和解析值 `1-ln(2)` 对照，检查采样概率、余弦和无效样本分母。实际环境贴图预过滤、GPU 纹理采样和画面误差尚未测量。

## 相关主题

- [[04_光照模型与PBR/BRDF与微表面模型]]
- [[05_光照阴影与GI/Reflection Probe]]
- [[04_光照模型与PBR/法线贴图]]
- [[04_光照模型与PBR/Cubemap环境采样]]

## 参考资料

- [Filament：Image based lights 与 Importance sampling for the IBL](https://google.github.io/filament/main/filament.html#annex/importancesamplingfortheibl)，核对分离近似、NDF 密度与源 mip 的立体角关系。
- Brian Karis, [Real Shading in Unreal Engine 4](https://blog.selfshadow.com/publications/s2013-shading-course/karis/s2013_pbs_epic_notes_v2.pdf)，环境项与 BRDF 项分离的原始说明。
