# Command Buffer与帧提交

CPU刚记录完一帧，就把上传缓冲拿去写下一帧，看似节省了内存，GPU却可能还在读旧内容。命令记录、队列提交和GPU完成发生在不同时间。我们沿这三个时刻追踪每个帧槽位的资源，完成值达到以后再复用，就能解释在途帧既影响吞吐也影响寿命。

## 命令记录与完成

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

以下是 D3D12 调用顺序轮廓，输入为一组帧资源。完成事件已创建为自动复位事件，由当前等待者独占；交换链获取由宿主提供；`RecordFrame`在记录端验证输入，API记录错误还会由Close返回。`nextFence` 全局递增；`HandleSubmissionFailure`按下节规则停止正常帧循环并处理提交故障。

```cpp
Frame& frame = frames[frameSlot];
UINT64 completed = fence->GetCompletedValue();
if (completed == UINT64_MAX) {
    HandleSubmissionFailure(DXGI_ERROR_DEVICE_REMOVED);
    return;
}
while (completed < frame.completionValue) {
    HRESULT eventResult = fence->SetEventOnCompletion(
        frame.completionValue, completionEvent);
    if (FAILED(eventResult)) {
        HandleSubmissionFailure(eventResult);
        return;
    }
    DWORD waitResult = WaitForSingleObject(completionEvent, INFINITE);
    if (waitResult != WAIT_OBJECT_0) {
        HRESULT error = waitResult == WAIT_FAILED
            ? HRESULT_FROM_WIN32(GetLastError()) : E_FAIL;
        HandleSubmissionFailure(error);
        return;
    }
    completed = fence->GetCompletedValue();
    if (completed == UINT64_MAX) {
        HandleSubmissionFailure(DXGI_ERROR_DEVICE_REMOVED);
        return;
    }
}
HRESULT resetResult = frame.allocator->Reset();
if (FAILED(resetResult)) {
    HandleSubmissionFailure(resetResult);
    return;
}
resetResult = commandList->Reset(frame.allocator.Get(), initialPipeline);
if (FAILED(resetResult)) {
    HandleSubmissionFailure(resetResult);
    return;
}
RecordFrame(commandList.Get(), frame);
HRESULT closeResult = commandList->Close();
if (FAILED(closeResult)) {
    HandleSubmissionFailure(closeResult);
    return; // 此列表没有提交，不能继续Execute
}
ID3D12CommandList* lists[] = {commandList.Get()};
queue->ExecuteCommandLists(1, lists);
const UINT64 submittedValue = nextFence++;
HRESULT signalResult = queue->Signal(fence.Get(), submittedValue);
if (FAILED(signalResult)) {
    HandleSubmissionFailure(signalResult); // 停止复用，进入下节故障路径
    return;
}
frame.completionValue = submittedValue;
```

示例在同一队列提交后signal，完成值覆盖它之前的工作。多队列共同使用同一资源时，回收还要覆盖所有相关队列的最后访问。allocator重置会回收命令内存，所以它分配的命令都完成后才能重置。上传区间和描述符回收采用相同的完成条件。命令列表对象复用与 allocator 内存重置有不同限制，不能仅以对象名称判断。

例如帧槽位 0 记录完成值 17，CPU 准备再次使用它时完成值只有 16，仍需等待。即使交换链本次返回图像索引 0，也不能把它当作完成 17 的证据。若资源又被复制队列使用到值 9，单看图形队列 17 也不够；可以保存各队列完成条件，或建立汇合依赖后使用一个覆盖全部工作的完成值。

### 提交失败与资源状态

帧槽位在可复用、记录中、已提交三个状态间移动。Reset失败就退出记录，Close失败就退出提交；这时本次命令尚未进入队列，可以保留诊断并清理未提交记录。D3D12中Close失败的命令列表之后也不能Reset成功，恢复时重建该列表，而不是在下一帧原样重试。Execute之后即使后续Signal失败，也不能把槽位当成“未提交”立即覆盖，因为GPU可能已经消费命令。应用进入设备/提交故障处理，停止复用依赖该完成值的资源，确认队列或设备已终止后再销毁。示例调用序列在每一步成功的路径上成立，错误返回不产生虚假的GPU完成事实。

