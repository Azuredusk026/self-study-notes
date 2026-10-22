# Stencil与对象遮罩

一个遮罩效果单独运行正常，和别的效果组合以后却把对象裁掉，先看它们是否改写了同一模板位。Stencil保存有限标签，比较和写入规则共同决定像素能否通过。把位分配、深度失败操作和清理时机对应起来，才能解释多对象与多效果的覆盖。

## Stencil

Stencil Buffer 保存少量整数位。每个样本可以根据比较结果执行 Keep、Replace、Increment 等操作。

常见用途：

- 标记角色或区域，限制后处理；
- Light Volume 中限制灯光计算；
- Portal 和 Mask；
- 镜面、描边和特殊材质分类。

Stencil可在允许提前测试的条件下减少着色，但附件访问与状态仍有成本，位数也有限。项目需要统一位分配，否则不同系统会互相覆盖。

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

数值的**排列顺序**可以用来减少比较次数。若角色、普通物体、地形依次取递增值，一次 `GreaterEqual` 比较配合适当的读掩码就能同时覆盖这三类，而把天空这类取更高值的对象排除在外：

```text
Character = 0x10
Lit       = 0x20
Terrain   = 0x30
Sky       = 0x80

readMask = 0xF0, reference = 0x30, compare = GreaterEqual
→ 一次比较命中全部三类 PBR 对象，排除天空
```

本例采用 OpenGL 比较语义：`(reference & readMask) op (stencil & readMask)`。`0x30 >= 0x10/0x20/0x30` 为真，`0x30 >= 0x80` 为假。零值仍满足比较，因此未标记样本需由其他条件排除，或使用精确分类判断。数值区间能减少比较，但分配方案会受排序约束。

### 位宽紧张下的取舍

假设高4位保存对象大类，低4位由局部效果使用。把皮肤归入角色大类后，贴花可一次排除全部角色；需要单独处理皮肤的通道则读取材质分类缓冲。这个分工要求皮肤识别数据在消费时仍可访问，节省的模板位也必须足以抵消额外数据读取。

写掩码控制更新哪些位。设操作结果为 $v$，原值为 $s$，8位写掩码为 $m$，最终值是 $(s\mathbin{\&}\sim m)\mathbin{|}(v\mathbin{\&}m)$。例如原值0x15、Replace值0x20、写掩码0xF0，结果为0x25；低4位的0x5保留下来。

模板失败时执行 `sfail`；模板通过但深度失败时执行 `dpfail`；两者都通过时执行 `dppass`。选中Replace分支后仍受写掩码约束。对象分类通常只在深度通过时写入，否则后方对象会覆盖前方表面的类别。

### 模板描边的执行顺序

模板描边需要两次绘制同一对象。第一遍正常绘制并把可见样本的模板值写成 1；第二遍略微放大几何，只在模板值不等于 1 的位置输出描边颜色：

```cpp
// 独立演示通道独占8位模板；FBO已具备模板附件；关闭Scissor以清理整个附件
glDisable(GL_SCISSOR_TEST);
glStencilMask(0xFF);
glClearStencil(0);
glClear(GL_STENCIL_BUFFER_BIT);
glEnable(GL_DEPTH_TEST);
glDepthMask(GL_TRUE);
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

该C++片段要求当前有效OpenGL上下文、已绑定FBO和着色程序；`DrawObject`封装网格绑定与绘制。演示通道使用已知初始状态，并在退出后由下一通道重新设置状态。共享模板附件时按位分配清理，不能照搬全位清空。输入是同一网格、正常材质 Pass 和扩张描边 Pass；输出写入当前颜色附件和共享 Depth/Stencil Attachment。第一遍的 `GL_REPLACE` 只应发生在通过所选测试的样本上。第二遍关闭模板写入，防止描边区域污染后续对象。

第二遍关闭深度测试时，所有未标成1的扩张样本都能着色。第一遍只标记可见部分，所以遮挡区域的原物体内部也保留0；第二遍会把这部分填满，不能保证只得到透视遮挡后的外轮廓。要让描边服从场景遮挡，可在第二遍保留深度测试。要得到完整物体轮廓的透视显示，则先单独绘制原网格的完整模板遮罩，关闭颜色写入与深度测试，再以扩张形状减去这份遮罩。

沿对象空间法线扩张在非均匀缩放、尖角和远近透视下会宽度不稳，扩张计算见[[11_NPR与风格化渲染/描边]]。验证时放一面墙遮住对象中部，逐次查看两遍 Draw 的模板输入、模板输出和颜色输出：遮挡内区是否着色可以直接区分“扩张形状填充”与“轮廓线”。

## 验证方法

- 在捕获中分别查看模板输入、比较值和三种更新操作。
- 组合描边、贴花和角色分类，检查位写入不会互相覆盖。
- 为数值区间比较枚举全部类别，确认天空和未标记像素被正确处理。

## 相关主题

- [[02_GPU与光栅化管线/渲染帧流程]]
- [[02_GPU与光栅化管线/可见性与合成]]
- [[06_纹理技术/纹理采样与过滤]]
- [[14_性能分析与优化/帧瓶颈诊断]]
- [[13_渲染架构/Draw Call与合批]]
- [[13_渲染架构/GBuffer布局]]

- [[02_GPU与光栅化管线/光栅化可见性]]

实现与验证：[raster_models.py](../examples/revision/raster_models.py) 与 [test_raster.py](../examples/revision/test_raster.py)枚举256个原值检查写掩码隔离，并核对分类比较结果，运行 `python -B 知识库/examples/revision/test_raster.py`。OpenGL上下文与两遍描边未运行；模板图像需用目标工程捕获。

## 参考资料

- [Khronos glStencilFunc规范源文件](https://github.com/KhronosGroup/OpenGL-Refpages/blob/main/gl4/glStencilFunc.xml)：2026-10-22核读mask参数与GL_GEQUAL条目，两边均先应用读掩码。
- [Khronos glStencilOp规范源文件](https://github.com/KhronosGroup/OpenGL-Refpages/blob/main/gl4/glStencilOp.xml)：2026-10-22核读sfail、dpfail、dppass和Replace定义。关闭深度测试时，模板通过也进入dppass分支。
