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

OpenGL Framebuffer 可以作为图形 API 层的最小离屏渲染例子。颜色附件和深度附件的尺寸、样本数必须兼容，提交前检查完整性：

```cpp
GLuint framebuffer = 0;
glCreateFramebuffers(1, &framebuffer);
glNamedFramebufferTexture(framebuffer, GL_COLOR_ATTACHMENT0,
                          colorTexture, 0);
glNamedFramebufferTexture(framebuffer, GL_DEPTH_ATTACHMENT,
                          depthTexture, 0);

GLenum drawBuffers[] = { GL_COLOR_ATTACHMENT0 };
glNamedFramebufferDrawBuffers(framebuffer, 1, drawBuffers);

if (glCheckNamedFramebufferStatus(framebuffer, GL_FRAMEBUFFER)
    != GL_FRAMEBUFFER_COMPLETE)
    ReportFramebufferError(framebuffer);
```

这段代码只建立 Attachment 关系。实际 Pass 还要设置 Viewport、Clear/Load 行为、读写状态，并在后续采样前保证写入可见。

示例使用 OpenGL Direct State Access（DSA），函数参数明确指出被修改的对象。它减少依赖全局 Bind State 造成的误操作，也方便封装资源创建。DSA 主要改善 API 状态管理，不会自动减少 GPU 的 Attachment、带宽或同步成本。

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

## Unreal 的 RHI 分层

Unreal 在图形 API 之上建立了自己的抽象层，理解这个分层有助于定位问题发生在哪一级。

```text
渲染器            平台无关的算法与 Pass 组织
  ↓
RHI              统一抽象：资源、命令列表、Shader、PSO
  ↓
DynamicRHI 实现   D3D12 / Vulkan / Metal / OpenGL 各自的后端
  ↓
图形 API
```

`FRHIResource` 是资源基类，纹理、缓冲、Uniform Buffer 都派生自它；`FDynamicRHI` 是后端入口，每个平台提供一份实现。渲染器只面向 RHI 接口编程，平台差异被约束在后端。

这个分层也解释了 Shader 的两级结构：`FShader` 及其派生的 `FGlobalShader` 属于引擎层，描述参数绑定与编译条件；平台相关的字节码与创建过程在 RHI 后端完成。

### 参数绑定模型

D3D12 的根签名、Vulkan 的描述符集布局，在 RHI 层被统一成 Shader 参数结构的声明。引擎用宏声明参数布局，编译期生成绑定信息，运行时按这份信息填充。

绑定模型的成本差异值得留意：频繁更换的参数应放在更廉价的绑定槽位，稳定不变的参数适合打包进 Uniform Buffer 一次绑定。参数结构设计不当会让每次 Draw 都重新绑定大量资源。

### RDG

Unreal 的 Render Dependency Graph 是 Render Graph 思路的具体实现。Pass 通过参数结构声明读写的资源，RDG 据此生成 Barrier、管理 Transient 资源、剔除无人消费的 Pass。

两个实践要点：

其一，**未被消费的 Pass 会被静默剔除**。新增的 Pass 如果写入的资源没有任何后续 Pass 读取，它不会执行，在帧捕获里也找不到。调试时若发现 Pass "消失"，先检查输出是否被消费，而不是怀疑注册失败。

其二，**不要混用手工资源管理**。手动创建的资源不参与别名复用，手动插入的 Barrier 可能与 RDG 生成的冲突。修改引擎渲染代码前先确认目标路径是否仍走 RDG。

## 验证方法

- 在 Frame Capture 中跟踪资源从写入到读取。
- 检查 Barrier 前后 Pipeline Stage 和 Access Mask。
- 查看 Render Graph Viewer 中 Pass Culling、资源生命周期和别名复用。
- 对比同步前后 GPU Bubble。
- 检查临时资源是否在错误时间释放或跨帧复用。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[03_Shader编程/Compute Shader与GPU执行模型]]
- [[13_引擎架构与资源系统/Unity与Unreal渲染扩展入口]]
- [[14_性能分析与优化/Profiler、RenderDoc与单帧分析]]
- [[13_引擎架构与资源系统/Unreal网格绘制与自定义Pass]]
- [[14_性能分析与优化/PSO缓存与运行时卡顿]]

## 参考资料

- Khronos, *Vulkan Specification*, Command Buffers and Synchronization.
- Microsoft Learn, *Direct3D 12 Command Queues and Command Lists*.
- Unity Manual, *Render Graph system*.
- LearnOpenGL, `src/4.advanced_opengl/5.1.framebuffers`.
- LearnOpenGL, `src/8.guest/2021/4.dsa`.
- Epic Games, *Render Dependency Graph* and *Graphics Programming* documentation.
- Unreal Engine source, `FRHIResource`, `FDynamicRHI`, `FRHICommandList`.
