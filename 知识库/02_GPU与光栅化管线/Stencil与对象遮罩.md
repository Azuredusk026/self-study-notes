# Stencil与对象遮罩

模板缓冲保存有限位宽的标签，通过比较和更新操作选择片元。位分配、读写掩码和深度失败操作共同决定实际遮罩。

## Stencil

Stencil Buffer 保存少量整数位。每个样本可以根据比较结果执行 Keep、Replace、Increment 等操作。

常见用途：

- 标记角色或区域，限制后处理；
- Light Volume 中限制灯光计算；
- Portal 和 Mask；
- 镜面、描边和特殊材质分类。

Stencil 很便宜，但位数有限。项目需要统一位分配，否则不同系统会互相覆盖。

### 用模板做对象分类

超出单个效果的用法是把模板当作全局的像素分类系统：几何阶段给每类对象写入约定的模板值，后续各 Pass 用模板测试筛选自己关心的像素。

这与在 Shader 内读取材质 ID 分支判断是两种不同层次的手段：

| | 模板测试 | Shader 内分类标记 |
|---|---|---|
| 决定的事 | 这个像素要不要进这个 Pass | 进来之后走哪个分支 |
| 执行时机 | 光栅化阶段，硬件完成 | 片元着色器内 |
| 成本 | 能提前执行模板测试时，可省去被拒绝样本的着色；时机受材质和 API 约束 | 需执行相应着色代码后判断 |

合理的分工是：模板做大类切分（天空、角色、场景），着色器内的分类标记做大类内部的细分（角色中的皮肤、头发、布料）。

### 位分配与数值顺序

模板通常只有 8 位，所有系统共享，因此位分配必须全局规划。一种常见结构是低位留给临时标记（如光体积），高位段编码对象大类。

数值的**排列顺序**可以用来减少比较次数。若角色、普通物体、地形依次取递增值，一次 `LessEqual` 比较配合适当的读掩码就能同时覆盖这三类，而把天空这类取更高值的对象排除在外：

```text
Character = 0x10
Lit       = 0x20
Terrain   = 0x30
Sky       = 0x80

readMask = 0xF0, reference = 0x30, compare = GreaterEqual
→ 一次比较命中全部三类 PBR 对象，排除天空
```

本例采用 OpenGL 比较语义：`reference op (stencil & readMask)`。`0x30 >= 0x10/0x20/0x30` 为真，`0x30 >= 0x80` 为假。零值仍满足比较，因此未标记样本需由其他条件排除，或使用精确分类判断。数值区间能减少比较，但分配方案会受排序约束。

### 位宽紧张下的取舍

8 位很快会不够用。一个真实的取舍案例是：皮肤原本占用独立的模板值，后来被合并进角色类别。

- **收益**：排除全部角色像素（贴花与投影必须排除角色）只需一次比较，而不是逐类比较；
- **代价**：无法单独用模板筛出皮肤像素，屏幕空间次表面散射这类需要精确圈定皮肤区域的效果失去了模板门控。

这个取舍成立的前提是目标平台本来也跑不动屏幕空间 SSS，皮肤的差异改由着色器内的分类标记处理，不增加 CPU 开销。换一个平台，结论可能完全相反。

这类决策应当连同理由一起记录。只看到最终的位分配表，后来者无法判断哪些位置可以调整、哪些是刻意为之。

### 模板描边的执行顺序

模板描边需要两次绘制同一对象。第一遍正常绘制并把可见样本的模板值写成 1；第二遍略微放大几何，只在模板值不等于 1 的位置输出描边颜色：

```cpp
glEnable(GL_STENCIL_TEST);
glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE);

glStencilMask(0xFF);
glStencilFunc(GL_ALWAYS, 1, 0xFF);
DrawObject(materialPass);

glStencilMask(0x00);
glStencilFunc(GL_NOTEQUAL, 1, 0xFF);
glDisable(GL_DEPTH_TEST);
DrawObject(outlinePass); // Vertex Shader 沿法线扩张位置

glEnable(GL_DEPTH_TEST);
glStencilMask(0xFF);
glStencilFunc(GL_ALWAYS, 0, 0xFF);
glDisable(GL_STENCIL_TEST);
```

输入是同一网格、正常材质 Pass 和扩张描边 Pass；输出写入当前颜色附件和共享 Depth/Stencil Attachment。第一遍的 `GL_REPLACE` 只应发生在通过所选测试的样本上。第二遍关闭模板写入，防止描边区域污染后续对象。

关闭深度测试能得到完整轮廓，也会让被遮挡部分透出来；保留深度测试可只显示可见轮廓。沿对象空间法线等比例扩张在非均匀缩放、尖角和远近透视下会宽度不稳，屏幕空间描边或背面膨胀需要单独处理。验证时清空模板为 0，并逐次查看两遍 Draw 的模板输入、模板输出和颜色输出。

## 验证方法

- 在捕获中分别查看模板输入、比较值和三种更新操作。
- 组合描边、贴花和角色分类，检查位写入不会互相覆盖。
- 为数值区间比较枚举全部类别，确认天空和未标记像素被正确处理。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[02_GPU与光栅化管线/剔除、透明与混合]]
- [[06_纹理技术/纹理采样与过滤]]
- [[14_性能分析与优化/帧瓶颈怎么判断]]
- [[13_渲染架构/Draw Call与合批]]
- [[13_渲染架构/GBuffer布局]]

- [[02_GPU与光栅化管线/光栅化、插值与深度模板]]

## 参考资料

- Microsoft Learn, *Depth-Stencil Functionality*.
- Khronos, *Vulkan Specification*, Rasterization and Fragment Operations.
- Emil Persson, *Creating Vast Game Worlds* and reversed-Z references collected by NVIDIA.
- Nathan Reed, *Depth Precision Visualized*, NVIDIA Developer Blog.
- Unity Manual, *Platform-specific rendering differences* and URP Depth Priming documentation.
- Unity Technologies, URP `CanCopyDepth` implementation in the Universal Render Pipeline package.
