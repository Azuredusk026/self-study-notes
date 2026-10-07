# Stream Output

有时顶点结果还要用于下一次模拟或绘制，无需立即光栅化。Stream Output把选定阶段输出按声明写进缓冲，后续再作为输入。接口声明、输出容量与图元顺序共同决定这份缓存能否正确复用。

## 流输出：把几何结果存下来

几何阶段的输出默认只能继续进入光栅化。如果想要的只是“处理后的顶点流”——供后续绘制、粒子状态更新或调试——其他路径可以在Compute中写缓冲，或者用CPU处理；Stream Output提供图形前端结果的直接捕获。

流输出（Direct3D 称 Stream Output，OpenGL 称 Transform Feedback）提供直接路径：声明要捕获的输出语义与写入布局，几何阶段结束后顶点属性按序写入缓冲区。

Direct3D 用声明表描述捕获项：

```cpp
D3D11_SO_DECLARATION_ENTRY decl[] = {
    { 0, "SV_POSITION", 0, 0, 4, 0 },   // 语义名, 索引, 起始分量, 分量数, 输出槽
    { 0, "NORMAL",      0, 0, 3, 0 },
    { 0, "TEXCOORD",    0, 0, 2, 0 },
};
```

OpenGL 用 `glTransformFeedbackVaryings` 指定变量名列表，配合 `GL_INTERLEAVED_ATTRIBS`（交错写入同一缓冲）或 `GL_SEPARATE_ATTRIBS`（分缓冲写入）；GLSL 还可以用 `xfb_buffer`、`xfb_offset`、`xfb_stride` 布局限定符直接描述写入布局。

### 顺序约束的代价

流输出的昂贵不在“多写一份”，而在**顺序**。图形 API 功能规范要求：无论内部如何并行调度，具体顺序保证按API、图元与捕获模式核对，不能从一个API推断所有后端。

一旦引入几何着色器或曲面细分，每个输入图元输出的顶点数可变，并行完成次序不可预测，顺序保证就从免费变成结构性成本：

- **原子追加**可分配唯一位置，但并行线程完成次序不等于输入顺序，单独使用不能满足有序捕获；
- **两阶段写入**：先算每个图元的输出大小，再做前缀和求偏移，最后并行写入——高效但复杂，这已经接近“用计算着色器手写几何管线”的形态；
- **粗粒度序列化**：实现简单，吞吐损失明显。

流输出把并行友好的散写问题变成了要求顺序稳定的队列问题，强迫并行机器在某处排队。这也是它看似是通用 GPGPU 的早期入口、却没有成为通用计算主路径的原因——计算着色器从一开始就按显式并行、显式同步组织，不背图形管线的顺序包袱。

流输出的现代角色是保守的：调试与可视化、小规模几何捕获、个别沿用至今的粒子更新。面对通用的生成、压缩、排序需求，实践上转向计算着色器加显式缓冲，顺序与压缩策略自行管理。

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

## 验证方法

用三个已知位置捕获结果并检查stride、元素数与顺序。把缓冲作为下一次顶点输入，对比直接绘制；读回只在GPU复制完成后进行。测试输出容量不足和多流绑定。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[02_GPU与光栅化管线/Geometry Shader]]
- [[13_渲染架构/GPU资源生命周期]]

## 参考资料

- Frank Luna, *Introduction to 3D Game Programming with DirectX 12*, Tessellation and Geometry Shader chapters.
- Khronos OpenGL Wiki, *Tessellation*, *Tessellation Control Shader*, *Tessellation Evaluation Shader*, *Transform Feedback*.
- Microsoft Learn, *Geometry-Shader Stage*, *Primitive Topologies*, *Getting Started with the Stream-Output Stage*.
- Microsoft, *Direct3D 11.3 Functional Specification*, Tessellation Pattern and Fixed Order of Pipeline Results.
- NVIDIA, *GeForce 8 and 9 Series GPU Programming Guide*, Geometry Shader performance sections.
- Joshua Barczak, *Why Geometry Shaders Are Slow (Unless you're Intel)*.
- Jasper Bekkers, *Mesh Shaders and the Future of Geometry Processing*.
- Catlike Coding, *Flat and Wireframe Shading*.
