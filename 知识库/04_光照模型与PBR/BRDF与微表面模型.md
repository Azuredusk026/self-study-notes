# BRDF与微表面模型

一个粗糙度参数改变了高光宽度，也可能改变总反射能量。要解释这个结果，先看入射光、表面分布、Fresnel与几何遮蔽怎样组成BRDF。模型各项单独可视化以后，才能判断异常来自参数映射、能量分配还是光源单位。

## 反射积分

### 辐射量与单位

- Radiant Flux：单位时间传输的总辐射能量，单位 W。
- Irradiance：单位面积接收到的通量，单位 W/m²；它已经对入射方向积分。
- Radiance：沿某方向、单位投影面积、单位立体角传输的通量，单位 W/(m²·sr)。渲染方程主要用它。

在工程中经常统称“光强”或“亮度”，但推导和单位换算时不能混用。

### Rendering Equation

表面点沿方向 $\omega_o$ 的出射 Radiance：

$$
L_o(x,\omega_o)=L_e(x,\omega_o)+
\int_{\Omega}f_r(x,\omega_i,\omega_o)
L_i(x,\omega_i)(\mathbf n\cdot\omega_i)\,d\omega_i
$$

- $L_e$：自发光；
- $L_i$：入射 Radiance；
- $f_r$：BRDF；
- $\mathbf n\cdot\omega_i$：入射方向对表面投影面积的影响；
- $\Omega$：表面法线上方半球。

实时渲染很少直接求完整积分。点光源、方向光等离散光源把部分积分变成少量求和；IBL、Lightmap、Probe 和光追则用不同方式近似剩余部分。

## 表面反射模型

### Lambert Diffuse

理想漫反射向所有出射方向分布相同。BRDF 为：

$$
f_d=\frac{\rho}{\pi}
$$

$\rho$ 是表面反照率。$1/\pi$ 用来满足能量守恒：对半球积分后，总反射能量不会超过入射能量。

实时 Shader 中常看到 `albedo * saturate(dot(N,L))`，省略的 $1/\pi$ 可能被光源单位、引擎约定或美术标定吸收。不能看到代码少了 $1/\pi$ 就直接判断错误，要先确认整套光照单位。

### Phong 和 Blinn-Phong

Phong 使用反射方向 $\mathbf R$ 与视线 $\mathbf V$：

$$
I_s\propto\max(0,\mathbf R\cdot\mathbf V)^p
$$

Blinn-Phong 使用半角向量：

$$
\mathbf H=\frac{\mathbf L+\mathbf V}{\lVert\mathbf L+\mathbf V\rVert},
\qquad I_s\propto\max(0,\mathbf N\cdot\mathbf H)^p
$$

指数 $p$ 越大，高光越集中。它们便宜直观，但参数不直接对应稳定的物理材质，能量也需要额外归一化。

## 物理约束

### BRDF 的约束

一个物理上合理的 BRDF 通常关心：

#### 非负

反射不能凭空产生负能量。

#### 能量守恒

所有方向反射出去的能量不能超过收到的能量。

#### Helmholtz Reciprocity

交换入射和出射方向，BRDF 应保持一致：

$$
f_r(\omega_i,\omega_o)=f_r(\omega_o,\omega_i)
$$

这是很多常规反射模型的约束，但带有特殊传输、非互易介质或某些艺术模型时需要重新确认。

## 微表面分解

### 微表面模型

微表面模型把粗糙表面看成许多微小镜面。宏观高光由三部分组成：

$$
f_s=\frac{D(\mathbf H)F(\mathbf V,\mathbf H)G(\mathbf L,\mathbf V)}
{4(\mathbf N\cdot\mathbf L)(\mathbf N\cdot\mathbf V)}
$$

#### D：Normal Distribution Function

$D(\mathbf H)$ 描述半角方向附近的微表面面积密度。它满足 $\int D(\mathbf H)(\mathbf N\cdot\mathbf H)d\omega_H=1$，因此可用于采样的密度是 $D\,N\cdot H$；单独的 $D$ 不是归一化概率密度。

各向同性 GGX 使用

$$
D(\mu,\alpha)=\frac{\alpha^2}{\pi[\mu^2(\alpha^2-1)+1]^2},\qquad \mu=\mathbf N\cdot\mathbf H.
$$

实时 PBR 常用 GGX/Trowbridge-Reitz，因为它的长尾高光比较符合真实粗糙表面。

Roughness 改变分布宽度。Roughness 越低，分布越集中，高光更尖。

#### F：Fresnel

描述光到达微表面后有多少被反射。Schlick 近似：

$$
F=F_0+(1-F_0)(1-\mathbf V\cdot\mathbf H)^5
$$

$F_0$ 是正视角反射率。掠射角通常趋近更强反射。

#### G：Geometry Term

描述微表面之间的 Masking 和 Shadowing。一些面朝观察者的微表面可能被其他微表面挡住，或收不到光。

本文采用可分离 Smith 近似 $G=G_1(N\cdot V)G_1(N\cdot L)$，其中

$$
G_1(\mu)=\frac{2\mu}{\mu+\sqrt{\alpha^2+(1-\alpha^2)\mu^2}}.
$$

它分别估计观察方向与入射方向可见的微面比例。高度相关 Smith 会联合考虑两种遮蔽，不能只替换函数名而沿用同一份积分表。分母中的 $4(N\cdot L)(N\cdot V)$ 来自微面反射方向到宏观表面方向的测度和投影换算；它不是控制高光强度的经验项。

#### 代码中的组合顺序

