# Bloom

小亮点只模糊一次，容易得到单一大小的光圈。Bloom先从HDR颜色构建多尺度图，再从粗层向细层合成，让光晕同时保留近处亮核和远处扩散。每级过滤与能量权重共同决定形状和闪烁。

## Bloom 的完整流程

Bloom 模拟强光在镜头、传感器和视觉系统中向周围扩散。它应该由 HDR 高亮驱动。

### 1. 高亮提取

根据亮度或颜色阈值提取高亮。Soft Knee 在阈值附近平滑过渡，避免亮度稍微变化时 Bloom 突然出现。

也可以让全部线性HDR颜色参与扩散，保留弱光贡献。带阈值的方案需要明确阈值是在场景尺度还是曝光尺度定义：若输入已乘预曝光 $p$，场景阈值 $T$ 也应换成 $pT$，否则曝光变化会改变入选的光源。

下面的HLSL函数用最大RGB分量定义亮度 $b$，保持提取后的RGB比例。阈值 $T\ge0$，过渡半宽 $k\ge0$，均与输入处于同一线性尺度。在 $[T-k,T+k]$ 内构造二次过渡，$k=0$ 时退化为硬阈值。

```hlsl
float3 ExtractBloom(float3 color, float threshold, float knee)
{
    float brightness=max(color.r,max(color.g,color.b));
    float soft=0.0;
    if (knee>0.0) {
        float q=clamp(brightness-threshold+knee,0.0,2.0*knee);
        soft=q*q/(4.0*knee);
    }
    float contribution=max(max(brightness-threshold,soft),0.0);
    return color*(contribution/max(brightness,1e-6));
}
```

在上边界 $b=T+k$，二次项的值为 $k$、导数为1，正好接上线性项 $b-T$；下边界处值与导数都为0。这保证了阈值附近的连续性。它是美术提取模型，并非镜头散射的光学定律。

### 2. 降采样

逐级把高亮图缩小。每级都需要低通过滤，避免降采样混叠。低分辨率也让大范围 Blur 更便宜。

下面的 HLSL 代码用四个双线性样本构造一次简单低通降采样。`Source` 为线性HDR `Texture2D<float4>`，`LinearClamp` 为线性钳位采样器，`sourceTexelSize` 是上一层纹素尺寸的倒数：

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

在偶数尺寸、输出宽高各减半并采用中心对齐时，这组偏移对应一个2×2盒平均；它保留常量，但不足以彻底抑制高频混叠。奇数尺寸需要明确边界覆盖与归一化。完整实现可以使用更宽、经过推导的核，减少降采样混叠和方块感。逐级上采样时，用 Tent/Kawase 核把低 Mip 加回上一层，再以 Scatter 控制各尺度能量。每层都从相邻 Mip 合成，比只对最低分辨率做一次大模糊更容易保留不同大小的光晕。

### 3. Blur

可以使用 Separable Gaussian、Kawase、Dual Filter 等。不同核会改变光斑形状、稳定性和采样成本。

### 4. Upsample 和合并

从低分辨率逐级上采样，与更高分辨率层组合，得到不同尺度的光晕。最终通常以加法或能量受控方式合回 HDR Scene Color，再执行 Tone Mapping。

设降采样各级为 $D_i$，最低级 $U_m=D_m$。一种可检查的尺度混合是 $U_i=(1-s)D_i+s\,\mathrm{Upsample}(U_{i+1})$，$s\in[0,1]$。每级上采样核归一化后，常量输入仍保持常量；直接把所有级相加，则级数越多总亮度越高。

最终采用 $C'=C+gU_0$ 时是增加光晕能量的美术合成。若模拟归一化的光学扩散，应从原图分走相应能量，例如对无阈值、归一化模糊结果使用 $(1-g)C+gU_0$。两个目标的参数含义不同，不能只凭“物理Bloom”名称假定守恒。

降采样链和上采样合成需安排独立的可读输入与可写输出。若同一子资源既作输入又作输出，通常需要中间纹理或引擎明确支持的反馈机制。动态分辨率变化时重算每层尺寸、有效mip数和源纹素倒数，防止读取未初始化边缘。

## 验证方法

固定曝光，用超过1的亮点检查高亮提取、每级mip和合成结果。逐级关闭上采样贡献，核对光晕尺度与总亮度；动态分辨率时按源纹素尺度调整滤波。

[test_post.py](../examples/revision/test_post.py) 检查零输入、软阈值中点及不同层数的常量保持；正文提取和降采样函数通过DXC编译。GPU纹理链、滤波伪影和性能尚未测量。

## 相关主题

- [[07_颜色与后处理/HDR与曝光]]
- [[07_颜色与后处理/Tone Mapping]]
- [[01_数学与采样/采样与混叠]]
- [[07_颜色与后处理/屏幕空间AO]]
- [[07_颜色与后处理/景深与运动模糊]]

## 参考资料

- [Filament：Bloom](https://google.github.io/filament/main/filament.html#imagingpipeline/physicallybasedcamera/bloom)，曝光相对自发光与Bloom输入。
- [LearnOpenGL 作者示例：Physically based bloom](https://github.com/JoeyDeVries/LearnOpenGL/tree/master/src/8.guest/2022/6.physically_based_bloom)，多尺度降采样与上采样的进一步实现入口；本页使用显式给出的简化归一化模型。
