# UI、字体与文本渲染

UI 渲染把布局结果转换成可批量提交的矩形、字形、图标和裁剪命令。文字还要经过 Unicode、字体选择和字形排版，不能把字符串中的每个字符直接当成一张固定图片。

## 从 UI 树到绘制列表

保留模式 UI 通常保存一棵控件树。布局阶段根据 Anchor、Size、Padding、字体和父节点约束计算最终矩形，再生成按层级排序的绘制命令。

即时模式 UI 每帧根据调用序列生成界面状态和绘制数据。两种模式最终都需要处理：

- 屏幕或世界空间坐标；
- Z Order 和层级裁剪；
- 纹理、字体和材质批次；
- 输入命中区域；
- DPI、分辨率和安全区。

布局和渲染可以分开更新。文本或尺寸不变时，缓存布局和网格能减少 CPU 工作；父级尺寸、字体回退或本地化内容变化时，需要让相关子树失效并重新排版。

## 字符、码点和字形

- 字符是读者理解的文字单位。
- Unicode 码点是字符编码空间中的编号。
- 字形（Glyph）是字体中实际绘制的形状。
- 字形 ID 是某个字体文件内部的索引。

一个码点可能对应多个字形，一个字形也可能由多个码点共同产生。连字、阿拉伯文连接形式、组合附加符号、Emoji 序列都需要文本塑形（Text Shaping）。

可靠流程是：

```text
Unicode Text
  → 双向与脚本分析
  → 字体回退
  → Text Shaping
  → Glyph ID、Advance 和 Offset
  → 换行与对齐
  → Glyph Quad / Path
```

FreeType 负责读取字体和栅格化字形。HarfBuzz 等塑形库根据脚本规则、Kerning 和字体特性生成字形序列。只按码点查询 FreeType 可以完成简单拉丁文本，无法覆盖完整国际化排版。

## 字形度量

每个字形常见度量包括：

- Advance：绘制后光标前进距离；
- Bearing：字形位图相对基线和光标的偏移；
- Width/Height：字形图像范围；
- Ascender/Descender：基线上下的字体范围；
- Line Gap：推荐行间距。

字形 Quad 的左上角不能只使用当前光标位置。它需要结合 Bearing 和 Baseline。连续字形的位置由塑形结果中的 Advance 与 Offset 累积，不应自己再重复应用一遍 Kerning。

## 位图字体和 Glyph Atlas

最直接的方法是把字形栅格化成 Alpha Mask，再把许多字形放进 Glyph Atlas。每个字形记录 Atlas UV、像素尺寸、Bearing 和 Advance。

Atlas 能让多个字形共享纹理绑定并进入同一批次，但要处理：

- 字形边缘 Padding，避免双线性过滤串色；
- 动态加入新字形时的空间分配；
- Atlas 满后的淘汰、扩容或分页；
- 不同字号、Hinting 和语言字符集；
- Atlas 更新期间的资源同步；
- Mipmap 对小字边缘的影响。

CJK 字符集很大，通常按实际使用字形动态缓存，或按语言资源预烘焙多个 Atlas Page。运行时缺字需要显示明确的替代字形，并记录缺失字体和码点。

## SDF 和 MSDF

符号距离场（Signed Distance Field，SDF）保存采样点到字形边界的带符号距离。下面的示例把零距离映射到 `0.5`，字形内部映射到更大的值。Shader 在这条等值线附近恢复覆盖率，因此同一张 Atlas 可以覆盖更大的缩放范围。

```hlsl
float GlyphAlpha(float2 uv)
{
    float distance = GlyphAtlas.Sample(LinearClamp, uv).r;
    float smoothing = max(fwidth(distance) * SdfSoftness, 1e-4);
    return smoothstep(0.5 - smoothing,
                      0.5 + smoothing,
                      distance);
}
```

`fwidth` 根据屏幕导数调整过渡宽度，使缩放时边缘保持接近一个像素。若生成器使用相反的距离符号，`smoothstep` 的方向也要反转。SDF 分辨率、Distance Range 和生成时的归一化方式必须与 Shader 中的阈值一致。

