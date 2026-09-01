# 法线贴图、切线空间与 IBL

法线贴图改变的是光照计算使用的表面方向，不会真正改变轮廓、遮挡和碰撞。IBL 则把来自环境各方向的光照压缩成运行时可采样的数据。

## 几何法线和着色法线

- Geometric Normal 来自三角形几何，决定真实表面方向。
- Vertex Normal 是顶点属性，可以跨三角形平滑。
- Shading Normal 是最终用于 BRDF 的方向，可能由插值法线和 Normal Map 组合。

着色法线可能偏离几何法线。偏差过大时会产生能量、阴影终止线和背面漏光问题。

## Tangent Space

切线空间使用三个基向量：

- Tangent $\mathbf T$：通常沿 UV 的 U 方向；
- Bitangent $\mathbf B$：通常沿 UV 的 V 方向；
- Normal $\mathbf N$：表面法线。

组成 TBN 矩阵后，可以在切线空间和世界/视图空间之间变换方向。

Bitangent 经常不直接存储，而是由：

$$
\mathbf B=sign\cdot(\mathbf N\times\mathbf T)
$$

重建。`sign` 记录镜像 UV 的手性。

## 为什么切线需要统一生成规则

Normal Map 烘焙时使用一套切线基，运行时如果用另一套，接缝和高光会不一致。MikkTSpace 是常用统一方案，但 DCC、烘焙器、引擎导入设置仍要确认是否一致。

硬边、UV 缝和镜像 UV 都可能导致顶点拆分。一个空间位置相同，不代表可以共享同一个 Normal/Tangent/UV 顶点。

## Normal Map 解码

纹理通常把 $[-1,1]$ 的方向映射到 $[0,1]$。运行时解码后需要恢复 Z，或从压缩格式读取三个分量。

BC5 常保存 X、Y 两个通道，再计算：

$$
z=\sqrt{\max(0,1-x^2-y^2)}
$$

这种方式给 X/Y 更多精度，适合切线空间法线。若 X/Y 因压缩落到单位圆外，需要 Clamp，否则会出现 NaN。

DirectX 和 OpenGL Normal Map 常在 Y 方向约定上相反。错误时凹凸会翻转。

### 从纹理到世界法线

下面的 HLSL 示例从 BC5 风格的 XY 解码切线空间法线，再用顶点切线的 `w` 恢复手性。输入的世界法线和切线需要在插值后重新归一化：

```hlsl
float3 DecodeNormalWS(
    float2 packedXY,
    float3 normalWS,
    float4 tangentWS)
{
    float2 xy = packedXY * 2.0 - 1.0;
    float z = sqrt(saturate(1.0 - dot(xy, xy)));
    float3 normalTS = float3(xy, z);

    float3 N = normalize(normalWS);
    float3 T = normalize(tangentWS.xyz - N * dot(N, tangentWS.xyz));
    float3 B = cross(N, T) * tangentWS.w;
    return normalize(mul(normalTS, float3x3(T, B, N)));
}
```

Gram-Schmidt 步骤去掉切线在法线方向的插值误差。矩阵乘法方向取决于 HLSL 编译约定；接入引擎时应使用其标准切线空间函数，并用方向 RGB 检查结果。

## Normal 强度

简单把 X/Y 乘强度后应重新计算或归一化 Z。直接把整个法线乘一个数，再 Normalize，不会改变方向，因此也不会改变凹凸强度。

## 多张法线如何混合

直接 `normalize(lerp(n1,n2,t))` 可以做两个方向之间的过渡，但把 Detail Normal 叠加到 Base Normal 时，普通加法或 Lerp 容易压平细节。

Reoriented Normal Mapping 等方法会把 Detail Normal 重新定向到 Base Normal 的局部表面，更适合层叠材质。具体公式需要与当前法线编码一致。

## Cubemap、Skybox 与环境映射

