# UI绘制

滚动一个列表，不必重建所有静态控件。UI绘制从布局失效范围生成矩形、裁剪和绘制命令，再按层级与兼容状态合批。输入命中使用同一布局，避免画面位置和可点击区域分离。

## 从 UI 树到绘制列表

保留模式 UI 通常保存一棵控件树。布局阶段根据 Anchor、Size、Padding、字体和父节点约束计算最终矩形，再生成按层级排序的绘制命令。

即时模式 UI 每帧根据调用序列生成界面状态和绘制数据。两种模式最终都需要处理：

- 屏幕或世界空间坐标；
- Z Order 和层级裁剪；
- 纹理、字体和材质批次；
- 输入命中区域；
- DPI、分辨率和安全区。

布局和渲染可以分开更新。文本或尺寸不变时，缓存布局和网格能减少 CPU 工作；父级尺寸、字体回退或本地化内容变化时，需要让相关子树失效并重新排版。

## 控件怎样提交到屏幕

### 裁剪、遮罩和九宫格

矩形裁剪适合使用 Scissor，能在光栅化前限制区域。复杂圆角或任意形状可以使用 Stencil、Mask Texture 或 Shader Clip。

嵌套 Mask 需要维护层级和 Stencil 值。Stencil 位数有限，深层嵌套需要回退策略。频繁改变 Scissor、Stencil 和材质也会打断批次。

九宫格把矩形分成四角、四边和中心。角保持尺寸，边沿单轴拉伸，中心双轴拉伸。它让同一纹理适配不同控件尺寸，同时需要正确处理 Border 超过目标尺寸的情况。

### 批处理和网格生成

普通字形可以用四个顶点、六个索引表示。CPU 先把同一 Atlas Page、材质、裁剪状态和层级范围内的 Quad 写入动态 Buffer，再成批提交。

常见打断条件包括：

- Atlas Page 或纹理改变；
- Blend、Stencil、Scissor 改变；
- 自定义材质或 Shader Variant；
- Z Order 要求穿插；
- 世界空间 UI 需要不同深度状态。

使用一个超大动态网格也有更新和上传成本。实践中按失效区域、Canvas 或绘制层级拆分，使静态部分能够缓存，动态数字和滚动列表只更新必要 Buffer。

### 高 DPI、本地化和输入

DPI 缩放应作用于布局单位，再映射到物理像素。文字基线和细线在最终像素网格上的位置会影响清晰度。动态分辨率只改变 3D 渲染时，屏幕 UI 通常保持显示分辨率。

本地化会改变文本长度、换行、阅读方向和字体回退。布局需要支持：

- CJK 自动换行和禁则；
- 从右到左文本与双向混排；
- 复数、数字和日期格式；
- 字体缺字与语言专用字体；
- 输入法组合文本、光标和选区。

命中测试应使用布局后的控件区域。旋转或世界空间 UI 需要把输入射线转换到对应局部空间，再按裁剪区域和层级判断目标。

## 绘制列表

以下为CPU伪代码，矩形与裁剪使用显示像素坐标，世界空间UI另执行投影与深度规则。

```text
layout = ResolveDirtySubtree(root, displaySize)
commands = TraverseInPaintOrder(layout)
for command in commands:
    if CompatibleWithCurrentBatch(command): AppendQuad(command)
    else: FlushBatchAndBegin(command)
```

## 验证方法

显示布局、裁剪与命中矩形，测试DPI、旋转、嵌套遮罩和长本地化文本。记录Batch Break、动态顶点上传和Overdraw，只在状态与层级兼容时合并。文字排版和字形纹理见独立专篇。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[25_UI与文本/文字渲染]]
- [[13_渲染架构/Draw Call与合批]]

## 参考资料

- LearnOpenGL, `src/7.in_practice/2.text_rendering`.
- FreeType Documentation, *Glyph Conventions*.
- HarfBuzz Documentation, *Shaping Concepts*.
- Viktor Chlumský, *Multi-channel Signed Distance Field*.
