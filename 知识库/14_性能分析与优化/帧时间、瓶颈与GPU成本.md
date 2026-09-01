# 帧时间、瓶颈与 GPU 成本

性能优化先看时间，不先看方案名称。60 FPS 的单帧预算约 16.67 ms，30 FPS 约 33.33 ms。FPS 是帧时间的倒数，平均 FPS 会掩盖偶发尖峰。

## Frame Time

需要同时记录：

- 平均帧时间；
- P95/P99；
- 最坏帧；
- CPU Main Thread；
- CPU Render Thread；
- GPU Frame；
- 内存和温度随时间变化。

一段 5 秒稳定场景和 30 分钟真机运行回答的是不同问题。

## CPU Bound

CPU 无法及时准备下一帧。常见来源：

- Gameplay、动画、物理；
- Culling 和 Render List；
- Draw Call/状态提交；
- 资源加载、反序列化和实例化；
- GC；
- 主线程锁和 Job 等待。

症状可能是 GPU 有空闲 Bubble，CPU Profiler 中某线程持续接近帧预算。

降低分辨率后帧时间几乎不变，常提示 CPU 或非像素瓶颈，但这不是单独的充分证据。

## GPU Bound

GPU 无法在预算内完成命令。可能受：

- Vertex/Geometry；
- Pixel/Fragment；
- Compute；
- Texture/Memory Bandwidth；
- Render Target 带宽；
- 同步和 Pipeline Bubble；
- Ray Tracing；
- Queue 重叠争用。

降低分辨率后明显加速，说明成本与像素相关的可能性高，例如 Overdraw、后处理、GBuffer 或高分辨率阴影，但仍要用 GPU Counter 确认。

## CPU 和 GPU 时间为什么不能简单相加

CPU 与 GPU 通常并行。帧总时间接近较慢一侧和必要同步，而不是 Main Thread + Render Thread + GPU 的直接总和。

如果 CPU 等待 `Present` 或 Fence，它的等待时间可能只是 GPU 慢的结果。不能看到 CPU Wait 很高就判断 CPU 算法慢。

## Draw Call 成本

Draw Call 主要增加 CPU 提交、状态准备和驱动/API 开销。GPU 端还会受小批次、状态切换和 Pipeline 利用率影响。

优化 Draw 时要区分：

- Draw 数；
- SetPass/PSO Switch；
- 每 Draw 三角形和实例数；
- CPU Render Thread 时间；
- GPU 是否因小批次或状态切换空闲。

## Vertex 成本

顶点成本不只由三角形数量决定：

- 顶点拆分；
- Index Cache；
- Skinning 骨骼数；
- Vertex Texture Fetch；
- Tessellation；
- 多 Pass 重复绘制；
- Shadow Cascade。

一个三角形越小，越容易在光栅化后只覆盖很少样本，甚至产生 Quad Utilization 浪费。

## Pixel 和 Overdraw

Pixel 成本约受下面因素共同影响：

```text
屏幕覆盖 × Overdraw 层数 × Shader 成本 × 样本数
```

透明、粒子、全屏 Pass 和复杂材质是常见来源。Early-Z 能减少部分不透明像素，但无法让所有情况免费。

## Fill Rate 和带宽

Fill Rate 关注单位时间处理/写入样本的能力。带宽关注从显存读取和写入多少字节。

高分辨率 GBuffer、HDR、MSAA、多个全屏 Pass 会增加 Render Target 带宽。纹理采样也会增加读取，但 Cache 命中和压缩会改变实际流量。

## Cache

GPU 常有 Texture Cache、L1/L2 和专用缓存。性能取决于访问局部性，不只是资源总大小。

- 连续实例数据容易合并读取；
- 随机访问大 Buffer 可能频繁 Miss；
- Mipmap 改善远处纹理 Footprint；
- 同一 Wave 访问相邻地址通常更友好。

## Occupancy 和 Latency Hiding

GPU 让多个 Wave 同时驻留，以便一个 Wave 等待纹理时执行另一个。每线程寄存器、Group Shared Memory 和 Group Size 会限制驻留数量。

Occupancy 不是目标分数。算法带宽已满时，提高 Occupancy 不一定加速；寄存器过少还可能 Spill 到内存。

## 同步成本

- CPU-GPU Fence；
- GPU Readback；
- Render Target 到 Shader Resource 的 Barrier；
- Graphics/Compute Queue 互等；
- 资源 Upload 覆盖仍在使用的数据。

同步可能表现为一段没有有效工作的 Bubble。优化要减少不必要依赖，而不是删除正确性需要的 Barrier。

## VRAM 和内存压力

超出显存预算会导致 Streaming、驱逐、系统内存回退或严重抖动。需要统计：

- Texture 各 Mip 和格式；
- Mesh/Animation Buffer；
- Render Target；
- Ray Tracing Acceleration Structure；
- 临时资源峰值；
- 重复 Bundle/Asset。

只看磁盘包体不能推断运行时 VRAM。

## 相关主题

- [[知识库/13_引擎架构与资源系统/Draw Call、Batching与GPU Instancing]]
- [[知识库/02_GPU与光栅化管线/光栅化、插值与深度模板]]
- [[知识库/14_性能分析与优化/Profiler、RenderDoc与单帧分析]]
- [[知识库/14_性能分析与优化/渲染优化验证与移动端实践]]

## 参考资料

- NVIDIA, *GPU Performance Background User's Guide*.
- AMD GPUOpen, *Performance Guide*.
- Unity Manual, *Understanding performance*.
