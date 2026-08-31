# Compute Shader 与 GPU 执行模型

Compute Shader 让程序直接提交并行计算，不需要顶点、三角形和光栅化。它适合大量结构相似、能够并行拆分的任务。

## Dispatch 和线程索引

HLSL 用 `[numthreads(x,y,z)]` 声明每个 Thread Group 的线程数。CPU 调用 `Dispatch(gx,gy,gz)` 提交 Group 数量。

总线程数是：

$$
(gx\cdot x,\ gy\cdot y,\ gz\cdot z)
$$

常见系统值：

- Group ID：当前 Group 在 Dispatch 网格中的位置；
- Group Thread ID：线程在 Group 内的位置；
- Dispatch Thread ID：整个 Dispatch 中的全局位置；
- Group Index：把 Group 内三维索引压成一维。

计算纹理时通常要做边界判断，因为 Dispatch 尺寸经常向上取整到 Group 大小。

## Thread Group

同一 Group 的线程可以：

- 使用 `groupshared` 内存；
- 执行 Group Barrier；
- 合作加载 Tile、做 Reduction 或 Prefix Sum。

不同 Group 的执行顺序没有保证。普通 Dispatch 内不能用 Group Barrier 同步整个 Dispatch。需要全局阶段同步时，应拆成多个 Dispatch，并在 API/Render Graph 中建立资源依赖。

## Wave 和 Warp

GPU 会把线程分成硬件执行批次。NVIDIA 常称 Warp，DirectX 常称 Wave，AMD 文档也使用 Wavefront。

Wave 宽度可能是 32、64 或其他值，不能在跨平台 Shader 中写死，除非目标和 Feature 明确保证。

同一 Wave 通常按 SIMT 方式执行相同指令。遇到不同分支时，硬件可能分别执行各路径，再用 Mask 关闭不参与的 Lane。这就是 Branch Divergence。

## 分支什么时候危险

按像素随机变化的条件容易让同一 Wave 发散。按整个 Dispatch、材质或大块 Tile 一致的条件可能不会严重发散。

分支代价还取决于：

- 两侧工作量；
- 编译器是否展开或改写；
- 是否能提前退出大量昂贵循环；
- 发散持续多少条指令；
- 分支后的内存访问是否仍连续。

## `groupshared` 内存

Group Shared Memory 位于 Compute Unit/SM 附近，延迟低、带宽高，适合复用一个 Tile 数据。

典型模式：

1. 每个线程从全局资源加载一个元素；
2. 写入 `groupshared`；
3. 执行 Group Barrier；
4. 多个线程重复读取共享数据完成卷积或归约。

共享内存容量有限。每个 Group 用得越多，可同时驻留的 Group 可能越少。

## Barrier

Barrier 要区分两件事：

- 等待同组线程到达；
- 保证某类内存写入对其他线程可见。

不是所有 Barrier 都同时完成两者。应使用语言/API 中与目标内存范围匹配的语义。

如果只有部分线程进入 Barrier，其他线程走了不同分支，可能死锁或产生未定义结果。Barrier 应位于 Group 内一致控制流中。

## UAV 和原子操作

UAV/Storage Resource 支持无序读写。多个线程写同一地址会产生 Race Condition。

解决方法包括：

- 让每个线程写唯一位置；
- 使用原子操作；
- 先在 Group 内归约，再少量写回；
- 使用前缀和分配唯一索引；
- 拆分为多个阶段。

原子操作保证更新不丢失，但大量线程竞争同一地址会串行化。

## 内存访问和合并

相邻 Lane 访问连续地址时，硬件更容易合并内存事务并利用 Cache。随机跳跃访问会浪费带宽。

数据布局需要结合访问方式：

- AoS 适合一次读取一个对象的全部属性；
- SoA 适合大量线程只读取同一属性；
- 对齐和步长会影响事务数量；
- 纹理缓存适合具有空间局部性的采样。

## Occupancy

GPU 通过同时驻留多个 Wave 隐藏访存延迟。Occupancy 受以下资源限制：

- 每线程寄存器；
- 每 Group 共享内存；
- Group 线程数；
- 硬件最大 Wave/Group 数。

Occupancy 高不等于一定快。算法可能受带宽、指令吞吐或同步限制。它只是分析维度之一。

## 常见算法

### Reduction

把一组值求和、最小值或最大值。通常先在 Group Shared 中做树形归约，再写一个 Group 结果，继续下一阶段。

### Prefix Sum

计算每个元素之前的累计值。GPU Culling 中可以用它把“可见/不可见”标记转换成紧凑输出索引。

### Tiled Processing

把图像分成 Tile，在 Shared Memory 缓存包含边界的区域，再执行模糊、边缘检测或光源筛选。

### Indirect Argument Generation

Compute Shader 统计可见对象并写 Indirect Draw 参数，让后续绘制不回读 CPU。

## 调试与验证

- 检查 Dispatch 尺寸和边界条件。
- 用小输入在 CPU 上写参考实现，比对 GPU 结果。
- 使用 GPU Debugger 检查资源状态、UAV 和 Barrier。
- 测试不同 Group Size，不凭 8x8 或 16x16 的惯例决定。
- 查看寄存器、共享内存、Occupancy 和带宽指标。
- 对原子竞争和非确定顺序做压力测试。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[10_VFX与模拟/粒子系统与GPU模拟]]
- [[12_光追与现代渲染/GPU-Driven管线与Nanite]]
- [[14_性能分析与优化/帧时间、瓶颈与GPU成本]]

## 参考资料

- Microsoft Learn, *Compute Shader Overview* and *HLSL Shader Model 6 Wave Intrinsics*.
- Khronos, *Vulkan Specification*, Compute Pipelines and Memory Model.
- NVIDIA and AMD GPU architecture/performance guides.
