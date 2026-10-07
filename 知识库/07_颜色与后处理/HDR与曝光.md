# HDR与曝光

灯光强度提高，最终画面却不一定更亮，因为自动曝光会改变整体缩放。HDR先保存超过显示白色的场景值，曝光决定它们进入显示曲线的位置；预曝光还要让历史颜色处于可比较尺度。

## 场景亮度

### HDR Buffer

场景线性光照可能远大于显示白色 1.0。HDR Render Target 使用浮点或高动态范围格式保存这些值，例如 `R11G11B10_FLOAT`、`RGBA16F`。

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

摄影式工作流可能使用 EV100、光圈、快门和 ISO 推导曝光。

Auto Exposure 通常从亮度直方图或平均对数亮度估计目标，再按不同明暗适应速度平滑变化。直方图需要排除极端高亮和黑边，否则结果会被少数像素拉走。

### Pre-Exposure

预曝光把场景颜色乘以管线定义的曝光缩放，让HDR值保持在更适合存储的范围。不同引擎参数可能以曝光值或其倒数表达，核对目标代码和前后解码再确定乘除方向。后处理和历史 Buffer 需要理解这个缩放，否则不同帧的值不能直接比较。

## 历史曝光换算

以下为机制伪代码，当前和历史颜色各自已经乘过其对应的正曝光缩放。

```text
historyInCurrentScale = historyColor * currentPreExposure / previousPreExposure
exposed = sceneLinear * exposure
displayInput = ResolvePipelineExposureConvention(exposed)
```

## 验证方法

固定曝光检查线性灯光比例，再开自动曝光观察直方图、目标与适应曲线。切换相机或曝光时核对历史缩放，前帧系数为零或无效时拒绝历史。格式动态范围和GPU支持按平台核对。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[07_颜色与后处理/颜色空间]]
- [[07_颜色与后处理/Tone Mapping]]
- [[07_颜色与后处理/Alpha表示]]

## 参考资料

- IEC 61966-2-1, sRGB color space.
- Microsoft Learn, *Data Conversion Rules* for sRGB resources.
- Epic Games, *Auto Exposure* and *Pre-Exposure* documentation.
