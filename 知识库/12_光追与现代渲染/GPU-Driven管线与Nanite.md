# GPU-Driven 管线与 Nanite

GPU-Driven Rendering 把可见性、LOD、实例列表和绘制参数尽量留在 GPU 内生成。目标不是“CPU 完全不参与”，而是避免 CPU 每帧逐对象提交和读回大规模可见列表。

## CPU-Driven 的扩展瓶颈

传统流程由 CPU：

1. 遍历 Scene Object；
2. 做 Frustum/Occlusion/LOD；
3. 按材质和深度排序；
4. 设置资源与状态；
5. 发出 Draw Call。

对象数量很大时，即使每个 Mesh 很简单，Render Thread、Driver 和状态管理也可能成为瓶颈。合批能减少 Draw，但会降低剔除粒度并增加资源组织复杂度。

GPU-Driven 让 CPU 主要提交场景 Buffer、相机和少量 Dispatch/Indirect Draw。GPU 并行生成本帧可见工作集。

## 场景数据

常见 Buffer：

- Instance Transform、Previous Transform、Bounds；
- Mesh/LOD/Material ID；
- Vertex/Index 或 Cluster Data；
- Visibility/LOD History；
- Draw/Dispatch Argument；
- Visible Instance/Cluster List。

数据应使用稳定 ID。GPU Buffer 的 Slot 不应直接等同 Gameplay 对象地址，删除和新增需要 Free List、Generation 或其他生命周期机制。

## Frustum 与 Distance/Screen Error

Compute Culling 先用 Sphere/AABB 对 View Frustum。再根据距离、Projected Size 或 Screen-space Error 选择 LOD。

LOD 选择应有 Hysteresis，避免阈值附近来回切换。若精细 LOD 尚未流送，可回退到可用父级，不应等待 GPU/IO 同步。

## Backface Cone Culling

一个 Cluster 可预计算 Normal Cone：Axis 和最大偏转角。如果从相机看，整个 Cone 都背向视线，就能在光栅化前剔除整个 Cluster。

双面材质、负缩放、变形和非流形几何会让 Cone 假设失效。工具应按资产标记是否允许此剔除。

## Hi-Z Occlusion

Depth Pyramid 每级保存一块区域的保守深度。把 Bounds 投影到屏幕后，选择覆盖范围对应的 Mip，并比较最近可能深度与 Hi-Z。

Reversed-Z 下 Pyramid 取 Min/Max 的方向与普通 Depth 不同。必须按深度约定推导，不能照抄比较符号。

使用上一帧 Hi-Z 没有当前帧完整深度，快速相机移动或新出现遮挡会产生误判。保守方案：

- 扩张 Bounds；
- 仅剔除有历史稳定遮挡的对象；
- 先绘制上一帧可见集，生成当前深度；
- 再测试不确定对象并补绘；
- 对新实例和相机 Cut 强制可见。

Occlusion False Positive 会让物体消失，不能以错误剔除换性能。

Hi-Z 也常称 HZB（Hierarchical Z-Buffer）。两者都指深度的分层降采样结构；归约使用最大值还是最小值取决于正向或反向 Z 以及遮挡测试定义。

## Compaction 与 Prefix Sum

每个线程判断可见后，需要把结果紧凑写入 Visible List。可以使用 Atomic Append，简单但高密度时有竞争；也可先写 0/1 Flag，通过 Prefix Sum 得到输出 Offset，再 Scatter。

Prefix Sum 通常分组内 Scan、Group Sum Scan、最终 Offset Add。它是 GPU Culling、粒子系统和 Cluster Pipeline 的基础并行原语。

## Indirect Draw

GPU 把可见数量和参数写入 Indirect Argument Buffer，随后执行 `DrawIndexedIndirect`、`ExecuteIndirect` 或对应 API。CPU 不读取数量，避免同步。

若每个 Mesh/Material 仍要一条 Indirect Draw，提交数量只是从对象级降到批次级。Multi-draw、Bindless Resource、Mesh Shader 或统一 Visibility Pass 可以继续减少批次。