`GetCompletedValue`在设备移除时返回UINT64_MAX，这不是“全部命令已经正常完成”的证明。若只比较数值大小，设备故障会被误判为可以重置所有帧槽位；示例在等待前后都先识别这个哨兵值并转入故障路径。事件注册失败直接离开等待路径；事件唤醒后重新查询完成值，满足本槽位条件才继续。唤醒本身不充当GPU完成证据。完成值计数不分配UINT64_MAX，并在接近回绕时排空与重建该计数纪元。

正常路径可以提前给本帧预留唯一完成值，Signal成功后将它登记为槽位的回收条件；上传、描述符和allocator都挂到这个条件。只供CPU组织命令的场景快照可以在所有记录任务结束后回收，但写进命令的资源、描述符页和材质版本必须由记录结果继续持有。列表已Close、尚在协调者队列里等待提交时，GPU完成值还不能代表这份引用的寿命。

协调者把记录结果从Recorded切换到Submitting时，将整批引用交给提交记录，再释放录制持有，交接期间始终有人持有资源。提交成功后，引用等到覆盖所有消费者队列的完成条件成立才释放。取消只能取得尚未提交的记录结果；先通知记录任务停止并等待它们退出，再销毁列表及其引用。取消与提交竞争同一个状态转换，已经进入Submitting的批次由提交或故障路径处理。具体描述符、材质版本和纹理的联合持有见 [[13_渲染架构/GPU资源绑定]]。

## 记录与排队策略

### 多线程记录

不同线程可以记录相互独立的命令列表。每条列表使用满足 API 线程约束的分配器或命令池，并共享只读的场景快照。录制顺序在 CPU 上无关，提交顺序与资源依赖仍需统一组织。

渲染线程和 RHI 线程是引擎的软件分工，GPU graphics/compute/copy queue 是硬件提交接口，两者不一一对应。线程数更多可能降低记录耗时，也可能增加小任务调度与锁竞争。

### 记录结果与提交顺序

假设阴影列表S写深度D，主列表L读取D。CPU线程先录完L、后录完S并不构成错误，因为记录只是保存命令；协调线程仍按S、依赖转换、L提交。若按线程完成顺序提交L、S，L就可能读到上一帧的D。两个列表各自合法也不能修复跨列表依赖，协调者须根据读写关系生成顺序和屏障，具体访问规则见 [[13_渲染架构/GPU同步与屏障]]。

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

- [[02_GPU与光栅化管线/渲染帧流程]]
- [[13_渲染架构/GPU同步与屏障]]
- [[13_渲染架构/GPU资源生命周期]]

示例状态：本页代码用于解释对应的数据和调用约束，完整资源创建、类型与调用环境由项目提供。除文中另列的实际实验外，本页未执行目标引擎编译、GPU捕获或性能计时。

## 参考资料

- [Microsoft：ID3D12GraphicsCommandList::Reset](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12graphicscommandlist-reset)、[Close](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12graphicscommandlist-close)：2026-10-23核读HRESULT失败路径及Close失败后的列表状态。

- [Microsoft：ID3D12Fence::GetCompletedValue](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12fence-getcompletedvalue)：2026-10-23核读设备移除返回UINT64_MAX的语义。

- [Microsoft：SetEventOnCompletion](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12fence-seteventoncompletion)：事件注册具有HRESULT失败路径。
- [D3D12 Command Queues and Lists](https://learn.microsoft.com/en-us/windows/win32/direct3d12/command-queues-and-command-lists)。
- [Vulkan Command Buffers](https://docs.vulkan.org/spec/latest/chapters/cmdbuffers.html)，pending 状态与重用限制。
- [Vulkan Frames in Flight](https://docs.vulkan.org/tutorial/latest/03_Drawing_a_triangle/03_Drawing/03_Frames_in_flight.html)。