普通单通道 SDF 在尖角处容易变圆。MSDF 把不同边的距离编码到 RGB，通过中值恢复距离，能保留更多尖锐转角。它仍需要正确的边着色、Padding 和采样范围。

极小字号更依赖 Hinting 和像素对齐，位图字形可能比 SDF 清晰。超大标题、描边和发光适合 SDF/MSDF。一个项目可以按字号和平台组合使用。

## 颜色和混合

字形 Atlas 通常提供 Coverage，文字颜色来自顶点或常量。使用预乘 Alpha 时：

$$
C_{src}=C_{text}\alpha
$$

Blend State 使用 `One, OneMinusSrcAlpha`。Atlas Coverage 属于线性覆盖数据，采样时不做 sRGB 解码；文字颜色则需要遵守 UI 颜色空间和最终显示变换。

LCD Subpixel Rendering 依赖显示器子像素排列和最终合成位置。旋转、缩放、HDR 合成和不同面板都会破坏假设，因此游戏 UI 常使用灰度抗锯齿。

## 裁剪、遮罩和九宫格

矩形裁剪适合使用 Scissor，能在光栅化前限制区域。复杂圆角或任意形状可以使用 Stencil、Mask Texture 或 Shader Clip。

嵌套 Mask 需要维护层级和 Stencil 值。Stencil 位数有限，深层嵌套需要回退策略。频繁改变 Scissor、Stencil 和材质也会打断批次。

九宫格把矩形分成四角、四边和中心。角保持尺寸，边沿单轴拉伸，中心双轴拉伸。它让同一纹理适配不同控件尺寸，同时需要正确处理 Border 超过目标尺寸的情况。

## 批处理和网格生成

普通字形可以用四个顶点、六个索引表示。CPU 先把同一 Atlas Page、材质、裁剪状态和层级范围内的 Quad 写入动态 Buffer，再成批提交。

常见打断条件包括：

- Atlas Page 或纹理改变；
- Blend、Stencil、Scissor 改变；
- 自定义材质或 Shader Variant；
- Z Order 要求穿插；
- 世界空间 UI 需要不同深度状态。

使用一个超大动态网格也有更新和上传成本。实践中按失效区域、Canvas 或绘制层级拆分，使静态部分能够缓存，动态数字和滚动列表只更新必要 Buffer。

## 高 DPI、本地化和输入

DPI 缩放应作用于布局单位，再映射到物理像素。文字基线和细线在最终像素网格上的位置会影响清晰度。动态分辨率只改变 3D 渲染时，屏幕 UI 通常保持显示分辨率。

本地化会改变文本长度、换行、阅读方向和字体回退。布局需要支持：

- CJK 自动换行和禁则；
- 从右到左文本与双向混排；
- 复数、数字和日期格式；
- 字体缺字与语言专用字体；
- 输入法组合文本、光标和选区。

命中测试应使用布局后的控件区域。旋转或世界空间 UI 需要把输入射线转换到对应局部空间，再按裁剪区域和层级判断目标。

## 验证方法

- 显示 Baseline、Bearing、Advance 和 Glyph Bounds。
- 测试拉丁、CJK、阿拉伯文、组合附加符号和 Emoji 序列。
- 放大 Atlas 检查 Padding、串色和缺字。
- 在不同 DPI、窗口比例和语言下检查换行与裁剪。
- 查看 UI Draw、Batch Break、动态顶点上传量和 Overdraw。
- 分别测试位图、SDF 和 MSDF 在小字号、旋转和缩放下的边缘。
- 检查预乘 Alpha、线性颜色与 HDR UI 合成顺序。

## 相关主题

- [[02_GPU与光栅化管线/剔除、透明与混合]]
- [[06_纹理技术/纹理采样、过滤、Mipmap与压缩]]
- [[06_纹理技术/UV、图集、流送与虚拟纹理]]
- [[13_引擎架构与资源系统/Draw Call、Batching与GPU Instancing]]
- [[15_资产与工具管线/资产导入、验证与发布]]

## 参考资料

- LearnOpenGL, `src/7.in_practice/2.text_rendering`.
- FreeType Documentation, *Glyph Conventions*.
- HarfBuzz Documentation, *Shaping Concepts*.
- Viktor Chlumský, *Multi-channel Signed Distance Field*.
