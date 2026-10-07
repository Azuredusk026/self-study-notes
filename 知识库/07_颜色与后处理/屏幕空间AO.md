# 屏幕空间AO

接触处需要更暗，但深度缓冲只有当前视图最前层。SSAO从这份局部信息采样周围遮挡，再过滤估计值。它能补接触层次，也会在屏幕外和深度断层失去信息，不能当作完整GI。

## Screen-space Ambient Occlusion

SSAO 从深度和法线估计当前点周围是否被几何遮挡。它只看屏幕可见表面，因此存在：

- 屏幕边缘缺失；
- 深度不连续 Halo；
- 远处物体在屏幕邻域造成错误遮挡；
- 噪声和时域拖影。

AO 应主要影响间接光。直接把它乘到所有光照会让有主光的区域也被错误压黑。

HBAO/GTAO 等方法改进方向包括 Horizon Search、法线余弦权重、距离衰减和更接近参考积分的近似。

### SSAO 的采样数据流

最小 SSAO 通常在观察空间工作。每个像素读取位置和法线，用一张小 Noise Texture 随机旋转半球 Kernel，再把样本点投影回屏幕，与深度缓冲中的表面比较。

```hlsl
float ComputeSSAO(float2 uv, float3 positionVS, float3 normalVS)
{
    float3 randomDir = normalize(NoiseTexture.Sample(NoiseSampler,
                                  uv * NoiseScale).xyz * 2.0 - 1.0);
    float3 T = normalize(randomDir - normalVS * dot(randomDir, normalVS));
    float3 B = cross(normalVS, T);
    float3x3 tbn = float3x3(T, B, normalVS);
    float occlusion = 0.0;

    for (uint i = 0; i < KernelSize; ++i) {
        float3 sampleVS = positionVS + mul(Kernel[i], tbn) * Radius;
        float4 clip = mul(Projection, float4(sampleVS, 1.0));
        float2 sampleUV = clip.xy / clip.w * 0.5 + 0.5;
        float sceneZ = PositionTexture.SampleLevel(PointSampler, sampleUV, 0).z;
        float range = smoothstep(0.0, 1.0,
                                 Radius / max(abs(positionVS.z - sceneZ), 1e-4));
        occlusion += (sceneZ >= sampleVS.z + Bias) * range;
    }
    return 1.0 - occlusion / KernelSize;
}
```

代码假定观察空间相机前方为负 Z，并直接保存 Position Buffer。实际管线常从深度重建位置以节省 GBuffer。深度约定改变时，比较方向也要改变。

Kernel 样本靠近原点时更密，能保留接触阴影；Noise Texture 只负责旋转采样方向，后续需要空间或时域滤波消除噪声。Radius 使用观察空间长度，Bias 用来减轻表面对自身的错误遮挡。

## 验证方法

显示原AO、滤波结果与半径，测试平面应基本无自遮挡。屏幕边缘、薄墙与远近深度断层分别检查；采样点出屏或在相机后时拒绝，随机向量平行法线时用稳定基底。AO合成明确作用于间接项。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[02_GPU与光栅化管线/深度缓冲与位置重建]]
- [[05_光照阴影与GI/动态GI]]
- [[07_颜色与后处理/Tone Mapping]]
- [[07_颜色与后处理/Bloom]]
- [[07_颜色与后处理/景深与运动模糊]]

## 参考资料

- John Hable, *Filmic Tonemapping Operators*.
- Jorge Jimenez et al., *Next Generation Post Processing in Call of Duty: Advanced Warfare*.
- Epic Games and Unity documentation on Bloom, Exposure and Color Grading.
- LearnOpenGL, `src/5.advanced_lighting/9.ssao`.
- LearnOpenGL, `src/8.guest/2022/6.physically_based_bloom`.
