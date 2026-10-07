# GPU同步与屏障

Compute已经写出了结果，接下来的顶点Shader却读到旧数据，这时再调用一次Draw通常解决不了问题。GPU阶段可以重叠，命令排在后面不等于写入已对读取可见。我们沿着访问阶段、资源范围与队列关系，把必要依赖写成屏障，再用帧标记检查读者拿到的是哪次结果。

## GPU访问依赖

### 执行与内存依赖

同一队列接收的命令有规定顺序，不同流水线阶段仍可能重叠。计算写完缓冲以后，顶点阶段读取它，既要等相关写入发生，也要让结果可见。直接等待整次提交结束能建立更强边界，却把本可重叠的工作也停住了。

先分清数据关系。写后读关注新结果是否可见，读后写关注旧结果是否已读完；两次只读通常没有写入可见性问题。布局或队列所有权变化仍是另一项约束，因此只看“读”字并不能省掉全部状态处理。

Vulkan 的 stage mask 选择相关执行阶段，access mask 选择读写类型，layout 描述图像使用布局。D3D12 传统屏障用资源状态组合表达访问，增强屏障进一步区分同步、访问和布局。两者不能逐字段机械对应。

### Vulkan 写后读示例

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

### 图像布局与子资源

颜色附件写完再采样，需要从颜色附件布局转为合适的着色读取布局。屏障的 mip、数组层和 aspect 范围必须覆盖实际访问。深度模板、多个 mip 和 Cube 数组尤其容易出现范围遗漏。

把旧布局写成`UNDEFINED`就是允许丢弃旧内容。历史、部分更新或load还要读取原数据时，这个前提不成立。保留真实旧布局后，再让屏障覆盖布局转换和实际访问，才能解释读者读到了什么。

## 提交与队列

### 队列同步

```text
计算队列写结果 → signal 完成值
                      ↓
图形队列 wait 完成值 → 读取结果
                      ↓
CPU 等待本帧完成值 → 回收帧资源
```

Vulkan semaphore 用于 GPU 提交间依赖；fence 通常用于 CPU 查询或等待提交完成。Timeline semaphore 可以用递增值管理多个依赖。D3D12 fence 支持队列 signal、队列 wait 和 CPU 等待，名称相同不代表语义和 Vulkan fence 完全一致。

Vulkan 独占资源跨 queue family 使用时，通常还需要匹配的 release/acquire 所有权转移。并发共享模式与同 family 队列有不同规则；semaphore 等待也不能自动代替全部布局和归属处理。

### 异步计算的条件

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
- [[03_Shader编程/Compute Shader]]、[[03_Shader编程/GPU归约与前缀和]]、[[03_Shader编程/GPU异步回读]]

示例状态：本页代码用于解释对应的数据和调用约束，完整资源创建、类型与调用环境由项目提供。除文中另列的实际实验外，本页未执行目标引擎编译、GPU捕获或性能计时。

## 参考资料

- [Vulkan Synchronization](https://docs.vulkan.org/spec/latest/chapters/synchronization.html)，执行、内存、semaphore 与 fence。
- [Khronos Synchronization Examples](https://github.com/KhronosGroup/Vulkan-Docs/wiki/Synchronization-Examples)，实际访问的屏障对应。
- [D3D12 Resource Barriers](https://learn.microsoft.com/en-us/windows/win32/direct3d12/using-resource-barriers-to-synchronize-resource-states-in-direct3d-12)。