Indirect Argument 从 UAV 写入到 Indirect Read 需要 Barrier。计数溢出和 Buffer 容量不足必须有可观察错误。

## Material 与排序

可见几何需要按 Pipeline/Material 分类。常用：

- 每材质独立 Bin 和 Counter；
- 对 Material Key 做 Radix Sort；
- Visibility Buffer 先写 Primitive ID，后续统一 Shading；
- Bindless Descriptor 让 Shader 根据 Material ID 访问资源。

Bindless 降低绑定次数，却提高随机访问和资源生命周期要求。同一 Wave 中材质差异大也会产生 Divergence。

## Cluster 与 Meshlet

Cluster/Meshlet 把 Mesh 切成几十到几百个三角形的小块，并限制唯一顶点数。每块保存 Bounds、Normal Cone、Material Range 和局部索引。

收益：

- 比 Instance 更细的 Frustum/Backface/Occlusion Culling；
- 数据块适合 Cache 和并行处理；
- 可作为 Mesh Shader Work Unit；
- 可独立选择 LOD 和流送。

Cluster 太小会增加元数据和调度；太大则剔除不精细。最佳大小取决于硬件、几何和工作负载，不是固定 64/128 就通用。

## Mesh Shader

现代 Mesh Pipeline 常由 Task/Amplification Shader 产生工作组，再由 Mesh Shader 输出一组顶点和 Primitive。它能在 GPU 内完成 Cluster Culling、LOD 与解码，减少传统 Vertex/Geometry 阶段限制。

Mesh Shader 不是软件光栅化。它最终仍把 Primitive 交给硬件 Rasterizer。Compute Shader 自行覆盖像素、写 Visibility/Depth 才属于 Software Rasterization。

平台不支持 Mesh Shader 时，可使用 Compute Culling + Indirect Indexed Draw 作为回退。

## Visibility Buffer

Visibility Pass 只写 Instance/Primitive/Triangle ID 和 Barycentric 等最小数据。后续 Compute/Pixel Shading 根据 ID 读取顶点与材质，重建属性并着色。

优势：

- 几何可见性阶段 Shader 很轻；
- 被覆盖的几何不重复执行完整材质；
- 材质计算可按 Tile/Material 分类；
- 适合微三角形与 GPU-Driven 列表。

代价：

- 需要随机读取 Index/Vertex/Material；
- 属性导数、Texture LOD 和 MSAA 处理更复杂；
- 透明材质仍需其他路径；
- ID 格式和内存带宽需要设计。

## Nanite 解决的问题

Nanite 是 Unreal 的虚拟化几何系统。核心思想是把高密度三角形预处理成 Cluster 层级，根据当前视点选择满足 Screen-space Error 的局部几何，并按需流送所需 Page。

它不是“没有面数限制”，也不是运行时自动把任意几何变成无限细节。磁盘、内存、流送、材质、变形和像素预算仍然存在。

## Cluster Group 与简化层级

朴素方案若独立简化每个 Cluster，要么边界裂开，要么永久锁住边界导致高层 LOD 仍保留大量三角形。

Nanite 的公开设计以 Cluster Group 为简化单元：

1. 把一组 Cluster 合成 Group；
2. 锁住 Group 外边界；
3. 对 Group 内部整体简化；
4. 把简化结果重新聚类；
5. 在更高层重复。

不同层的 Group Boundary 会变化，父子关系不必是一对一树，可形成局部多对多的 DAG。这样能在保持某次简化边界水密的同时，避免同一边永久被锁住。

具体 Cluster 数量、三角形上限和内部布局会随引擎版本变化，理解时应关注职责，不把示例数字当接口保证。

## Screen-space Error 与 Cut

每个节点记录简化误差和 Bounds。运行时把 Object-space Error 投影到屏幕，判断该节点是否足够精细。

