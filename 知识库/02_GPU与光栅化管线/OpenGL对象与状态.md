# OpenGL对象与状态

OpenGL对象名称不是内存地址，绑定又改变当前上下文。绘制失败时要同时核对对象生命周期与当时状态，不能只看到句柄非零就认为资源已正确使用。

## OpenGL 状态机与对象

OpenGL 上下文保存当前程序、Vertex Array、Framebuffer、纹理单元、深度测试和混合等状态。`glBind*`、`glUseProgram` 与 `glEnable` 修改当前上下文，后续 Draw 会读取当时的状态组合。对象句柄只是当前上下文可识别的整数名称，不是 CPU 指针，也不代表对象已经绑定。

对象的常见生命周期是 `glGen*` 或 `glCreate*` 取得名称，绑定或直接状态访问完成初始化，Draw 使用对象，最后在拥有共享关系的上下文中删除。应用可以按 OpenGL 删除语义释放名称，驱动管理尚未完成工作的底层引用；缓冲区内容的覆盖和跨上下文访问仍要正确同步。显式 API 的资源销毁则由应用跟踪 GPU 完成。

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

## 验证方法

查询真实版本与扩展，检查函数加载、共享上下文和第一条异常绘制前的状态。删除名称语义由驱动管理未完成引用，覆盖缓冲内容仍需同步。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[13_渲染架构/Render Pass与附件]]
- [[02_GPU与光栅化管线/一帧如何到达屏幕]]

## 参考资料

- Microsoft Learn, *Graphics Pipeline (Direct3D 11)*.
- Khronos, *Vulkan Specification*, Chapter: Pipelines.
- AMD GPUOpen, graphics performance guides.
- LearnOpenGL, `src/4.advanced_opengl/9.*.geometry_shader_*`.
- LearnOpenGL, `src/8.guest/2021/3.tessellation`.
- LearnOpenGL 中文镜像，*OpenGL*、*Hello Window*、*Hello Triangle*。
