# Alpha表示

透明边缘出现黑线，常是RGB填充、预乘方式和Blend State不一致。Alpha可以是覆盖，也可以是项目数据，首先要确定含义。Straight与Premultiplied保存颜色的方式不同，过滤与合成必须沿同一表示。

## 覆盖与合成

### Alpha 通道怎么处理

sRGB 格式的非线性转换通常只作用于 RGB，Alpha 保持线性数值。Alpha 可能代表：

- Coverage/Opacity；
- Mask；
- Smoothness；
- 其他项目数据。

因此一张 Base Color 的 RGB 可以按 sRGB 解码，Alpha 仍作为线性 Mask 使用。

> [!warning] 不要靠猜
> 纹理文件本身不会保证 Alpha 的语义。导入器、压缩格式和 Shader 约定需要一致。

### Alpha Blend 应在线性空间进行

如果 RGB 仍在 sRGB 编码空间就做混合，中间颜色会偏暗。正确过程是先解码 RGB 到 Linear，在线性 Render Target 上混合，最终显示时再编码。

硬件对 sRGB Render Target 可以在写入时自动编码，对 sRGB Texture 可以在采样时自动解码。是否发生转换由资源格式和 View 决定，不是 Shader 变量名决定。

### 两种颜色表示

完整混合方程与排序见 [[02_GPU与光栅化管线/透明合成]]。本页关注制作与过滤，防止RGB与覆盖数据采用不一致的表示。

#### Straight Alpha

RGB 保存未乘 Alpha 的原始颜色。常见混合：



透明像素中的 RGB 仍会参与纹理过滤。如果边缘外填充为黑色，可能出现黑边。

#### Premultiplied Alpha

RGB 已经乘过 Alpha：



它更自然地表示 Coverage 边缘，也能统一普通透明和加法趋势。但源资源必须按线性值预乘。直接在 sRGB 编码值上预乘会得到错误结果。

### UI 在线性项目中为什么容易出问题

常见原因：

- UI 纹理 sRGB 标记错误；
- Shader 手动 Gamma 转换和硬件转换重复；
- Straight/Premultiplied Alpha 与 Blend State 不一致；
- UI 在 HDR/Tone Mapping 前绘制，被曝光和曲线改变；
- UI 在后处理后绘制，却仍使用场景颜色假设；
- RenderTexture 格式和颜色空间不一致。

排查时要画出完整链路，而不是只切换项目 Gamma/Linear 设置。

## 验证方法

用有色边缘和零Alpha像素比较过滤，再检查Shader输出与blend因子。预乘在线性RGB进行，RGB编码与Alpha数值转换分开。透明层排序与OIT由透明合成说明。

## 相关主题

- [[02_GPU与光栅化管线/透明合成]]
- [[25_UI与文本/文字渲染]]
- [[07_颜色与后处理/颜色空间]]
- [[07_颜色与后处理/HDR与曝光]]

## 参考资料

- IEC 61966-2-1, sRGB color space.
- Microsoft Learn, *Data Conversion Rules* for sRGB resources.
- Epic Games, *Auto Exposure* and *Pre-Exposure* documentation.
