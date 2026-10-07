# Bloom

小亮点只模糊一次，容易得到单一大小的光圈。Bloom先从HDR颜色构建多尺度图，再从粗层向细层合成，让光晕同时保留近处亮核和远处扩散。每级过滤与能量权重共同决定形状和闪烁。

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

## 验证方法

固定曝光，用超过1的亮点检查高亮提取、每级mip和合成结果。逐级关闭上采样贡献，核对光晕尺度与总亮度；动态分辨率时按源纹素尺度调整滤波。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[07_颜色与后处理/HDR与曝光]]
- [[07_颜色与后处理/Tone Mapping]]
- [[01_数学与采样/采样与混叠]]
- [[07_颜色与后处理/屏幕空间AO]]
- [[07_颜色与后处理/景深与运动模糊]]

## 参考资料

- John Hable, *Filmic Tonemapping Operators*.
- Jorge Jimenez et al., *Next Generation Post Processing in Call of Duty: Advanced Warfare*.
- Epic Games and Unity documentation on Bloom, Exposure and Color Grading.
- LearnOpenGL, `src/5.advanced_lighting/9.ssao`.
- LearnOpenGL, `src/8.guest/2022/6.physically_based_bloom`.