选择出的节点集合形成层级上的 Cut：既覆盖需要绘制的表面，又避免父子同时重复绘制。为了并行决定可见性，Error 传播必须满足层级一致性和单调关系。

相邻区域可选不同细节层，产生 View-dependent LOD。过渡稳定性依赖误差度量、边界构造、时间滞后和像素覆盖，不等于完全没有 Popping。

## Nanite 的 Culling 与 Raster

运行时先用层级 Bounds 减少需要检查的 Cluster，再做 Instance/Cluster Frustum、Backface 与 Occlusion Culling。

大三角形适合硬件 Rasterizer。极小三角形在固定 Rasterizer 中会受 Quad/Setup 效率影响，Compute Software Raster 可能更合适。实现可以按投影三角形尺寸选择路径，最终写入统一 Visibility/Depth 表示。

这不是“软件光栅永远更快”。性能取决于三角形尺寸、覆盖、原子写、硬件和实现。

## Page Streaming 与虚拟化

精细 Cluster 数据按 Page 存储。粗层级常驻，细节按 View Request 流送。请求从 GPU 可见性产生，经 CPU/IO 调度加载到 GPU Page Pool。

需要处理：

- Page Residency 和 Eviction；
- 请求去重与优先级；
- Camera Teleport 的峰值；
- 缺页时回退父级；
- 压缩与 GPU 解码；
- 多视图、阴影和反射带来的额外需求。

虚拟化把“全部常驻”改成“按需驻留”，不是取消内存预算。

几何 Page 可以对父级或相邻层级做增量编码，只保存可重建的差值，再使用 LZ 等无损压缩降低磁盘和传输体积。压缩率、随机访问粒度和解压吞吐需要一起设计：Page 太大增加无效传输，Page 太小会放大请求、元数据和 IO 开销。

DirectStorage 一类直接存储路径减少传统逐文件 CPU IO 和中间复制，让批量请求、GPU 可用压缩数据与上传队列更紧密地衔接。它不会消除资产调度问题，仍需要优先级、反馈延迟、驻留预算和缺页时的父级回退。

## 材质、透明与动态几何

高密度 Visibility Pipeline 对不透明/Masked 几何最自然。透明排序、像素深度偏移、任意顶点位移和复杂 Deformation 会破坏预计算 Bounds、层级与可见性假设。

Nanite 的具体支持范围会随 Unreal 版本扩展。笔记应按当前官方文档核对，不把早期限制或新实验特性写成永久结论。

传统 LOD、Skeletal Mesh、Impostor 和普通 Raster Pipeline 仍然需要，与虚拟化几何混合存在。

## 验证方法

- 统计输入 Instance/Cluster、各级 Culling 后数量和最终 Draw/Dispatch。
- 输出 Frustum、Backface、Occlusion、LOD Reject Reason。
- 测试 Camera Cut、快速移动、新生对象和遮挡物移动。
- 检查 Indirect Args、Barrier、Visible List 容量和溢出处理。
- 比较 CPU Render Thread、GPU Cull、Raster、Shade 和 Streaming 时间。
- 在不同三角形屏幕尺寸下区分 Setup、Coverage、Pixel 与 Atomic 成本。
- 对缺页回退、LOD Popping、裂缝、Masked Material 和 Motion Vector 做回归。

## 相关主题

- [[知识库/08_几何与网格/网格数据、缓存与几何处理]]
- [[知识库/08_几何与网格/LOD、地形与程序化资产]]
- [[知识库/13_引擎架构与资源系统/Draw Call、Batching与GPU Instancing]]
- [[知识库/14_性能分析与优化/帧时间、瓶颈与GPU成本]]

## 参考资料

- Epic Games, *A Deep Dive into Nanite Virtualized Geometry* and current Nanite documentation.
- Burns and Hunt, *The Visibility Buffer: A Cache-Friendly Approach to Deferred Shading*.
- NVIDIA and Microsoft Mesh Shader specifications and programming guides.
- Haar and Aaltonen, *GPU-Driven Rendering Pipelines* technical presentations.
