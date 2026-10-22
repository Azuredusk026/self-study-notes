# Tone Mapping

场景亮度可以远大于显示白色，直接Clamp会把亮部层次全部截掉。Tone Mapping用曲线压缩动态范围，再按明确色域和输出变换显示。曝光决定输入落在哪里，曲线决定这些值怎样分配对比。

## Tone Mapping

Tone Mapping 把场景 HDR 映射到显示设备能表达的范围。它不是简单 Clamp。

### Reinhard

简单形式：

$$
C_{out}=\frac{C}{1+C}
$$

对非负标量，曲线满足 $T(0)=0$、$T(1)=0.5$、$T(10)=10/11$，导数 $T'(C)=1/(1+C)^2>0$。高亮仍可区分，只是对比逐渐压缩。是否显得发灰还取决于曝光、中灰位置和显示编码，不能单由曲线名称判断。

### Filmic Curve

Filmic 曲线通常分为 Toe、Linear Section 和 Shoulder：

- Toe 控制暗部压缩；
- 中段保持主要对比；
- Shoulder 平滑压缩高亮，避免硬截断。

ACES 相关实时曲线通常是对 ACES 流程的近似或拟合，不代表完整 ACES 色彩管理。使用时需要确认输入色域、输出变换和引擎实现。

### 亮度与颜色比例

逐通道映射会让三个通道以不同倍率压缩。例如 `(10,2,1)` 变为约 `(0.909,0.667,0.5)`，红绿比例由5变为约1.36。另一种演示模型先计算亮度 $Y$，再统一缩放 $C'=C\,T(Y)/Y$；对于Reinhard可简化为 $C'=C/(1+Y)$，零亮度不再需要除法。

统一缩放保持RGB比例，却不能保证每个通道都不超过1。饱和高亮仍需色域映射，直接逐通道裁剪会再次改变颜色。因此Tone Mapping、色域映射与输出编码有不同职责；实际流程需说明工作原色、显示峰值和目标编码。PQ或HLG显示输出也不等同于“RGB限制到0—1再套sRGB”。

## Color Grading 和 LUT

Color Grading 调整曝光、对比、白平衡、饱和度、色调和局部颜色。

3D LUT 把输入 RGB 映射到输出 RGB。引擎也可以把多组调色参数烘焙进 LUT，运行时一次采样。

注意：

- LUT 的输入输出色域必须明确；
- 低分辨率 LUT 会产生量化；
- LUT 之前或之后的 Tone Mapping 顺序不同；
- LUT 不能恢复已经 Clamp 掉的信息。

若三维LUT在输入参数0和1处分别保存首尾格点，边长为 $N$，纹理坐标应为 `uv=(parameter*(N-1)+0.5)/N`，使端点落在纹素中心。三线性采样会混合相邻8点。HDR输入常先经对数等整形映射进入有限域；直接把大于1的场景值钳到1会让全部高光查询同一个边界。LUT的输入域、整形函数与生成时的处理顺序必须一同发布。

## 最小映射

HLSL片段对非负线性输入做逐通道Reinhard，输出尚未做显示编码。逐通道形式会改变饱和度，正式色彩流程另核对色域与亮度保持策略。

```hlsl
float3 mapped = sceneLinear / (1.0 + sceneLinear);
```

## 验证方法

输入0、1、10及更高亮度，检查曲线单调、有界和高光层次。固定曝光后对照灰阶、饱和色与LUT边界，确认输出编码只执行一次。

[test_post.py](../examples/revision/test_post.py) 检查按亮度缩放保持RGB比例，并用饱和色反例说明其仍可能出色域；既有机制检查覆盖Reinhard单调与极值。完整显示变换、LUT资产与目标显示器尚未验证。

## 相关主题

- [[07_颜色与后处理/HDR与曝光]]
- [[07_颜色与后处理/颜色空间]]
- [[07_颜色与后处理/Bloom]]
- [[07_颜色与后处理/屏幕空间AO]]
- [[07_颜色与后处理/景深与运动模糊]]

## 参考资料

- [Filament：Imaging pipeline](https://google.github.io/filament/main/filament.html#imagingpipeline)，场景颜色、曝光和显示链路。
- [W3C CSS Color 4：色彩转换代码](https://www.w3.org/TR/css-color-4/#color-conversion-code)，RGB原色变换与输出传递函数。
- John Hable, *Filmic Tonemapping Operators*，电影式曲线的进一步阅读；本页Reinhard关系由显式公式与数值检查验证。
