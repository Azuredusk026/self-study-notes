# GPU同步与屏障

GPU 同步需要回答：哪次访问必须先完成，哪些写入要对后续读取可见，资源当前采用什么布局，以及哪条队列拥有使用权。屏障表达这些依赖，不能用一条笼统的“等待 GPU”代替全部语义。

## 执行与内存依赖

同一队列按规定接受命令，但不同流水线阶段可以重叠。计算写缓冲后，顶点阶段读取该缓冲，需要写入可见性和阶段依赖。等待命令提交完成是更强的操作，通常会损失并行。

写后读通常同时需要执行与内存依赖。读后写重点是防止覆盖仍在读取的数据。只读访问之间通常不需要内存屏障，但纹理布局和队列所有权依然受 API 规则约束。

Vulkan 的 stage mask 选择相关执行阶段，access mask 选择读写类型，layout 描述图像使用布局。D3D12 传统屏障用资源状态组合表达访问，增强屏障进一步区分同步、访问和布局。两者不能逐字段机械对应。

## Vulkan 写后读示例

以下使用 Vulkan 1.3 `synchronization2`，缓冲由计算着色器写入，再作为顶点存储缓冲读取。示例省略命令池与资源创建，缓冲在同一队列使用。

```cpp
VkBufferMemoryBarrier2 barrier{};
barrier.sType = VK_STRUCTURE_TYPE_BUFFER_MEMORY_BARRIER_2;
barrier.srcStageMask = VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT;
barrier.srcAccessMask = VK_ACCESS_2_SHADER_STORAGE_WRITE_BIT;
barrier.dstStageMask = VK_PIPELINE_STAGE_2_VERTEX_SHADER_BIT;
barrier.dstAccessMask = VK_ACCESS_2_SHADER_STORAGE_READ_BIT;
barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
barrier.buffer = particleBuffer;
barrier.offset = 0;
barrier.size = VK_WHOLE_SIZE;
VkDependencyInfo dependency{};
dependency.sType = VK_STRUCTURE_TYPE_DEPENDENCY_INFO;
dependency.bufferMemoryBarrierCount = 1;
dependency.pBufferMemoryBarriers = &barrier;
vkCmdPipelineBarrier2(commandBuffer, &dependency);
```

若后续用同一缓冲作为顶点输入，目标应改为顶点属性输入阶段和相应 access；作为间接参数时则使用 draw-indirect 和 indirect-command-read。同步对象应对应真实使用方式。

## 图像布局与子资源

颜色附件写完再采样，需要从颜色附件布局转为合适的着色读取布局。屏障的 mip、数组层和 aspect 范围必须覆盖实际访问。深度模板、多个 mip 和 Cube 数组尤其容易出现范围遗漏。

使用 `UNDEFINED` 作为旧布局表示旧内容可以丢弃。历史缓冲、部分区域更新或需要 load 的附件应保留真实旧布局。布局转换自身也可能访问内存，需要纳入依赖。

## 队列同步

```text
计算队列写结果 → signal 完成值
                      ↓
图形队列 wait 完成值 → 读取结果
                      ↓
CPU 等待本帧完成值 → 回收帧资源
```

Vulkan semaphore 用于 GPU 提交间依赖；fence 通常用于 CPU 查询或等待提交完成。Timeline semaphore 可以用递增值管理多个依赖。D3D12 fence 支持队列 signal、队列 wait 和 CPU 等待，名称相同不代表语义和 Vulkan fence 完全一致。

Vulkan 独占资源跨 queue family 使用时，通常还需要匹配的 release/acquire 所有权转移。并发共享模式与同 family 队列有不同规则；semaphore 等待也不能自动代替全部布局和归属处理。

## 异步计算的条件

异步计算适合填补图形路径未用满的执行资源。两条队列都饱和于带宽或同类运算时，竞争可能延长总帧时间。要比较整帧关键路径，而不只看计算通道自身时间。

过早等待会把可重叠工作串起来，过晚等待则可能读未完成结果。渲染图可以推导依赖，但应用必须正确声明读写和跨帧资源。

## 验证方法

- 开启 Vulkan validation 的同步检查，或目标 D3D12 调试层，解决真实报告的读写冲突。
- 将相关任务暂时串行化，若伪影消失，再检查访问范围、布局与完成值。
- 在 GPU 队列时间线上检查 signal/wait 的位置，比较异步开关后的整帧耗时。
- 用每帧不同的标记写入缓冲，在读者输出中检查是否读到旧帧或未初始化值。

调试层未报告错误不等于自动证明同步完备。执行检查、资源可视化和目标硬件压力测试需要结合使用。

## 相关主题

- [[13_渲染架构/Render Graph]]
- [[13_渲染架构/Command Buffer与帧提交]]
- [[03_Shader编程/Compute Shader与GPU执行模型]]

## 参考资料

- [Vulkan Synchronization](https://docs.vulkan.org/spec/latest/chapters/synchronization.html)，执行、内存、semaphore 与 fence。
- [Khronos Synchronization Examples](https://github.com/KhronosGroup/Vulkan-Docs/wiki/Synchronization-Examples)，实际访问的屏障对应。
- [D3D12 Resource Barriers](https://learn.microsoft.com/en-us/windows/win32/direct3d12/using-resource-barriers-to-synchronize-resource-states-in-direct3d-12)。
