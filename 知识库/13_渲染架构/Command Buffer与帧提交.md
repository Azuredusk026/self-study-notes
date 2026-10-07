# Command Buffer与帧提交

CPU刚记录完一帧，就把上传缓冲拿去写下一帧，看似节省了内存，GPU却可能还在读旧内容。命令记录、队列提交和GPU完成发生在不同时间。我们沿这三个时刻追踪每个帧槽位的资源，完成值达到以后再复用，就能解释在途帧既影响吞吐也影响寿命。

## 记录到完成

### 一帧的所有权

```text
游戏状态快照 → 渲染线程组织通道 → 记录命令
                                      ↓
                               队列提交并 signal
                                      ↓
                          GPU 完成 → 帧资源可复用
```

每个在途帧有自己的allocator、上传区间和描述符暂存。把最后提交的完成值记在槽位里，下次复用先检查这个值，就能知道旧GPU工作是否仍在使用它。交换链图像索引只指出这次取得的显示图像，不一定等于CPU帧资源槽位，两者分别管理。

### D3D12 的安全复用

以下是 D3D12 调用顺序轮廓，输入为一组帧资源。完成事件已创建，错误处理与交换链获取省略。`nextFence` 全局递增。

```cpp
Frame& frame = frames[frameSlot];
if (fence->GetCompletedValue() < frame.completionValue) {
    fence->SetEventOnCompletion(frame.completionValue, completionEvent);
    WaitForSingleObject(completionEvent, INFINITE);
}
frame.allocator->Reset();
commandList->Reset(frame.allocator.Get(), initialPipeline);
RecordFrame(commandList.Get(), frame);
commandList->Close();
ID3D12CommandList* lists[] = {commandList.Get()};
queue->ExecuteCommandLists(1, lists);
frame.completionValue = nextFence++;
queue->Signal(fence.Get(), frame.completionValue);
```

示例在同一队列提交后signal，完成值覆盖它之前的工作。多队列共同使用同一资源时，回收还要覆盖所有相关队列的最后访问。allocator重置会回收命令内存，所以它分配的命令都完成后才能重置。上传区间和描述符回收采用相同的完成条件。命令列表对象复用与 allocator 内存重置有不同限制，不能仅以对象名称判断。

## 记录与排队策略

### 多线程记录

不同线程可以记录相互独立的命令列表。每条列表使用满足 API 线程约束的分配器或命令池，并共享只读的场景快照。录制顺序在 CPU 上无关，提交顺序与资源依赖仍需统一组织。

渲染线程和 RHI 线程是引擎的软件分工，GPU graphics/compute/copy queue 是硬件提交接口，两者不一一对应。线程数更多可能降低记录耗时，也可能增加小任务调度与锁竞争。

### 在途帧数量

更多在途帧能让 CPU 和 GPU 重叠，也增加未呈现工作的排队量、内存和潜在输入延迟。帧资源环的大小、交换链缓冲数、present 模式和引擎限帧共同决定实际延迟，不能把“缓冲数为三”直接等同于三帧输入延迟。

CPU 读回需要确认复制完成；每帧立即等待会截断 CPU/GPU 并行。非实时决策可采用延迟几帧读取，结果附原始帧号。

## 引擎映射

### 引擎对应

Unity `ScriptableRenderContext.Submit` 提交已组织的渲染工作，资源释放应交给对应生命周期接口。Unreal 渲染线程和 RHI 命令列表将平台无关请求转交后端。两者的 CPU 标记时间需与 GPU 时间区分。

## 验证方法

- 增加 GPU 负载，让 CPU 快速循环；检查上传数据是否跨帧串色或命令 allocator 重置时报错。
- 改变在途帧数量，记录 CPU 等待、GPU 空闲、内存峰值和输入到显示延迟。
- 用不同帧标记做异步回读，确认返回帧号与提交记录一致。
- 暂时单线程录制，再对比多线程版本输出与记录开销，排除共享可变状态问题。

## 相关主题

- [[02_GPU与光栅化管线/一帧如何到达屏幕]]
- [[13_渲染架构/GPU同步与屏障]]
- [[13_渲染架构/GPU资源生命周期]]

示例状态：本页代码用于解释对应的数据和调用约束，完整资源创建、类型与调用环境由项目提供。除文中另列的实际实验外，本页未执行目标引擎编译、GPU捕获或性能计时。

## 参考资料

- [D3D12 Command Queues and Lists](https://learn.microsoft.com/en-us/windows/win32/direct3d12/command-queues-and-command-lists)。
- [Vulkan Command Buffers](https://docs.vulkan.org/spec/latest/chapters/cmdbuffers.html)，pending 状态与重用限制。
- [Vulkan Frames in Flight](https://docs.vulkan.org/tutorial/latest/03_Drawing_a_triangle/03_Drawing/03_Frames_in_flight.html)。
