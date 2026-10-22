# HDR与曝光

灯光强度提高，最终画面却不一定更亮，因为自动曝光会改变整体缩放。HDR先保存超过显示白色的场景值，曝光决定它们进入显示曲线的位置；预曝光还要让历史颜色处于可比较尺度。

## 场景亮度

### HDR Buffer

场景线性光照可能远大于显示白色 1.0。HDR Render Target 使用浮点或高动态范围格式保存这些值，例如 `R11G11B10_FLOAT`、`RGBA16F`。前者没有Alpha且只表示非负值；后者可保存负值，适合部分滤波或色域变换的中间结果。

格式选择影响：

- 动态范围和精度；
- Alpha 是否存在；
- Blend/UAV 支持；
- 带宽和内存；
- 移动端 Tile/Attachment 成本。

### Exposure

曝光把场景亮度缩放到适合显示和 Tone Mapping 的范围：

$$
C_{exposed}=C_{scene}\cdot exposure
$$

摄影式工作流常用 $EV_{100}=\log_2(N^2/t\cdot100/ISO)$，其中 $N$ 是光圈值，$t$ 是以秒计的曝光时间。把EV换成Shader倍率还涉及测光标定，不能把EV数值直接当乘数。曝光倍率翻倍相当于增加一档输入光能。

Auto Exposure 通常从亮度直方图或平均对数亮度估计目标，再按不同明暗适应速度平滑变化。直方图需要排除极端高亮和黑边，否则结果会被少数像素拉走。

### 测光与时间适应

以下是明确的简化测光模型。在线性sRGB原色下，亮度 $Y=0.2126R+0.7152G+0.0722B$；换工作原色时需要对应的亮度系数。对有效像素使用权重 $w_i$，计算

$$
\bar Y=\exp\left(\frac{\sum_iw_i\ln\max(Y_i,\epsilon)}{\sum_iw_i}\right),\qquad
e_{target}=k/\bar Y.
$$

$k$ 是目标中灰，例如本模型取0.18。直方图方案先限制亮度范围和参与统计的百分位，再估计目标；空有效集合保持上一曝光，全黑画面以最小亮度和最大曝光限制避免发散。若输入已预曝光，统计前需除以对应倍率，或者把目标一致地换算到该尺度。

在对数曝光 $x=\log_2 e$ 上采用 $a=1-e^{-\Delta t/\tau}$、$x_t=(1-a)x_{t-1}+a x_{target}$，再取 $e_t=2^{x_t}$。$\Delta t$ 与 $\tau$ 使用秒，明适应和暗适应可选择不同的正时间常数。这个模型按经过的时间响应，固定目标时两个半步与一个整步相等；每帧使用固定混合系数则会随帧率改变速度。

### Pre-Exposure

预曝光把场景颜色乘以管线定义的曝光缩放，让HDR值保持在更适合存储的范围。不同引擎参数可能以曝光值或其倒数表达，核对目标代码和前后解码再确定乘除方向。后处理和历史 Buffer 需要理解这个缩放，否则不同帧的值不能直接比较。

## 历史曝光换算

令当前场景真实线性颜色为 $C_t$，写入缓冲的正预曝光倍率为 $p_t$，则 $S_t=p_tC_t$。前帧历史为 $H_{t-1}=p_{t-1}C_{t-1}$，重投影后换到当前存储尺度时应乘 $p_t/p_{t-1}$。显示曲线所需的倍率为 $e_t$，当前存储值只需再乘 $e_t/p_t$。

```hlsl
float3 HistoryInCurrentScale(float3 history, float previousScale, float currentScale)
{
    return history * (currentScale / previousScale);
}
float3 ExposureForDisplay(float3 storedScene, float currentScale, float displayExposure)
{
    return storedScene * (displayExposure / currentScale);
}
```

函数是HLSL机制片段，调用前验证三个倍率有限且大于零，无效历史直接拒绝。若 $C=20$、$p_{t-1}=0.5$，历史保存10；当前 $p_t=2$ 时应换成40。若当前显示曝光为0.25，进入显示曲线的值为 $40\times0.25/2=5$，与直接算 $20\times0.25$ 一致。

Unreal 5.6官方文档描述在写入场景颜色前应用前帧曝光。上面的 $p_t$ 表示当前缓冲实际采用的倍率，其来源可为上一帧曝光估计，不能仅凭变量含“current”或“previous”推断乘除方向。

## 验证方法

固定曝光检查线性灯光比例，再开自动曝光观察直方图、目标与适应曲线。切换相机或曝光时核对历史缩放，前帧系数为零或无效时拒绝历史。格式动态范围和GPU支持按平台核对。

[test_post.py](../examples/revision/test_post.py) 检查时间步长不变性、预曝光比例和零值/非有限倍率拒绝，正文换算函数通过DXC编译。实际测光直方图、引擎历史缓冲和GPU格式支持尚未运行。

## 相关主题

- [[07_颜色与后处理/颜色空间]]
- [[07_颜色与后处理/Tone Mapping]]
- [[07_颜色与后处理/Alpha表示]]

## 参考资料

- [Epic：Auto Exposure，Unreal 5.6](https://dev.epicgames.com/documentation/en-us/unreal-engine/auto-exposure-in-unreal-engine?application_version=5.6)，Histogram/Basic与Pre-Exposure段。
- [W3C：线性sRGB到XYZ转换](https://www.w3.org/TR/css-color-4/#color-conversion-code)，亮度为XYZ中的Y分量。
