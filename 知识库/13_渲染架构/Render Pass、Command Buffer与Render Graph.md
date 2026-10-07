# Render Pass、Command Buffer与Render Graph

渲染通道说明执行哪项任务，命令缓冲记录实际 GPU 操作，渲染图组织资源依赖。阅读时沿“资源与任务 → 记录与提交 → 执行与完成”追踪，区分引擎软件分工与图形 API 的对象。

## 阅读路径

| 要回答的问题 | 专题 |
|---|---|
| 附件开始保留什么，结束存储什么 | [[13_渲染架构/Render Pass与附件]] |
| CPU 记录后何时到 GPU，何时可复用 | [[13_渲染架构/Command Buffer与帧提交]] |
| 写入何时对读取可见 | [[13_渲染架构/GPU同步与屏障]] |
| 图如何剔除、分配与安排通道 | [[13_渲染架构/Render Graph]] |
| 材质如何寻址参数和纹理 | [[13_渲染架构/GPU资源绑定]] |
| 上传、回读、历史与临时内存何时回收 | [[13_渲染架构/GPU资源生命周期]] |
| Shader 与渲染状态怎样构成 PSO | [[13_渲染架构/Pipeline State Object]] |

## 一次颜色效果的数据流

下面是图与命令职责的 API 中立轮廓。输入是可采样的场景颜色，输出有明确消费者；资源状态与完成值由具体后端落实。

```text
source = graph.Import(sceneColor)
destination = graph.CreateTexture(sceneDescription)
pass = graph.AddPass("ColorEffect")
pass.Read(source, Sampled)
pass.Write(destination, ColorAttachment)
pass.Execute(context => RecordFullScreenDraw(context))
graph.Export(destination, finalColor)
graph.Compile()
graph.Execute()
submitRecordedCommands()
retainResourcesUntilGpuCompletion()
```

记录回调可能在图编译之后才执行。通道没有可观察输出时可以被剔除，外部纹理和副作用需要显式声明。命令已记录、已提交和 GPU 已完成分别决定不同资源的使用权限。

## 引擎入口

Unity 6 URP 在 `RecordRenderGraph` 声明通道，旧兼容路径使用其既有执行接口。Unreal RDG 通过参数结构表达读写，再生成 RHI 请求。图内逻辑句柄不等同于可以无限保存的原生资源指针。

- [[22_渲染引擎实现/Unity渲染帧组织]]
- [[22_渲染引擎实现/URP Render Graph自定义Pass]]
- [[22_渲染引擎实现/Unreal渲染帧组织]]
- [[22_渲染引擎实现/Unreal RDG Pass实现]]

## 验证方法

先输出纯色确认通道实际执行，再采样输入并检查附件与消费者。查看图逻辑依赖与 GPU 实际命令，确认屏障、资源范围和回收完成值。需要性能结论时记录独立 GPU 计时，捕获状态用于解释路径。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[14_性能分析与优化/性能对照实验]]
- [[13_渲染架构/Render Graph]]

## 参考资料

- [Vulkan Command Buffers](https://docs.vulkan.org/spec/latest/chapters/cmdbuffers.html) 与 [Synchronization](https://docs.vulkan.org/spec/latest/chapters/synchronization.html)。
- [D3D12 Command Queues and Lists](https://learn.microsoft.com/en-us/windows/win32/direct3d12/command-queues-and-command-lists)。
- Unity 6 URP Render Graph 与 Epic Render Dependency Graph 官方文档。