Cubemap 用三维方向查找六个二维面。采样坐标不是普通 UV，而是从立方体中心指向目标方向的向量。硬件根据绝对值最大的分量选择面，再计算面内坐标。

六个面的朝向、坐标手性和纹理原点必须一致。接缝常来自：

- 面顺序或旋转错误；
- 边缘 Texel 没有连续过滤；
- 各面曝光和颜色处理不同；
- Mip 生成时没有跨面处理；
- 方向在错误空间中计算。

Skybox 常使用一个以相机为中心的立方体。View Matrix 保留旋转、去掉平移，让背景看起来位于无限远。下面的 GLSL 写法让输出深度位于远平面；深度测试使用 `LEQUAL`，并在不透明物体之后绘制：

```glsl
vec4 SkyboxPosition(vec3 cubePosition)
{
    mat4 viewRotation = mat4(mat3(view));
    vec4 clip = projection * viewRotation
              * vec4(cubePosition, 1.0);
    return clip.xyww;
}

vec3 SampleSkybox(vec3 directionWS)
{
    return texture(environmentMap, normalize(directionWS)).rgb;
}
```

`clip.xyww` 让透视除法后的 Z 等于 1。反向 Z 管线的深度值和比较函数不同，需要使用引擎提供的 Skybox 深度约定。

环境反射使用反射方向查询 Cubemap：

$$
\mathbf R=reflect(-\mathbf V,\mathbf N)
$$

$\mathbf V$ 和 $\mathbf N$ 必须处于 Cubemap 期望的同一空间。直接采样清晰环境只适合理想镜面；粗糙材质需要按 BRDF 预过滤后的环境 Mip。

透明介质的理想折射方向可以用 `refract` 计算。输入的 $\eta$ 是入射介质折射率与透射介质折射率之比：

```glsl
vec3 incidentWS = normalize(positionWS - cameraPositionWS);
float eta = etaIncident / etaTransmitted;
vec3 refractedWS = refract(incidentWS, normalize(normalWS), eta);
vec3 environment = texture(environmentMap, refractedWS).rgb;
```

当发生全反射时，`refract` 返回零向量，Shader 应改用反射方向。这个环境采样只近似无限远背景，不包含物体厚度、吸收、局部遮挡和折射后的场景深度。

动态环境捕获会从 Probe 位置覆盖 Cubemap 的六个面。实现可以提交六个视图，也可以使用分层渲染一次写入多个面；完整更新还要生成 Mip 或重新预过滤。常见调度方式是分面、分帧或按重要性更新，并从捕获列表中排除 Probe 自己。验证时在 Probe 六面放置方向标记，检查接缝、手性、更新延迟和递归捕获。

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

## 验证方法

- 显示 T、B、N 三个方向，检查手性和接缝。
- 使用非均匀缩放测试法线矩阵。
- 分别关闭 Normal Map、Diffuse IBL 和 Specular IBL。
- 用镜面球检查 Cubemap 方向和接缝。
- 用 Roughness 阶梯检查 Prefilter Mip 是否连续。
- 对比烘焙器和引擎使用的 Tangent Basis。

## 相关主题

- [[01_数学与采样/向量、矩阵与空间变换]]
- [[01_数学与采样/概率采样、积分与球谐函数]]
- [[04_光照模型与PBR/经典光照、BRDF与微表面模型]]
- [[06_纹理技术/高度、法线与视差映射]]
- [[06_纹理技术/纹理采样、过滤、Mipmap与压缩]]

## 参考资料

- Mikkelsen, *MikkTSpace*.
- Brian Karis, *Real Shading in Unreal Engine 4*.
- Colin Barré-Brisebois and Stephen Hill, *Blending in Detail*.
- LearnOpenGL, `src/5.advanced_lighting/4.normal_mapping`.
- LearnOpenGL, `src/4.advanced_opengl/6.1.cubemaps_skybox` and `6.2.cubemaps_environment_mapping`.
