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
- BRDF LUT 采到纹理边缘会产生数值外推，应把 $N\cdot V$ 与 Roughness 映射到纹素中心；
- 低分辨率预过滤图会让强小光源在相邻 Mip 间突然消失。

BRDF LUT 通常保存 Fresnel 分解后的两个系数，输入限定在 $[0,1]^2$。它依赖固定的 NDF、Geometry 项和采样约定，更换 BRDF 后需要重新积分，不能把任意 LUT 与任意材质模型混用。

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
float2 terms = BrdfLut.SampleLevel(LinearClamp, float2(saturate(dot(N,V)), roughness), 0).rg;
float3 specular = environment * (F0 * terms.x + terms.y);
```

片段省略LUT半纹素地址修正与可见性，漫反射另从Irradiance求值。Split-sum是分离近似，高频环境和局部遮挡仍有误差。

## 验证方法

白色常量环境检查能量，粗糙度阶梯检查mip映射与LUT响应，镜面球核对环境方向。位置离开捕获中心时检查视差误差，与同位置参考积分对照。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[04_光照模型与PBR/BRDF与微表面模型]]
- [[05_光照阴影与GI/Reflection Probe]]
- [[04_光照模型与PBR/法线贴图]]
- [[04_光照模型与PBR/Cubemap环境采样]]

## 参考资料

- Mikkelsen, *MikkTSpace*.
- Brian Karis, *Real Shading in Unreal Engine 4*.
- Colin Barré-Brisebois and Stephen Hill, *Blending in Detail*.
- LearnOpenGL, `src/5.advanced_lighting/4.normal_mapping`.
- LearnOpenGL, `src/4.advanced_opengl/6.1.cubemaps_skybox` and `6.2.cubemaps_environment_mapping`.
