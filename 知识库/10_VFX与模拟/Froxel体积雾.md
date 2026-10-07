# Froxel体积雾

视锥网格将散射与透射离散为三维资源，再沿视线累计供表面合成。时域历史用于减少噪声，前缀积分需要同时保存累计透射。

## Froxel 体积雾

局部体积雾的主流实时方案是把视锥离散成体素网格。由于这些体素是视锥形而非立方体（沿深度方向逐渐变大），通常称为 froxel（frustum voxel）。

典型分辨率如 $160\times90\times64$。深度方向一般按指数分布，让近处体素更密——与透视投影的采样密度需求一致。

整个方案分两步：

1. **散射计算**：每个 froxel 求一次光照散射与消光，结果写入三维纹理；
2. **积分**：沿深度方向累计散射与透射，得到从相机到指定深度的介质结果。散射需乘之前各段的透射率，通常不能直接做普通数值相加。

第二步是关键。有了前缀和，着色时只需按像素深度采样一次三维纹理就能拿到总散射量，复杂度 $O(1)$，不必沿视线逐步进行光线步进。

### 沿深度复用

让一个线程负责一段连续的深度切片，而非每个 froxel 一个线程：

```hlsl
[numthreads(4, 4, 4)]
void ScatteringKernel(uint3 id : SV_DispatchThreadID)
{
    uint startSlice = id.z * _SlicesPerThread;
    uint endSlice   = startSlice + _SlicesPerThread;

    for (uint3 v = uint3(id.xy, startSlice); v.z < endSlice; ++v.z)
    {
        // froxelFront = 上一格的 froxelBack，沿射线递推
        // 距离、透射率可以累加复用
    }
}
```

沿 Z 步进时，前一个体素的远平面就是后一个的近平面，射线距离与累计透射率都可以递推。这比每个体素独立计算省下大量重复工作，代价是牺牲 Z 方向的并行度。

### 时域累积

逐帧独立计算的体积雾噪点明显，提高采样数的代价又太高。标准做法是时域累积：每帧用抖动偏移采样，再与历史结果混合。

典型的混合权重偏向历史（例如当前帧仅占七分之一），用多帧摊薄噪声：

```hlsl
float3 reprojUVW = CalcReprojectUVW(reprojPosWS, _PrevCameraPositionWS,
                                    _PrevViewProjectionMatrix, ...);
if (all(reprojUVW >= 0.0) && all(reprojUVW <= 1.0))
{
    real3 history = SAMPLE_TEXTURE3D_LOD(_PrevVolumetricFog, s_linear, reprojUVW, 0).rgb;
    current = lerp(current, history, TAA_HISTORY_BLEND_WEIGHT);
}
```

一个关键细节：**反投影必须使用未抖动的位置，采样才使用抖动位置**。两者混用会让历史查找位置随抖动摆动，表现为持续闪烁——这与抖动本身要消除的噪声是两回事，且更难察觉成因。

实现上需要双缓冲三维纹理，每帧交换当前与历史。超出历史范围（相机快速移动、首帧）时要回退到纯当前帧结果。

### 融合两个 Kernel 的可能

散射与积分分成两个 Kernel 的代价是：一整张三维纹理的写入加读取、一次额外 Dispatch、一个 UAV 屏障。

若一个线程完整负责一条 XY 视线的全部深度切片，可以边计算局部散射边合成累计结果。若不同线程只负责部分切片，仍需跨段前缀处理，不能仅加局部累加器。融合可能降低中间纹理访问，也会减少 Z 方向并行度。

是否划算取决于三维纹理的带宽成本与并行度损失的相对大小，需要在目标平台实测。这类“多趟换并行度”的权衡在 Compute 管线中很常见。

## 透射加权的前缀合成

每段保存局部散射 `segmentRadiance` 与段透射 `segmentT`。输入为沿同一视线排列的切片，输出累计散射和透射。两者可以写入同一个 RGBA 资源。

```hlsl
float3 accumulatedRadiance = 0.0;
float accumulatedT = 1.0;
for (uint slice = 0; slice < sliceCount; ++slice)
{
    float4 segment = LoadSegment(uint3(pixel, slice));
    accumulatedRadiance += accumulatedT * segment.rgb;
    accumulatedT *= segment.a;
    StorePrefix(uint3(pixel, slice),
        float4(accumulatedRadiance, accumulatedT));
}
```

切片长度需要参与局部段积分。合成不透明表面时使用 `radiance + transmittance * surfaceColor`。并行前缀算法可利用段合成的结合律，但线程局部的多切片循环还需处理分段前缀，不能只拼接各线程的局部累积。

## 验证方法

- 固定同一视线与非负消光，检查累计透射不增。
- 对比直接步进与三维积分结果，检查深度切片插值。
- 相机切换和灯光突变时拒绝过期历史。
- 融合 kernel 前后对比整帧耗时、寄存器压力和输出误差。

## 相关主题

- [[01_数学与采样/信号、频率与噪声]]
- [[02_GPU与光栅化管线/抗锯齿与时域重建]]
- [[03_Shader编程/Compute Shader与GPU执行模型]]
- [[07_颜色与后处理/颜色空间、Alpha、HDR与曝光]]
- [[10_VFX与模拟/常用VFX材质、模拟与性能]]
- [[14_性能分析与优化/帧瓶颈怎么判断]]

- [[10_VFX与模拟/大气散射、天空与体积云]]

## 参考资料

- Sébastien Hillaire, *A Scalable and Production Ready Sky and Atmosphere Rendering Technique*.
- Eric Bruneton and Fabrice Neyret, *Precomputed Atmospheric Scattering*.
- Andrew Schneider, *The Real-time Volumetric Cloudscapes of Horizon Zero Dawn*.
- Bartlomiej Wronski, *Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering*, SIGGRAPH.
- Sébastien Hillaire, *Physically Based and Unified Volumetric Rendering in Frostbite*.
