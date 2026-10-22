# Stream Output

有时顶点结果还要用于下一次模拟或绘制，无需立即光栅化。Stream Output把选定阶段输出按声明写进缓冲，后续再作为输入。接口声明、输出容量与图元顺序共同决定这份缓存能否正确复用。

## 流输出声明

几何阶段的输出默认只能继续进入光栅化。如果想要的只是“处理后的顶点流”——供后续绘制、粒子状态更新或调试——其他路径可以在Compute中写缓冲，或者用CPU处理；Stream Output提供图形前端结果的直接捕获。

流输出（Direct3D 称 Stream Output，OpenGL 称 Transform Feedback）提供直接路径：声明要捕获的输出语义与写入布局，顶点处理结果按序写入缓冲区。在 D3D11 中，启用 Geometry Shader 时捕获其输出；省略 Geometry Shader 时可捕获 Vertex Shader 的输出。捕获本身不要求程序生成新图元。

Direct3D 用声明表描述捕获项：

```cpp
D3D11_SO_DECLARATION_ENTRY decl[] = {
    { 0, "SV_POSITION", 0, 0, 4, 0 },   // 流编号, 语义名, 索引, 起始分量, 分量数, 输出槽
    { 0, "NORMAL",      0, 0, 3, 0 },
    { 0, "TEXCOORD",    0, 0, 2, 0 },
};
```

本例捕获4+3+2个32位分量，每条记录为36字节。创建Geometry Shader的流输出声明时，输出槽0的stride应为36；复用为顶点输入时，位置、法线和UV的偏移依次为0、16、28字节。声明描述的是选中字段的输出布局，不能直接采用含额外填充的CPU结构体大小。

OpenGL 用 `glTransformFeedbackVaryings` 在链接程序前指定变量名列表，配合 `GL_INTERLEAVED_ATTRIBS`（交错写入同一缓冲）或 `GL_SEPARATE_ATTRIBS`（分缓冲写入）。支持 OpenGL 4.4 或 `ARB_enhanced_layouts` 扩展时，GLSL 还可用 `xfb_buffer`、`xfb_offset`、`xfb_stride` 布局限定符描述写入布局；接入时先核对版本与扩展。

### 输出数量与顺序

D3D11流输出把条带展开为列表，只写完整图元。四顶点三角形带构成两个三角形，捕获结果是六条顶点记录，而不是四条；据此分配前述布局的缓冲需要216字节。把输入顶点数直接当作输出计数，会低估容量。

可变数量输出同时带来容量和调度问题。原子追加可以分配唯一位置，但完成顺序不等于输入顺序；需要稳定顺序的计算方案可先记录每项数量，再做前缀和分配连续区间。这个算法比较说明了顺序要求带来的额外工作，实际流输出硬件采用何种缓冲和调度方式仍需对应架构资料或计数器支持。

捕获结果只用于下次绘制时，D3D11的`DrawAuto`可消费记录的输出数量，避免CPU回读计数。输出缓冲按`D3D11_BIND_STREAM_OUTPUT`创建，作为顶点输入时还需相应绑定标志。取消输出绑定后再把它用作输入；D3D12的显式资源状态转换属于另一套接口契约。

## 输出契约

下面是Direct3D风格的机制伪代码，具体字段按目标API建立。目标缓冲有固定stride与容量，资源必须支持输出及后续输入用途。

```text
declaration = [(stream=0, semantic=POSITION, components=3)]
stride = 12
bindStreamOutput(buffer, offset=0)
draw(inputGeometry)
unbindStreamOutput()
transitionForNextConsumer(buffer)
bindVertexInput(buffer, stride)
drawCapturedGeometry()
```

计数与容量必须配套，输出溢出不能当作完整结果。Direct3D的Stream Output与OpenGL Transform Feedback有不同绑定及计数接口；按目标版本核对，不跨API复制对象名称。

对两个三角形的带输入，先按前述声明分配至少216字节输出缓冲，并将其绑定到SO槽0。绘制后取消SO目标绑定，再以36字节stride绑定顶点输入；顶点布局三个字段偏移为0、16、28。`DrawAuto`使用流输出记录的顶点计数，调用端不再把原输入的4误传成输出顶点数。

若只有144字节容量，容量只够四条记录，而条带展开需要六条。不能把缓冲里已有部分记录当作完整几何成功；运行时应结合SO统计查询和容量策略决定重试或拒绝。显式API路径另建立状态依赖，本段的D3D11取消绑定并不是一个可跨后端照搬的transition函数。

## 验证方法

用三个已知位置捕获结果并检查stride、元素数与顺序。把缓冲作为下一次顶点输入，对比直接绘制；读回只在GPU复制完成后进行。测试输出容量不足和多流绑定。

实现状态：D3D11声明和输出流程是宿主片段，36字节stride及条带六记录可按字段数复算。未创建D3D设备或执行捕获；运行验收需检查SO统计、容量不足行为和读回记录。

## 相关主题

- [[02_GPU与光栅化管线/Geometry Shader]]
- [[13_渲染架构/GPU资源生命周期]]

## 参考资料

- [Khronos ARB_enhanced_layouts](https://github.com/KhronosGroup/OpenGL-Registry/blob/main/extensions/ARB/ARB_enhanced_layouts.txt)：2026-10-22核读Overview第5项及Transform Feedback布局条款；显式xfb限定符的能力范围与字节偏移定义。
- [Microsoft Stream-Output Stage](https://learn.microsoft.com/en-us/windows/win32/direct3d11/d3d10-graphics-programming-guide-output-stream-stage)：2026-10-22核读条带转列表、完整图元写入、DrawAuto与绑定要求。
- [D3D11_SO_DECLARATION_ENTRY](https://learn.microsoft.com/en-us/windows/win32/api/d3d11/ns-d3d11-d3d11_so_declaration_entry)：声明字段顺序，既有2026-10-07核读记录。
