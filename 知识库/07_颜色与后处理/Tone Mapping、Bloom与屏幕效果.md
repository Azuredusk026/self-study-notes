# Tone Mapping、Bloom 与屏幕效果

后处理读取已经渲染出的屏幕 Buffer，再生成最终画面。很多效果依赖 HDR 颜色、深度、法线和运动向量。执行顺序会直接改变结果。

## 后处理链的常见顺序

不同引擎会调整，但可以用下面的关系理解：

```text
HDR Scene Color
  → 曝光
  → Bloom / DOF / Motion Blur / AO 合成
  → Tone Mapping
  → Color Grading / Display Transform
  → UI 或最终输出
```

有些 Color Grading 会合并到 Tone Mapping LUT，有些透明和 UI 会在不同位置绘制。必须按实际帧捕获确认。

## Tone Mapping

Tone Mapping 把场景 HDR 映射到显示设备能表达的范围。它不是简单 Clamp。

### Reinhard

简单形式：

$$
C_{out}=\frac{C}{1+C}
$$

它能压缩高亮，但整体容易发灰，颜色处理也比较简单。

### Filmic Curve

Filmic 曲线通常分为 Toe、Linear Section 和 Shoulder：

- Toe 控制暗部压缩；
- 中段保持主要对比；
- Shoulder 平滑压缩高亮，避免硬截断。

ACES 相关实时曲线通常是对 ACES 流程的近似或拟合，不代表完整 ACES 色彩管理。使用时需要确认输入色域、输出变换和引擎实现。

## Bloom 的完整流程

Bloom 模拟强光在镜头、传感器和视觉系统中向周围扩散。它应该由 HDR 高亮驱动。

### 1. 高亮提取

根据亮度或颜色阈值提取高亮。Soft Knee 在阈值附近平滑过渡，避免亮度稍微变化时 Bloom 突然出现。

有些物理或统一管线不设置硬阈值，而是让所有 HDR 值参与，只靠曝光和 Bloom 强度控制。

### 2. 降采样

逐级把高亮图缩小。每级都需要低通过滤，避免降采样混叠。低分辨率也让大范围 Blur 更便宜。

下面的 HLSL 代码用四个双线性样本构造一次简单低通降采样。`sourceTexelSize` 是上一层的单个 Texel 尺寸：

```hlsl
float3 DownsampleBloom(float2 uv, float2 sourceTexelSize)
{
    float2 o = sourceTexelSize * 0.5;
    float3 sum = 0.0;
    sum += Source.SampleLevel(LinearClamp, uv + float2(-o.x, -o.y), 0).rgb;
    sum += Source.SampleLevel(LinearClamp, uv + float2( o.x, -o.y), 0).rgb;
    sum += Source.SampleLevel(LinearClamp, uv + float2(-o.x,  o.y), 0).rgb;
    sum += Source.SampleLevel(LinearClamp, uv + float2( o.x,  o.y), 0).rgb;
    return sum * 0.25;
}
```

完整实现可以使用更宽、经过推导的核，减少降采样混叠和方块感。逐级上采样时，用 Tent/Kawase 核把低 Mip 加回上一层，再以 Scatter 控制各尺度能量。每层都从相邻 Mip 合成，比只对最低分辨率做一次大模糊更容易保留不同大小的光晕。

### 3. Blur

可以使用 Separable Gaussian、Kawase、Dual Filter 等。不同核会改变光斑形状、稳定性和采样成本。

### 4. Upsample 和合并

从低分辨率逐级上采样，与更高分辨率层组合，得到不同尺度的光晕。最终通常以加法或能量受控方式合回 HDR Scene Color，再执行 Tone Mapping。

Bloom 不是把模糊亮度乘回原图。乘法更接近调制颜色，会让暗部和能量关系变得异常。

## Color Grading 和 LUT

Color Grading 调整曝光、对比、白平衡、饱和度、色调和局部颜色。

