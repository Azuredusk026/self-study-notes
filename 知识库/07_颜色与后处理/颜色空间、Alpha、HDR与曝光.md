# 颜色空间、Alpha、HDR 与曝光

渲染中的颜色要区分三件事：数值如何编码、数值属于什么色域、数值代表场景光还是显示输出。把它们都叫“Gamma”会让纹理导入、混合和后处理出错。

## 为什么光照要在线性空间计算

现实中的光能量可以线性相加。两盏相同灯一起照射，理想情况下总能量是单盏的两倍。

显示和图片编码通常不是线性的。如果直接在编码值上做光照、插值和混合，会错误地压暗中间值。

典型流程：

```text
sRGB 颜色纹理
  → 采样时解码为 Linear
  → 光照、混合和后处理
  → Tone Mapping
  → 输出编码到显示空间
```

## sRGB 不是单纯 Gamma 2.2

sRGB 使用分段传递函数。低值部分近似线性，其余部分接近幂函数。

从 sRGB 编码值 $C_s$ 解码到线性值 $C_l$ 的常见形式：

$$
C_l=
\begin{cases}
C_s/12.92,&C_s\le0.04045\\
\left(\frac{C_s+0.055}{1.055}\right)^{2.4},&C_s>0.04045
\end{cases}
$$

用 $C^{2.2}$ 是简化近似，不是完整 sRGB 定义。

sRGB 还规定色度原色和白点。讨论广色域、HDR 显示时，不能只看传递函数。

## 哪些纹理使用 sRGB

通常按“它是给人看的颜色，还是给 Shader 读取的数据”判断。

### 常用 sRGB

- Base Color/Albedo；
- UI 彩色图片；
- 手绘颜色和部分 Emissive 颜色。

### 常用 Linear/Data

- Normal；
- Roughness、Metallic、AO；
- Mask、Height、SDF；
- LUT 和数值查找纹理；
- 深度和运动向量。

不能因为一张贴图看起来是灰色就判断它是 Linear。灰色照片仍是颜色，单通道 Roughness 才是数据。

## Alpha 通道怎么处理

sRGB 格式的非线性转换通常只作用于 RGB，Alpha 保持线性数值。Alpha 可能代表：

- Coverage/Opacity；
- Mask；
- Smoothness；
- 其他项目数据。

因此一张 Base Color 的 RGB 可以按 sRGB 解码，Alpha 仍作为线性 Mask 使用。

> [!warning] 不要靠猜
> 纹理文件本身不会保证 Alpha 的语义。导入器、压缩格式和 Shader 约定需要一致。

## Alpha Blend 应在线性空间进行

如果 RGB 仍在 sRGB 编码空间就做混合，中间颜色会偏暗。正确过程是先解码 RGB 到 Linear，在线性 Render Target 上混合，最终显示时再编码。

硬件对 sRGB Render Target 可以在写入时自动编码，对 sRGB Texture 可以在采样时自动解码。是否发生转换由资源格式和 View 决定，不是 Shader 变量名决定。

## Straight 和 Premultiplied Alpha

### Straight Alpha

RGB 保存未乘 Alpha 的原始颜色。常见混合：

$$
C_o=\alpha_sC_s+(1-\alpha_s)C_d
$$

透明像素中的 RGB 仍会参与纹理过滤。如果边缘外填充为黑色，可能出现黑边。

### Premultiplied Alpha

RGB 已经乘过 Alpha：

$$
C_o=C_s+(1-\alpha_s)C_d
$$

它更自然地表示 Coverage 边缘，也能统一普通透明和加法趋势。但源资源必须按线性值预乘。直接在 sRGB 编码值上预乘会得到错误结果。

## UI 在线性项目中为什么容易出问题

常见原因：

- UI 纹理 sRGB 标记错误；
- Shader 手动 Gamma 转换和硬件转换重复；
- Straight/Premultiplied Alpha 与 Blend State 不一致；
- UI 在 HDR/Tone Mapping 前绘制，被曝光和曲线改变；
- UI 在后处理后绘制，却仍使用场景颜色假设；
- RenderTexture 格式和颜色空间不一致。

排查时要画出完整链路，而不是只切换项目 Gamma/Linear 设置。

## HDR Buffer

场景线性光照可能远大于显示白色 1.0。HDR Render Target 使用浮点或高动态范围格式保存这些值，例如 `R11G11B10_FLOAT`、`RGBA16F`。

格式选择影响：

- 动态范围和精度；
- Alpha 是否存在；
- Blend/UAV 支持；
- 带宽和内存；
- 移动端 Tile/Attachment 成本。

## Exposure

曝光把场景亮度缩放到适合显示和 Tone Mapping 的范围：

$$
C_{exposed}=C_{scene}\cdot exposure
$$

摄影式工作流可能使用 EV100、光圈、快门和 ISO 推导曝光。

Auto Exposure 通常从亮度直方图或平均对数亮度估计目标，再按不同明暗适应速度平滑变化。直方图需要排除极端高亮和黑边，否则结果会被少数像素拉走。

## Pre-Exposure

有些引擎在写 HDR Buffer 前先乘上一帧曝光的倒数，让数值保持在更稳定范围，减少低精度 HDR 格式溢出。后处理和历史 Buffer 需要理解这个缩放，否则不同帧的值不能直接比较。

## 验证方法

- 用 0.5 灰色检查 sRGB 解码后的线性值，而不是期待仍为 0.5。
- 分别显示源纹理、采样后的 Linear RGB 和最终显示输出。
- 检查 Texture/Render Target 的真实 GPU Format 和 View。
- 使用透明渐变和有色边缘测试 Straight/Premultiplied。
- 固定曝光，再比较灯光和 Emissive 数值。
- 检查 TAA/历史 Buffer 是否已经 Pre-Exposed。

## 相关主题

- [[04_光照模型与PBR/PBR材质与能量守恒]]
- [[02_GPU与光栅化管线/剔除、透明与混合]]
- [[07_颜色与后处理/Tone Mapping、Bloom与屏幕效果]]
- [[14_性能分析与优化/渲染优化验证与移动端实践]]

## 参考资料

- IEC 61966-2-1, sRGB color space.
- Microsoft Learn, *Data Conversion Rules* for sRGB resources.
- Epic Games, *Auto Exposure* and *Pre-Exposure* documentation.
