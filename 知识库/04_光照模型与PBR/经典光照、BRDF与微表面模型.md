# 经典光照、BRDF 与微表面模型

光照模型要回答的是：某个方向来的光，经过表面后，有多少能量沿观察方向离开。实时渲染常把这个问题拆成光源、可见性、材质响应和几何关系。

## 先区分几个量

- Radiant Flux：单位时间传输的总辐射能量。
- Irradiance：单位面积接收到的通量，单位方向积分后落到表面。
- Radiance：沿某方向、单位投影面积、单位立体角传输的光量。渲染方程主要用它。

在工程中经常统称“光强”或“亮度”，但推导和单位换算时不能混用。

## Rendering Equation

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

## Lambert Diffuse

理想漫反射向所有出射方向分布相同。BRDF 为：

$$
f_d=\frac{\rho}{\pi}
$$

$\rho$ 是表面反照率。$1/\pi$ 用来满足能量守恒：对半球积分后，总反射能量不会超过入射能量。

实时 Shader 中常看到 `albedo * saturate(dot(N,L))`，省略的 $1/\pi$ 可能被光源单位、引擎约定或美术标定吸收。不能看到代码少了 $1/\pi$ 就直接判断错误，要先确认整套光照单位。

## Phong 和 Blinn-Phong

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

## BRDF 的约束

一个物理上合理的 BRDF 通常关心：

### 非负

反射不能凭空产生负能量。

### 能量守恒

所有方向反射出去的能量不能超过收到的能量。

### Helmholtz Reciprocity

交换入射和出射方向，BRDF 应保持一致：

$$
f_r(\omega_i,\omega_o)=f_r(\omega_o,\omega_i)
$$

这是很多常规反射模型的约束，但带有特殊传输、非互易介质或某些艺术模型时需要重新确认。

## 微表面模型

微表面模型把粗糙表面看成许多微小镜面。宏观高光由三部分组成：

$$
f_s=\frac{D(\mathbf H)F(\mathbf V,\mathbf H)G(\mathbf L,\mathbf V)}
{4(\mathbf N\cdot\mathbf L)(\mathbf N\cdot\mathbf V)}
$$

### D：Normal Distribution Function

描述有多少微表面法线接近半角向量。实时 PBR 常用 GGX/Trowbridge-Reitz，因为它的长尾高光比较符合真实粗糙表面。

Roughness 改变分布宽度。Roughness 越低，分布越集中，高光更尖。

### F：Fresnel

描述光到达微表面后有多少被反射。Schlick 近似：

$$
F=F_0+(1-F_0)(1-\mathbf V\cdot\mathbf H)^5
$$

$F_0$ 是正视角反射率。掠射角通常趋近更强反射。

### G：Geometry Term

描述微表面之间的 Masking 和 Shadowing。一些面朝观察者的微表面可能被其他微表面挡住，或收不到光。

常见实现使用 Smith 方法，把视线和光线方向的遮蔽组合起来。

## 为什么 Roughness 不能直接当高光指数

不同 BRDF 对 Roughness 的映射不同。引擎还可能使用 $\alpha=roughness^2$ 让美术控制更线性。

跨引擎复制 Roughness 时要核对：

- 输入是 Roughness 还是 Smoothness；
- 是否平方；
- NDF 和 Geometry Term；
- IBL 预过滤的 Roughness 到 Mip 映射；
- 纹理是否经过正确颜色空间解码。

## 多次散射

单次微表面模型会把被 Masking/Shadowing 挡住的能量直接丢掉，粗糙材质可能显得过暗。多次散射补偿会估计这些能量在微表面间再次反射后的贡献。

实时引擎常用近似或查表，不会逐次追踪所有微表面反弹。

## 如何验证材质模型

- 使用灰球、金属球和不同 Roughness 阶梯图。
- 固定曝光和环境，避免自动曝光掩盖能量问题。
- 检查 $N\cdot L$、$N\cdot V$、D、F、G 的单独可视化。
- 对比直接光和 IBL 中的 Roughness 响应是否连续。
- 用白炉测试（White Furnace Test）检查能量是否异常增加或丢失。

## 相关主题

- [[知识库/01_数学与采样/概率采样、积分与球谐函数]]
- [[知识库/04_光照模型与PBR/PBR材质与能量守恒]]
- [[知识库/04_光照模型与PBR/法线贴图、切线空间与IBL]]
- [[知识库/05_光照阴影与GI/光源与直接光照]]

## 参考资料

- Bruce Walter et al., *Microfacet Models for Refraction through Rough Surfaces*.
- Brian Karis, *Real Shading in Unreal Engine 4*.
- Google Filament, *Physically Based Rendering in Filament*.