以下 HLSL 机制函数展开 GGX、可分离 Smith 与 Schlick。`N`、`V`、`L` 是同一空间的单位向量，后两者从表面指向观察者和光源。颜色已在线性空间，`metallic`、`roughness`、`F0` 和 `baseColor` 均在 $[0,1]$。函数返回含入射余弦的响应，调用端乘光源贡献、可见性和距离衰减，不能再乘一次 `NoL`。

```hlsl
static const float PI = 3.14159265359;

float DistributionGGX(float NoH, float alpha)
{
    float a2 = alpha * alpha;
    float denominator = NoH * NoH * (a2 - 1.0) + 1.0;
    return a2 / (PI * denominator * denominator);
}

float SmithG1(float cosine, float alpha)
{
    float a2 = alpha * alpha;
    return 2.0 * cosine /
        (cosine + sqrt(a2 + (1.0 - a2) * cosine * cosine));
}

float3 FresnelSchlick(float VoH, float3 F0)
{
    float f = pow(1.0 - VoH, 5.0);
    return F0 + (1.0 - F0) * f;
}

float3 EvaluateDirectResponse(
    float3 N, float3 V, float3 L,
    float3 baseColor, float metallic, float roughness, float3 F0)
{
    float NoL = dot(N, L);
    float NoV = dot(N, V);
    if (NoL <= 0.0 || NoV <= 0.0) return 0.0;
    float3 H = normalize(V + L);
    float NoH = saturate(dot(N, H));
    float VoH = saturate(dot(V, H));
    float alpha = max(roughness * roughness, 0.002);
    float D = DistributionGGX(NoH, alpha);
    float G = SmithG1(NoV, alpha) * SmithG1(NoL, alpha);
    float3 F = FresnelSchlick(VoH, F0);
    // 合并 BRDF 与 NoL，避免先除再乘 NoL。
    float3 specularResponse = D * G * F / (4.0 * NoV);
    float3 diffuseWeight = (1.0 - F) * (1.0 - metallic);
    return diffuseWeight * baseColor * NoL / PI + specularResponse;
}
```

两个方向都在上半球时，`V+L` 非零。`alpha` 下限把理想镜面替换为有限宽度波瓣，属于明确的数值近似；材质端与 IBL 烘焙端要采用相同映射。极小值计算需使用足够精度，不能直接假定半精度稳定。

这里的 $(1-F)$ 是简化的漫反射衰减，不能凭这个逐方向权重断言整个组合严格守恒；半球能量与材料参数的关系见 [[04_光照模型与PBR/PBR材质]]。

## 参数与能量

### 粗糙度映射

不同 BRDF 对 Roughness 的映射不同。引擎还可能使用 $\alpha=roughness^2$ 让美术控制更线性。

跨引擎复制 Roughness 时要核对：

- 输入是 Roughness 还是 Smoothness；
- 是否平方；
- NDF 和 Geometry Term；
- IBL 预过滤的 Roughness 到 Mip 映射；
- 纹理是否经过正确颜色空间解码。

### 多次散射

单次微表面模型会把被 Masking/Shadowing 挡住的能量直接丢掉，粗糙材质可能显得过暗。多次散射补偿会估计这些能量在微表面间再次反射后的贡献。

实时引擎常用近似或查表，不会逐次追踪所有微表面反弹。

## 验证方法

- 使用灰球、金属球和不同 Roughness 阶梯图。
- 固定曝光和环境，避免自动曝光掩盖能量问题。
- 检查 $N\cdot L$、$N\cdot V$、D、F、G 的单独可视化。
- 对比直接光和 IBL 中的 Roughness 响应是否连续。
- 白炉测试（White Furnace Test）将所有入射方向设为单位辐射亮度，数值积分 $E(V)=\int f_r(L,V)(N\cdot L)d\omega_L$。对纯反射、无吸收且包含多次散射的模型，$E$ 应为 1；单次微表面模型允许 $E<1$，不能把这种模型误差误判为程序错误。

本页的 [数值检查](../examples/revision/test_lighting.py) 验证 NDF 投影面积归一化、交换光线与视线的互易性、背面返回零以及白炉能量。对于 $\alpha=1$、$N=V$、$F_0=1$，本文模型给出 $E=\int_0^1\mu/(1+\mu)d\mu=1-\ln2\approx0.30685$；这个解析值能识别余弦或分母被重复使用的问题。运行 `python -B 知识库/examples/revision/test_lighting.py`。

## 相关主题

- [[01_数学与采样/Monte Carlo采样]]、[[01_数学与采样/球谐光照]]
- [[04_光照模型与PBR/PBR材质]]
- [[04_光照模型与PBR/皮肤次表面散射]]
- [[04_光照模型与PBR/法线贴图]]、[[04_光照模型与PBR/IBL]]、[[04_光照模型与PBR/Cubemap环境采样]]
- [[05_光照阴影与GI/直接光照]]

示例与验证范围：代码按文中前提解释机制，完整类型、资源和项目状态需由接入工程补齐。完整目标引擎运行与GPU性能为UNVERIFIED；正文给出的机制与实际实验范围分别记录。

## 参考资料

- Bruce Walter et al., *Microfacet Models for Refraction through Rough Surfaces*.
- Brian Karis, *Real Shading in Unreal Engine 4*.
- [Google Filament：Specular BRDF、Energy loss in specular reflectance](https://google.github.io/filament/main/filament.html#materialsystem/specularbrdf)，核对 GGX、Smith、Schlick 与白炉定义。
- LearnOpenGL, `src/6.pbr/1.1.lighting` and `1.2.lighting_textured`.
