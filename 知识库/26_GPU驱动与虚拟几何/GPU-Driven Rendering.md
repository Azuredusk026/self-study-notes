# GPU-Driven Rendering

GPU-Driven Rendering 把可见性、LOD、实例列表和绘制参数尽量留在 GPU 内生成。目的是避免 CPU 每帧逐对象提交和读回大规模可见列表。CPU 仍负责场景更新、资源与批次调度，GPU 负责生成可见列表和绘制参数。

## 专题阅读

- [[26_GPU驱动与虚拟几何/Nanite几何选择与流送]]：Nanite 将高密度几何预处理为层级与分页数据，运行时按屏幕误差选择几何并流送细节。

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

### 引擎中的场景 Buffer

Unreal 的 GPUScene 是这类结构的具体实现。它把参与 GPUScene 路径的图元与实例数据维护在 GPU 侧的持久 Buffer 中，每帧只上传变化的部分——增量更新而非全量重传，这是场景规模能够扩展的前提。

与之配套的是延迟剔除（Deferred Culling）。流程是先注册、后收集、再统一剔除：

1. 帧初始化时创建剔除上下文并注册回调；
2. 各个 Pass 构建渲染命令时，把收集到的动态网格加入待剔除批次；
3. 收集完成后触发回调，更新 Compute Shader 所需的 Buffer；
4. 执行剔除 Pass，输出可见实例列表与 Indirect 绘制参数。

“先收集后剔除”正是“延迟”一词的含义。这样做的好处是把兼容的剔除工作集中成批次，减少 GPU 的启动开销与同步点。

需要区分两个同名概念：这里的实例剔除作用于普通图元的实例列表，与 Nanite 内部的 Cluster 级剔除是不同层级的机制，两者可以并存。

## 哪些实例进入工作集

### Frustum 与 Distance/Screen Error

Compute Culling 先用 Sphere/AABB 对 View Frustum。再根据距离、Projected Size 或 Screen-space Error 选择 LOD。

LOD 选择应有 Hysteresis，避免阈值附近来回切换。若精细 LOD 尚未流送，可回退到可用父级，不应等待 GPU/IO 同步。

### Backface Cone Culling

一个 Cluster 可预计算 Normal Cone：Axis 和最大偏转角。如果从相机看，整个 Cone 都背向视线，就能在光栅化前剔除整个 Cluster。

双面材质、负缩放、变形和非流形几何会让 Cone 假设失效。工具应按资产标记是否允许此剔除。

### Hi-Z Occlusion

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

## 可见列表怎样变成绘制

### Compaction 与 Prefix Sum

每个线程判断可见后，需要把结果紧凑写入 Visible List。可以使用 Atomic Append，简单但高密度时有竞争；也可先写 0/1 Flag，通过 Prefix Sum 得到输出 Offset，再 Scatter。

Prefix Sum 通常分组内 Scan、Group Sum Scan、最终 Offset Add。它是 GPU Culling、粒子系统和 Cluster Pipeline 的基础并行原语。

### Indirect Draw

GPU 把可见数量和参数写入 Indirect Argument Buffer，随后执行 `DrawIndexedIndirect`、`ExecuteIndirect` 或对应 API。CPU 不读取数量，避免同步。

若每个 Mesh/Material 仍要一条 Indirect Draw，提交数量只是从对象级降到批次级。Multi-draw、Bindless Resource、Mesh Shader 或统一 Visibility Pass 可以继续减少批次。

Indirect Argument 从 UAV 写入到 Indirect Read 需要 Barrier。计数溢出和 Buffer 容量不足必须有可观察错误。

### Material 与排序

可见几何需要按 Pipeline/Material 分类。常用：

- 每材质独立 Bin 和 Counter；
- 对 Material Key 做 Radix Sort；
- Visibility Buffer 先写 Primitive ID，后续统一 Shading；
- Bindless Descriptor 让 Shader 根据 Material ID 访问资源。

Bindless 降低绑定次数，却提高随机访问和资源生命周期要求。同一 Wave 中材质差异大也会产生 Divergence。

