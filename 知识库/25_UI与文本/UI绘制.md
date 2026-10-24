# UI绘制

滚动一个列表，不必重建所有静态控件。UI绘制从布局失效范围生成矩形、裁剪和绘制命令，再按层级与兼容状态合批。输入命中使用同一布局，避免画面位置和可点击区域分离。

## 控件树与绘制列表

保留模式 UI 通常保存一棵控件树。布局阶段根据 Anchor、Size、Padding、字体和父节点约束计算最终矩形，再生成按层级排序的绘制命令。

即时模式 UI 每帧根据调用序列生成界面状态和绘制数据。两种模式最终都需要处理：

- 屏幕或世界空间坐标；
- Z Order 和层级裁剪；
- 纹理、字体和材质批次；
- 输入命中区域；
- DPI、分辨率和安全区。

布局和渲染可以分开更新。文本或尺寸不变时，缓存布局和网格能减少 CPU 工作；父级尺寸、字体回退或本地化内容变化时，需要让相关子树失效并重新排版。

## 控件提交与裁剪

### 裁剪、遮罩和九宫格

矩形裁剪适合使用Scissor，限制附件中允许产生覆盖的像素范围；它不减少已经提交的顶点工作。复杂圆角或任意形状可以使用 Stencil、Mask Texture 或 Shader Clip。

嵌套 Mask 需要维护层级和 Stencil 值。Stencil 位数有限，深层嵌套需要回退策略。频繁改变 Scissor、Stencil 和材质也会打断批次。

九宫格把矩形分成四角、四边和中心。设源图宽100、左右边框各20，目标宽160，横向位置为`[0,20,140,160]`，对应源图UV为`[0,0.2,0.8,1]`；纵轴同样分四个位置，再生成九个矩形。角的像素尺寸保持20，中心由60拉伸成120。若目标宽只有30，边框总宽40已经放不下：一种明确策略是按30/40等比收缩左右边框到15，中心宽度归零。直接继续使用20会产生倒置的中心四边形。选择保持角尺寸并允许溢出也是另一种布局策略，必须与裁剪及命中范围一致。

### 有效裁剪与命中

父裁剪区域为`[0,0,100,80)`，子控件请求`[30,-10,150,20)`时，实际可绘制区域是交集`[30,0,100,20)`。区间使用左闭右开，边界相接但没有面积时直接跳过绘制。以下为显示像素坐标的机制伪代码：

```text
clip.left   = max(parent.left, child.left)
clip.top    = max(parent.top, child.top)
clip.right  = min(parent.right, child.right)
clip.bottom = min(parent.bottom, child.bottom)
if clip.left >= clip.right or clip.top >= clip.bottom: skip
```

输入命中也使用这个有效区域。否则滚出窗口的按钮虽然被Scissor挡住，仍可能收到点击。旋转控件先把输入点变换到局部空间，矩形Scissor只负责屏幕上的保守范围，精确形状由局部命中与遮罩判定。

### 批处理和网格生成

普通字形可以用四个顶点、六个索引表示。CPU 先把同一图集页、材质、裁剪状态和层级范围内的 Quad 写入动态 Buffer，再成批提交。

常见打断条件包括：

- 图集页或纹理改变；
- Blend、Stencil、Scissor 改变；
- 自定义材质或 Shader Variant；
- Z Order 要求穿插；
- 世界空间 UI 需要不同深度状态。

使用一个超大动态网格也有更新和上传成本。实践中按失效区域、Canvas 或绘制层级拆分，使静态部分能够缓存，动态数字和滚动列表只更新必要 Buffer。

绘制列表按画家顺序生成后，仅合并相邻且状态兼容的命令。状态键包括纹理页、Shader与材质参数、混合状态、裁剪区域、模板引用及深度状态。半透明A、B、A三条命令，即使两条A使用同一纹理，也不能跨过B直接合为一批，否则重叠处颜色会改变。

```text
for command in paintOrder:
    key = (texture, material, blend, scissor, stencil, depth)
    if currentBatch.key == key and buffersHaveCapacity:
        append vertices and rebased indices
    else:
        flush currentBatch
        begin batch with key
        append vertices and rebased indices
flush currentBatch
```

动态索引还要叠加当前批次顶点基址。16位索引接近上限时拆批，或者使用受后端支持的32位索引；仅检查状态相同不能保证缓冲合法。临时顶点和索引区间在GPU完成读取之前保持有效，下一帧上传使用环形区间与完成值控制复用。

DPI缩放在布局单位到帧缓冲像素的转换处执行一次。OpenGL常见Scissor原点在左下，需要用`framebufferHeight-bottom`转换y；其他后端按自身约定设置。缩放两次会让裁剪随着DPI偏移，漏减窗口原点则会在多视口时出错。

### 高 DPI、本地化和输入

DPI 缩放应作用于布局单位，再映射到物理像素。文字基线和细线在最终像素网格上的位置会影响清晰度。动态分辨率只改变 3D 渲染时，屏幕 UI 通常保持显示分辨率。

本地化会改变文本长度、换行、阅读方向和字体回退。布局需要支持：

- CJK 自动换行和禁则；
- 从右到左文本与双向混排；
- 复数、数字和日期格式；
- 字体缺字与语言专用字体；
- 输入法组合文本、光标和选区。

命中测试应使用布局后的控件区域。旋转或世界空间 UI 需要把输入射线转换到对应局部空间，再按裁剪区域和层级判断目标。

## 验证方法

显示布局、裁剪与命中矩形，测试DPI、旋转、嵌套遮罩和长本地化文本。记录Batch Break、动态顶点上传和Overdraw，只在状态与层级兼容时合并。文字排版和字形纹理见独立专篇。

## 参考实验与证据

[CPU参考模型](../examples/revision_22_26/reference.py)检查嵌套裁剪交集、空交集、相邻合批和A/B/A保序。2026-10-22执行`python 知识库/examples/revision_22_26/test_reference.py`，21项通过，其中4项属于本页。完整布局引擎、命中处理、GPU缓冲上传和实际绘制尚未验证。

## 相关主题

- [[25_UI与文本/文字渲染]]
- [[13_渲染架构/Draw Call与合批]]

## 参考资料

- Dear ImGui [v1.91.9b OpenGL后端](https://github.com/ocornut/imgui/blob/v1.91.9b/backends/imgui_impl_opengl3.cpp)，`ImGui_ImplOpenGL3_RenderDrawData`中的裁剪坐标转换、空矩形检查、纹理绑定与索引偏移；2026-10-22核读。该源码说明一种真实后端，不代表所有UI框架使用相同布局模型。
- 本页半透明保序与状态兼容关系见[[13_渲染架构/Draw Call与合批]]，字形塑形与图集见[[25_UI与文本/文字渲染]]。
