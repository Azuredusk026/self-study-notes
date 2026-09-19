# Profiler、RenderDoc 与单帧分析

性能分析的目标是形成证据链：哪一帧慢、哪一侧慢、哪个事件占时间、它为什么慢、修改后是否改善。

## 第一层：稳定复现

先固定：

- 设备、分辨率和图形设置；
- 场景、相机路径和角色状态；
- VSync、帧率上限和动态分辨率；
- 是否 Development Build；
- 冷启动还是缓存后；
- 温度和电量状态。

无法复现的“偶尔卡”要先记录 Trace，而不是直接猜优化方案。

## 第二层：判断 CPU 还是 GPU

### Unity Profiler

查看 Main Thread、Render Thread、Job、GC、Loading 和 GPU Module。Timeline 比单一 Hierarchy 百分比更适合看线程等待关系。

注意：

- Editor Profiler 有编辑器开销；
- GPU 时间可能受平台和 Profiler 支持限制；
- `Gfx.WaitForPresent` 可能表示 CPU 等 GPU/VSync；
- Deep Profile 会严重改变性能。

### 平台工具

- PIX：Direct3D；
- Nsight Graphics：NVIDIA；
- Radeon GPU Profiler：AMD；
- Xcode GPU Tools：Apple；
- Android GPU Inspector：Android；
- Snapdragon Profiler、Arm Mobile Studio 等厂商工具。

引擎 Profiler 给系统视角，平台工具给硬件 Counter 和 API 细节。

## Frame Debugger 能看什么

Frame Debugger 按引擎事件展示：

- Draw 顺序；
- Batcher 原因；
- Render Target 变化；
- Shader Pass；
- 最终画面怎样逐步形成。

它适合理解引擎组织，但不一定显示真实 API Barrier、Driver 工作和精确 GPU 时间。

## RenderDoc 能看什么

RenderDoc 捕获一个图形 API 帧，可以检查：

- Event Browser；
- Pipeline State；
- Texture/Buffer；
- Mesh Input/Output；
- Shader Resource 和 Constant；
- Pixel History；
- Shader Debug；
- Draw/Dispatch 时间（取决于计时支持）。

它主要回答“这一帧发生了什么”，不是长时间卡顿、温度和 CPU 调度工具。

## API Debug Message

图形 API 的验证层和调试回调适合在开发构建中尽早发现无效状态、资源绑定、同步和对象生命周期问题。OpenGL Debug Output 的最小接入如下：

```cpp
void APIENTRY OnGlMessage(GLenum source, GLenum type, GLuint id,
                          GLenum severity, GLsizei length,
                          const GLchar* message, const void* user)
{
    if (severity == GL_DEBUG_SEVERITY_NOTIFICATION)
        return;
    LogGraphicsMessage(source, type, id, severity, message);
}

glEnable(GL_DEBUG_OUTPUT);
glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS);
glDebugMessageCallback(OnGlMessage, nullptr);
```

同步回调便于在调试器中定位触发调用，也会增加 CPU 开销。正式运行可以关闭同步或按来源、类型和 ID 过滤消息。

调试层只能报告 API 能识别的问题。合法但错误的矩阵、坐标空间、光照公式和性能设计仍需要帧捕获、可视化和对照实验定位。Vulkan Validation Layer、D3D12 Debug Layer 和 GPU-based Validation 也遵循相同边界。

## 单帧分析顺序

### 1. 看 Pass 构成

列出 Shadow、Depth、GBuffer/Forward、Lighting、Transparent、Post Process、UI。检查是否有意外重复 Camera、Reflection、Scene Capture。

### 2. 看分辨率和格式

检查每个 Render Target 的宽高、Samples、Format 和 Mip。一个不必要的 Full-resolution RGBA16F 临时 Buffer 可能比 Shader 算术更贵。

### 3. 看 Draw 和状态

检查 Draw 数、Instance Count、PSO/Material 切换、Vertex/Index 数量和 Batcher。

### 4. 看像素覆盖

检查全屏 Pass、透明层数、粒子 Bounds 和 Overdraw。一个只在角落显示的效果不应运行全屏复杂 Shader。

### 5. 看 Shader 和资源

统计纹理采样、循环、分支、寄存器和指令。确认实际绑定的纹理尺寸、Mip 和压缩格式。

### 6. 看同步和依赖

