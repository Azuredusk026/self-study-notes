# OpenGL对象与状态

OpenGL对象名称不是内存地址，绑定又改变当前上下文。绘制失败时要同时核对对象生命周期与当时状态，不能只看到句柄非零就认为资源已正确使用。

## OpenGL 状态机与对象

OpenGL 上下文保存当前程序、Vertex Array、Framebuffer、纹理单元、深度测试和混合等状态。`glBind*`、`glUseProgram` 与 `glEnable` 修改当前上下文，后续 Draw 会读取当时的状态组合。对象句柄只是当前上下文可识别的整数名称，不是 CPU 指针，也不代表对象已经绑定。

对象的常见生命周期是 `glGen*` 或 `glCreate*` 取得名称，绑定或直接状态访问完成初始化，再供 Draw 使用。删除操作需要能识别该对象的当前上下文：缓冲和纹理可由共享组内上下文使用；核心规范中的 VAO、FBO 等容器对象不共享，必须由所属上下文管理。应用按 OpenGL 删除语义释放名称，驱动管理尚未完成工作的底层引用；缓冲区内容覆盖和跨上下文访问仍要正确同步。显式 API 的资源销毁则由应用跟踪 GPU 完成。

Core Profile 提供当前核心规范中的接口。固定管线矩阵、立即模式等兼容接口属于 Compatibility Profile。窗口库创建上下文后应查询实际版本和扩展，不能把头文件中存在的函数当成运行环境一定支持：

```cpp
GLint major = 0, minor = 0;
glGetIntegerv(GL_MAJOR_VERSION, &major);
glGetIntegerv(GL_MINOR_VERSION, &minor);

bool hasCoreDebug = major > 4 || (major == 4 && minor >= 3);
bool hasDebugOutput = hasCoreDebug
    || glfwExtensionSupported("GL_KHR_debug") == GLFW_TRUE;
if (hasDebugOutput) {
    glEnable(GL_DEBUG_OUTPUT);
    glDebugMessageCallback(OnGLMessage, nullptr);
}
```

这段代码依赖已经设为当前的有效 OpenGL 上下文。版本查询得到运行时能力，扩展查询还要结合相应函数入口是否成功加载。多个上下文并存时，对象共享范围与当前状态需要按规范和窗口库设置处理。逐通道记录着色程序、帧缓冲、深度和混合状态。对象绑定出错时，从第一条输出异常的绘制向前查找最近一次状态变更。

## 顶点数组的绑定捕获

对象保存数据，绑定点决定下一条命令操作哪个对象，容器对象再保存对象间的连接。以OpenGL 3.3核心上下文的顶点输入为例，调用`glVertexAttribPointer`时，当前`GL_ARRAY_BUFFER`会被记录到当前VAO的对应属性中。之后切换ARRAY_BUFFER不会自动改变这条连接。

```cpp
// vao、positions、otherBuffer已创建；positions含紧密排列的float3
glBindVertexArray(vao);
glBindBuffer(GL_ARRAY_BUFFER, positions);
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), nullptr);
glEnableVertexAttribArray(0);
glBindBuffer(GL_ARRAY_BUFFER, otherBuffer);
// vao的属性0仍读取positions；glVertexAttribPointer再次调用才会改接
```

这段C++调用片段省略上下文、函数加载和数据上传。排查时查询属性0的`GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING`，再查stride、offset和使能位；仅查询当前ARRAY_BUFFER会看见otherBuffer，却不能解释绘制真正读取的资源。索引缓冲绑定则属于VAO状态，切换VAO时必须一并检查。

## 验证方法

查询真实版本与扩展，检查函数加载、共享上下文和第一条异常绘制前的状态。删除名称语义由驱动管理未完成引用，覆盖缓冲内容仍需同步。

实现状态：版本查询和VAO绑定均为需要有效上下文的C++片段，未在OpenGL上下文中执行。绑定捕获语义已核对规范；运行验收需按查询值确认属性0仍指向positions，并检查调试回调输出。

## 相关主题

- [[13_渲染架构/Render Pass与附件]]
- [[02_GPU与光栅化管线/渲染帧流程]]

## 参考资料

- [OpenGL 4.6 Core规范](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf)：2026-10-22核读2.6.9—2.6.11的容器对象定义，FBO、VAO与Transform Feedback对象均不共享；范围限定核心规范。
- [Khronos glVertexAttribPointer规范源文件](https://github.com/KhronosGroup/OpenGL-Refpages/blob/main/gl4/glVertexAttribPointer.xml)：2026-10-22核读Description中的GL_ARRAY_BUFFER_BINDING捕获及vertex array state段，限定传统属性指针接口。
- [Khronos glDebugMessageCallback](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glDebugMessageCallback.xhtml)：调试回调接口入口，本轮未运行上下文验证。
