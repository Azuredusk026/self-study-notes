# Nanite几何选择与流送

Nanite 将高密度几何预处理为层级与分页数据，运行时按屏幕误差选择几何并流送细节。其构建、选择和缺页回退需要一起理解，通用 GPU 剔除流程由相关专题解释。

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

## 层级选择的算法轮廓

以下为通用层级切面选择伪代码，解释覆盖和细节选择，不代表 Nanite 源码逐行实现。输入节点保存屏幕误差、子节点和驻留信息，输出是互不重复的绘制集合。

```text
Select(node, view):
    if ConservativelyInvisible(node.bounds, view): return
    error = ProjectError(node.error, node.bounds, view)
    if error <= threshold or node.hasNoChildren:
        Emit(node)
        return
    if AllRequiredChildrenResident(node):
        for child in node.children:
            Select(child, view)
    else:
        RequestMissingPages(node)
        EmitResidentFallback(node)
```

真实 DAG 选择还需处理组边界、父子误差一致性和多视图请求。缺页时保留可绘制粗层，不能直接省略表面。用逐级阈值变化检验覆盖完整，并检查父子不会同时重叠绘制。

## 验证方法

- 使用 Nanite 可视化查看层级选择、实例与 cluster 数量。
- 固定镜头记录 streaming 请求，再瞬移检查粗层回退和细节恢复。
- 对 Masked、位移、动态几何和阴影分别按目标 UE 版本验证。
- 记录 GPU culling、raster、材质和 page pool 成本。

## 相关主题

- [[02_GPU与光栅化管线/几何着色器、曲面细分与流输出]]
- [[08_几何与网格/网格数据与GPU访问]]
- [[08_几何与网格/LOD、地形与程序化资产]]
- [[13_渲染架构/Draw Call与合批]]
- [[14_性能分析与优化/帧瓶颈怎么判断]]

- [[26_GPU驱动与虚拟几何/GPU-Driven Rendering]]

## 参考资料

- Epic Games, *A Deep Dive into Nanite Virtualized Geometry* and current Nanite documentation.
- Burns and Hunt, *The Visibility Buffer: A Cache-Friendly Approach to Deferred Shading*.
- NVIDIA and Microsoft Mesh Shader specifications and programming guides.
- Haar and Aaltonen, *GPU-Driven Rendering Pipelines* technical presentations.
