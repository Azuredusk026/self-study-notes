# Render Pass、Command Buffer 与 Render Graph

这三个词处在不同层次：Render Pass 描述一段渲染工作，Command Buffer 记录具体 GPU 命令，Render Graph 根据资源依赖组织多个 Pass。

## Render Pass 的多种含义

### 算法层

Shadow Pass、GBuffer Pass、Lighting Pass、Bloom Pass。这里的 Pass 是完成某项任务的一段工作。

### 材质/引擎层

一个 Shader/Material 可以有多个 Pass，例如 Depth、Forward、ShadowCaster。引擎根据当前阶段选择。

### 图形 API 层

Vulkan Render Pass、Dynamic Rendering、Metal Render Command Encoder 等描述 Attachment、Load/Store 和子过程。它和 Unity ShaderLab 的 `Pass` 不是同一个概念。

讨论时必须指出层次。

## Command Buffer 为什么存在

GPU 不直接执行 CPU 函数调用。CPU 把状态、Draw、Dispatch、Copy 和 Barrier 编码成命令序列，再提交到 Queue。

记录成集合有几个原因：

- 批量减少 API/驱动提交开销；
- CPU 可以提前记录，GPU 稍后异步执行；
- 多线程可以并行准备不同命令；
- 命令顺序和资源依赖变得明确；
- 同一批命令可以统一提交和同步；
- 现代 API 可以减少驱动的隐式状态推断。

它不是单纯“方便插入自定义管线命令”的容器。

## 记录不等于执行

调用 `Draw`/`Dispatch` 记录命令时，GPU 可能还没开始对应工作。只有提交后，Queue 才按依赖执行。

因此：

- CPU 修改临时数据后，命令真正执行时数据必须仍然有效；
- Upload/Constant Buffer 需要 Ring Buffer 或 Fence 管理重用；
- GPU Readback 会引入等待；
- Profiler 的 CPU 调用时间不等于 GPU 执行时间。

## Pipeline State

现代 API 会把 Shader、Blend、Depth/Stencil、Rasterizer、Render Target Format 等组合成 Pipeline State Object。

提前创建 PSO 可以把兼容性检查和编译移出 Draw 热路径。代价是组合数量增加，需要 PSO Cache 和预热策略。

## Resource State 和 Barrier

同一资源可能先作为 Render Target 写入，再作为 Shader Resource 读取。GPU 必须知道：

- 前一次写入何时完成；
- Cache 何时可见；
- 当前访问类型和布局；
- 哪些阶段需要等待。

Barrier 建立执行和内存依赖。Barrier 太少会数据竞争，太多会让 GPU 失去并行和压缩优化。

## Queue 和同步

Graphics、Compute、Copy Queue 可以并行，但跨 Queue 资源依赖需要 Semaphore/Fence 等同步。

Async Compute 适合和图形工作重叠。若两者都吃满 ALU、带宽或 Cache，重叠可能反而更慢。

## Render Graph

Render Graph 让每个 Pass 声明：

- 读取哪些资源；
- 写入哪些资源；
- 创建哪些临时资源；
- 需要什么 Attachment 和状态。

系统据此建立有向依赖图。

## Render Graph 能做什么

### Pass Culling

某个 Pass 的输出最终没人使用，而且没有外部副作用，就可以跳过。

### Transient Resource

只在少数 Pass 之间存在的纹理不必常驻。Render Graph 可以计算生命周期，并让不重叠的资源复用同一块内存。

### Barrier 和 Layout

根据读写关系自动生成资源转换，减少手写遗漏。

### Pass Merge

Tile-based GPU 上，如果多个 Pass 的 Attachment 关系兼容，可以尽量留在 Tile Memory，减少 Store/Load。

## Render Graph 不能自动解决什么

- Pass 算法本身太慢；
- 错误的分辨率和格式；
- 没声明的外部副作用；
- 资源被隐藏在全局状态里；
- Shader 内部随机访问和带宽；
- 不合理的跨 Queue 同步。

如果 Pass 没有准确声明资源，自动优化反而可能产生错误。

## Unity CommandBuffer

Unity `CommandBuffer` 可以记录 Draw、Blit、Dispatch、SetRenderTarget 等命令，再由 Built-in Event、SRP 或自定义 Pass 执行。

使用时要注意：

- 临时 RenderTexture 生命周期；
- Camera 多次渲染；
- XR Slice；
- Render Scale 和 Dynamic Resolution；
- 不要在每帧无必要地创建大量 CommandBuffer 和资源；
- 新版 URP/HDRP 的 Render Graph 路径可能改变推荐接口。

具体 API 随 Unity 版本变化，应按项目版本核对。

## 验证方法

- 在 Frame Capture 中跟踪资源从写入到读取。
- 检查 Barrier 前后 Pipeline Stage 和 Access Mask。
- 查看 Render Graph Viewer 中 Pass Culling、资源生命周期和别名复用。
- 对比同步前后 GPU Bubble。
- 检查临时资源是否在错误时间释放或跨帧复用。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[03_Shader编程/Compute Shader与GPU执行模型]]
- [[13_引擎渲染与资源架构/Unity与Unreal渲染扩展入口]]
- [[14_性能分析与优化/Profiler、RenderDoc与单帧分析]]

## 参考资料

- Khronos, *Vulkan Specification*, Command Buffers and Synchronization.
- Microsoft Learn, *Direct3D 12 Command Queues and Command Lists*.
- Unity Manual, *Render Graph system*.