## 细粒度几何怎样处理

### Cluster 与 Meshlet

Cluster/Meshlet 把 Mesh 切成几十到几百个三角形的小块，并限制唯一顶点数。每块保存 Bounds、Normal Cone、Material Range 和局部索引。

收益：

- 比 Instance 更细的 Frustum/Backface/Occlusion Culling；
- 数据块适合 Cache 和并行处理；
- 可作为 Mesh Shader Work Unit；
- 可独立选择 LOD 和流送。

Cluster 太小会增加元数据和调度；太大则剔除不精细。最佳大小取决于硬件、几何和工作负载，不是固定 64/128 就通用。

### Mesh Shader

现代 Mesh Pipeline 常由 Task/Amplification Shader 产生工作组，再由 Mesh Shader 输出一组顶点和 Primitive。它能在 GPU 内完成 Cluster Culling、LOD 与解码，减少传统 Vertex/Geometry 阶段限制。

Mesh Shader 不是软件光栅化。它最终仍把 Primitive 交给硬件 Rasterizer。Compute Shader 自行覆盖像素、写 Visibility/Depth 才属于 Software Rasterization。

平台不支持 Mesh Shader 时，可使用 Compute Culling + Indirect Indexed Draw 作为回退。

### Visibility Buffer

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

## 验证方法

- 统计输入 Instance/Cluster、各级 Culling 后数量和最终 Draw/Dispatch。
- 输出 Frustum、Backface、Occlusion、LOD Reject Reason。
- 测试 Camera Cut、快速移动、新生对象和遮挡物移动。
- 检查 Indirect Args、Barrier、Visible List 容量和溢出处理。
- 比较 CPU Render Thread、GPU Cull、Raster、Shade 和 Streaming 时间。
- 在不同三角形屏幕尺寸下区分 Setup、Coverage、Pixel 与 Atomic 成本。
- 对缺页回退、LOD Popping、裂缝、Masked Material 和 Motion Vector 做回归。

### GPU 剔除与间接绘制列表

输入是实例 Bounds 与 Hi-Z，输出是紧凑可见实例索引。计数器和输出容量在 Dispatch 前准备好：

```hlsl
[numthreads(64, 1, 1)]
void CullInstances(uint id : SV_DispatchThreadID)
{
    if (id >= instanceCount) return;
    Bounds b = InstanceBounds[id];
    if (!IntersectsFrustum(b, viewFrustum)) return;
    if (IsOccludedByHiZ(b, hiZTexture)) return;
    uint dst;
    InterlockedAdd(VisibleCount[0], 1, dst);
    if (dst < visibleCapacity) VisibleInstances[dst] = id;
}
```

剔除前要保证 Hi-Z 对应当前约定的深度方向，并在写入可见列表后建立到 Indirect Draw 读取的同步。原子追加适合最小实现，大规模场景可用 Prefix Sum 做稳定压紧。验证时关闭各项剔除分别比较计数，并把 Bounds、Mip 选择和被拒绝原因可视化；这里的原子计数在容量溢出后仍会增长，因此最终绘制计数必须限制到已写入容量，并报告溢出。生产系统还要准备保守回退，避免缺失对象。仅在写数组时判断 `dst < visibleCapacity` 并不能修复间接绘制读取越界。

## 相关主题

- [[02_GPU与光栅化管线/几何着色器、曲面细分与流输出]]
- [[08_几何与网格/网格数据与GPU访问]]
- [[08_几何与网格/LOD、地形与程序化资产]]
- [[13_渲染架构/Draw Call与合批]]
- [[14_性能分析与优化/帧瓶颈怎么判断]]

## 参考资料

- Epic Games, *A Deep Dive into Nanite Virtualized Geometry* and current Nanite documentation.
- Burns and Hunt, *The Visibility Buffer: A Cache-Friendly Approach to Deferred Shading*.
- NVIDIA and Microsoft Mesh Shader specifications and programming guides.
- Haar and Aaltonen, *GPU-Driven Rendering Pipelines* technical presentations.