查找 Queue Wait、Barrier、Readback、Resolve 和 Copy。判断 GPU 是否有 Bubble。

## Pixel History

Pixel History 可以显示某像素被哪些 Draw 修改、因 Depth/Stencil 失败或 Blend 后得到什么结果。

适合定位：

- 为什么物体没显示；
- 谁覆盖了颜色；
- 透明混合顺序；
- Stencil/Depth 状态；
- Overdraw 来源。

## GPU Counter

不同硬件提供不同 Counter，常见维度：

- Shader Core 利用率；
- Texture/Memory 吞吐；
- Cache Hit/Miss；
- Wave Occupancy；
- Raster/ROP；
- Primitive Culling；
- Tile Load/Store；
- Ray Tracing Unit。

Counter 高不是自动的问题。例如带宽利用高但帧时间达标，可能只是硬件被充分使用。需要结合瓶颈和修改实验。

## 引擎自带的追踪工具

通用图形调试器擅长单帧的 GPU 细节，但定位"哪个系统在什么时候消耗了多少"需要引擎侧的追踪工具。

### 追踪型 Profiler

Unreal Insights 一类的工具记录一段时间内的多通道数据——CPU 各线程的调用栈、GPU 时间、内存分配、加载事件、网络收发——并按同一时间轴对齐。

它与单帧捕获的分工很清楚：单帧捕获回答"这一帧的这次绘制为什么慢"，时间轴追踪回答"卡顿出现在哪一帧、由哪个系统引起"。定位偶发卡顿只能靠后者，因为你无法预知该在哪一帧按下捕获。

使用要点是先划定关注区间。一段几分钟的追踪数据量巨大，应当用自定义标记圈出关卡加载、战斗开始等关键区段，再逐层下钻。

### 内存分类报告

内存问题需要按类别归因而非只看总量。引擎通常提供两级手段：

- **全量报告**：某一时刻按资源类型、类、包分类的内存清单，适合回答"内存被谁占了"；
- **统计项埋点**：为自定义子系统声明统计项，持续采样其内存占用，适合回答"这个系统的内存是否随时间增长"。

前者是快照，后者是曲线。判断泄漏必须用后者——单次快照无法区分"占用大"与"持续增长"。

### 构建配置影响测量结果

性能数据必须标注构建配置，否则无法比较：

| 配置 | 特点 | 适用 |
|---|---|---|
| Debug | 无优化，可完整调试 | 定位逻辑错误，不用于性能测量 |
| Development | 优化开启，保留统计与控制台 | 日常性能分析 |
| Shipping | 全优化，剥离调试设施 | 最终性能验收 |

Development 与 Shipping 的差距可能达到可观比例——统计埋点、日志、断言本身都有成本。用 Development 数据承诺 Shipping 表现会高估负担；反过来，Shipping 缺少埋点，难以定位问题来源。

实践做法是用 Development 定位与迭代，用 Shipping 做最终验收，并在报告中始终标明配置。编辑器内运行则是第三种情况，其开销与独立包差异更大，不能作为性能依据。
## 从证据到假设

一个合格假设应写成：

> 透明粒子在 1440p 覆盖屏幕 6 层，Transparent Pass 占 4.2 ms，GPU Counter 显示 Color/Texture Bandwidth 接近上限。把远景粒子降到半分辨率并收紧网格后，预计减少带宽和 Overdraw。

而不是：

> 粒子很多，应该优化一下。

## 不同工具结果冲突

可能来自：

- 捕获帧不是同一场景状态；
- GPU Timestamp 粒度；
- Profiler 插桩改变执行；
- Dynamic Resolution/Exposure/Streaming 状态不同；
- Capture 禁用了某些异步或 Driver 优化；
- Editor 和 Player 路径不同。

记录工具版本和捕获条件，再做交叉验证。

## 相关主题

- [[14_性能分析与优化/帧时间、瓶颈与GPU成本]]
- [[14_性能分析与优化/渲染优化验证与移动端实践]]
- [[13_引擎架构与资源系统/Render Pass、Command Buffer与Render Graph]]
- [[06_纹理技术/UV、图集、流送与虚拟纹理]]

## 参考资料

- RenderDoc documentation.
- Microsoft PIX documentation.
- NVIDIA Nsight Graphics and AMD Radeon GPU Profiler documentation.
- Unity Profiler and Frame Debugger manuals.
- LearnOpenGL, `src/7.in_practice/1.debugging`.
