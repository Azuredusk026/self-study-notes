# Draw Call、Batching 与 GPU Instancing

Draw Call 的主要问题通常在 CPU 提交、状态管理和驱动/API 工作。它不是 GPU “画一次像素”的单位，也不能脱离三角形、像素和 Shader 成本只看数量。

## 一次 Draw 包含什么

CPU 需要确定：

- Pipeline State；
- Vertex/Index Buffer；
- Descriptor/Resource；
- Constant 和实例数据；
- Draw 参数。

GPU 执行后，还要处理顶点、光栅化、Pixel Shader、深度和混合。减少 Draw 只解决其中一部分成本。

## 为什么状态切换重要

连续 Draw 如果共享 Shader、材质状态和资源布局，CPU 和 GPU 更容易复用状态。频繁切换 Pipeline、Render Target、Descriptor 和纹理会增加验证、缓存失效或 Pipeline Bubble。

渲染排序经常同时考虑：

- 不透明物体 Front-to-back，提高 Early-Z；
- 按 Pipeline/材质分组，减少状态切换；
- 透明物体 Back-to-front，保证混合近似正确。

这些目标可能冲突，需要按场景权衡。

## Static Batching

把静态网格变换到统一空间并合并 Buffer，减少提交。

优点：

- 运行时不需要逐对象变换；
- 可以减少小网格 Draw。

代价：

- 合并后的顶点会复制，增加内存；
- 大合并网格可能降低剔除粒度；
- 不能单独移动；
- Lightmap、材质和平台限制影响能否合并。

## Dynamic Batching

CPU 每帧把少量动态网格转换并合并。它只适合很小的网格和有限属性。

现代平台上，CPU 变换和拷贝成本可能比节省的 Draw 更贵。不同 Unity 版本和 SRP 支持也不同，不能把它当默认优化。

## SRP Batcher

Unity SRP Batcher 的重点是减少相同 Shader Variant 间材质常量设置和 CPU 状态准备。它把引擎内置数据和材质数据按稳定布局组织，让 Draw 间只更新必要内容。

它通常**不会把多个对象变成一个 Draw Call**。Profiler 中 Draw 数可能不变，但 CPU Render Thread 时间下降。

材质 Shader 的 Constant Buffer 布局、兼容 Pass 和 Keyword 会影响是否进入 SRP Batcher。

## GPU Instancing

多个对象共享 Mesh 和 Material/Shader Variant，只为每个实例提供不同数据：

- Transform；
- Color；
- 动画帧；
- LOD/可见性；
- 自定义属性。

CPU 可以用一次 Instanced Draw 提交多个实例。主要收益是减少 Draw Call 和 CPU-GPU 命令交互，不是因为“只画一次模型”或自动减少像素工作。

GPU 仍会为每个实例处理对应顶点和片元。

## 实例数据成本

每实例完整 4x4 矩阵需要 64 字节。大量实例时可以保存 Position、Quaternion、Scale，或使用压缩格式减少带宽，但会增加 Shader 解码。

实例属性应连续存储，避免每实例随机访问多个 Buffer。

## GPU Animation Texture

把每帧骨骼矩阵或变换烘焙到纹理/Buffer。每个实例保存动画 ID、时间和混合权重，Vertex Shader 采样骨骼数据完成蒙皮。

动画混合可以：

1. 分别采样动画 A/B 的骨骼变换；
2. 平移做 Lerp，旋转做 Nlerp/Slerp；
3. 重新组合变换后蒙皮。

直接线性混合矩阵可能破坏正交性并产生缩放。双采样也会增加纹理带宽和顶点成本。

## MaterialPropertyBlock

Unity MPB 可以为 Renderer 提供每对象参数而不克隆 Material。它是否与 SRP Batcher、GPU Instancing 兼容取决于属性声明、管线和 Unity 版本。

不能只看“没有生成材质实例”。需要在 Frame Debugger/Profiler 检查实际 Batcher 原因。

## Indirect Draw

GPU Culling 后把可见实例数量和参数写入 Indirect Argument Buffer，再由 GPU 发起 Draw。CPU 不需要回读可见列表。

这能进一步减少大量实例的 CPU 工作，但需要：

- GPU 可见性和 LOD；
- Prefix Sum/Compaction；
- Indirect Argument；
- 资源 Barrier；
- 避免读回同步。

## 合批为什么失败

- Material/Shader Variant 不同；
- Render State 或 Pass 不同；
- Mesh 不同且方案要求相同 Mesh；
- Lightmap、Probe、Shadow 状态不同；
- Per-object 数据没有放入兼容实例通道；
- 排序或透明顺序不能合并；
- 负缩放、特殊渲染层或 Renderer Feature 分开绘制。

## 验证方法

- CPU Profiler 查看 Render Thread、Batch 构建和提交时间。
- Frame Debugger 查看为什么一个对象没有进入目标 Batcher。
- RenderDoc 检查一次 Draw 的 Instance Count。
- 分别统计 Draw、SetPass/PSO Switch、Vertex 和 Pixel 成本。
- 比较合批前后内存、剔除粒度和 GPU 时间，不只比较 Draw 数。

## 相关主题

- [[03_Shader编程/Shader编译、关键字与变体]]
- [[09_动画系统/骨骼动画、蒙皮与GPU动画]]
- [[12_光追与现代渲染/GPU-Driven管线与Nanite]]
- [[14_性能分析与优化/帧时间、瓶颈与GPU成本]]

## 参考资料

- Unity Manual, *Draw call batching* and *SRP Batcher*.
- Microsoft Learn, *DrawInstanced and ExecuteIndirect*.
- GPUOpen, GPU-driven rendering references.
