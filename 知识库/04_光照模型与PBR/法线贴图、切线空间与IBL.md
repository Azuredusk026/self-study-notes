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
