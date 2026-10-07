# Tone Mapping

场景亮度可以远大于显示白色，直接Clamp会把亮部层次全部截掉。Tone Mapping用曲线压缩动态范围，再按明确色域和输出变换显示。曝光决定输入落在哪里，曲线决定这些值怎样分配对比。

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

## Color Grading 和 LUT

Color Grading 调整曝光、对比、白平衡、饱和度、色调和局部颜色。

3D LUT 把输入 RGB 映射到输出 RGB。引擎也可以把多组调色参数烘焙进 LUT，运行时一次采样。

注意：

- LUT 的输入输出色域必须明确；
- 低分辨率 LUT 会产生量化；
- LUT 之前或之后的 Tone Mapping 顺序不同；
- LUT 不能恢复已经 Clamp 掉的信息。

## 最小映射

HLSL片段对非负线性输入做逐通道Reinhard，输出尚未做显示编码。逐通道形式会改变饱和度，正式色彩流程另核对色域与亮度保持策略。

```hlsl
float3 mapped = sceneLinear / (1.0 + sceneLinear);
```

## 验证方法

输入0、1、10及更高亮度，检查曲线单调、有界和高光层次。固定曝光后对照灰阶、饱和色与LUT边界，确认输出编码只执行一次。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[07_颜色与后处理/HDR与曝光]]
- [[07_颜色与后处理/颜色空间]]
- [[07_颜色与后处理/Bloom]]
- [[07_颜色与后处理/屏幕空间AO]]
- [[07_颜色与后处理/景深与运动模糊]]

## 参考资料

- John Hable, *Filmic Tonemapping Operators*.
- Jorge Jimenez et al., *Next Generation Post Processing in Call of Duty: Advanced Warfare*.
- Epic Games and Unity documentation on Bloom, Exposure and Color Grading.
- LearnOpenGL, `src/5.advanced_lighting/9.ssao`.
- LearnOpenGL, `src/8.guest/2022/6.physically_based_bloom`.