3D LUT 把输入 RGB 映射到输出 RGB。引擎也可以把多组调色参数烘焙进 LUT，运行时一次采样。

注意：

- LUT 的输入输出色域必须明确；
- 低分辨率 LUT 会产生量化；
- LUT 之前或之后的 Tone Mapping 顺序不同；
- LUT 不能恢复已经 Clamp 掉的信息。

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

## Depth of Field

景深根据镜头参数和深度估计 Circle of Confusion（CoC）。焦平面附近 CoC 小，前景和背景离焦区域 CoC 大。

实现难点：

- 前景模糊会覆盖后方清晰像素；
- 深度边界容易漏色；
- 半透明没有可靠单层深度；
- 大 Blur Radius 成本高；
- Bokeh 形状和能量需要控制。

常见流程会分离 Near/Far Field，在低分辨率 Gather/Scatter，再按 CoC 合成。

## Motion Blur

运动模糊使用相机和物体 Motion Vector 沿运动方向采样。只用相机矩阵无法处理骨骼、顶点动画和独立物体运动。

需要限制最大半径，处理深度边界和前后景速度差。Velocity Buffer 错误会产生拉丝和背景污染。

## Lens Effect

Vignette、Chromatic Aberration、Film Grain、Lens Distortion 可以塑造镜头感，但它们通常在显示链后段工作。

这些效果不应遮盖曝光、颜色空间或上游渲染错误。Chromatic Aberration 和 Grain 还会降低 TAA/压缩后的细节稳定性。

## Fog 与参与介质

Linear Fog 在起止距离之间线性增加雾量；Exponential Fog 使用指数衰减，让密度随距离自然累积；Height Fog 再让密度随高度变化，用于地面雾和大气层次。这些简化模型通常只根据像素位置计算透射率，不能表达局部光束和体积遮挡。

Volumetric Fog 把视锥划成三维 Froxel，注入介质密度、灯光和阴影，再沿视线积分散射与透射。它能表现局部雾、光柱和带阴影的空气透视，但需要时域重投影稳定低分辨率体积数据。快速变化的灯光、相机切换和密度边界容易出现拖影或分层。

## 性能和分辨率

后处理多为全屏工作，成本约与像素数、采样数和中间 Buffer 带宽相关。

常用优化：

- Half/Quarter Resolution；
- Ping-pong Render Target 复用；
- 合并可兼容 Pass；
- Compute Tiling 和 Shared Memory；
- 使用更小格式；
- Dynamic Resolution；
- 通过 Render Graph 缩短临时资源生命周期。

合并 Pass 需要权衡寄存器、分支和缓存，不能只为了减少 Draw Call 把所有效果塞进一个巨型 Shader。

## 验证方法

- 按阶段查看 HDR Scene、Exposure、Bloom Pyramid 和 Tone Mapped 输出。
- 用超过 1.0 的已知高亮测试 Bloom，不只观察 LDR 白色。
- 分别冻结曝光和 Tone Mapping，避免参数互相补偿。
- 检查 AO 是否只影响期望的间接项。
- 显示 CoC、Velocity 和 Blur Radius。
- 在目标分辨率和动态分辨率下记录每个 Pass 的 GPU 时间和带宽。

## 相关主题

- [[07_颜色与后处理/颜色空间、Alpha、HDR与曝光]]
- [[01_数学与采样/信号、频率与噪声]]
- [[02_GPU与光栅化管线/抗锯齿与时域采样]]
- [[13_引擎架构与资源系统/Render Pass、Command Buffer与Render Graph]]

## 参考资料

- John Hable, *Filmic Tonemapping Operators*.
- Jorge Jimenez et al., *Next Generation Post Processing in Call of Duty: Advanced Warfare*.
- Epic Games and Unity documentation on Bloom, Exposure and Color Grading.
- LearnOpenGL, `src/5.advanced_lighting/9.ssao`.
- LearnOpenGL, `src/8.guest/2022/6.physically_based_bloom`.
