# GPU异步回读

CPU立即读取刚算出的GPU结果，会等待前面整条队列。异步回读先安排复制，后续再使用已完成请求；它把等待转成数据年龄，因此完成值、容量与失效策略是同一条实现链。

## 异步回读与延迟数据

结果需要回到 CPU 时（例如 CPU 侧执行剔除），同步回读会让 CPU 硬等 GPU，形成流水线停顿。异步回读把等待从当前CPU调用移到请求完成之后，仍占用复制与带宽，完成延迟由队列负载决定。

工程做法是维护一个环形队列：本帧使用最新已完成的回读结果，同时提交本帧的新请求。队列长度受请求频率、完成延迟与内存预算共同约束。所有槽仍在途时，可以跳过本帧请求，不能覆盖GPU尚在写的回读区。

旧数据可能因相机或场景变化失效，因此消费前检查年龄与产生条件。以遮挡剔除为例：

```csharp
var isTooFarAway = Vector3.Distance(currentCameraPosWS, recordCameraPosWS) >= maxCameraDistance;
var isDifferentDir = Vector3.Dot(currentCameraForwardWS, recordCameraForwardWS) <= minDirectionCosine;
var isStale = frameAge > maxResultAge;

if (isTooFarAway || isDifferentDir || isStale)
{
    SkipCullingThisFrame();
}
```

这是Unity风格C#条件片段，阈值来自项目空间与延迟预算；相机变化检查不能保证场景遮挡未变，还要检查场景版本或对象变化。实际Unity运行UNVERIFIED。失效策略的方向必须是保守的：剔除失效时宁可多提交绘制，也不能漏画——多画只是掉帧，漏画是可见的画面错误。

## 请求完成与发布

每条请求保存生产序号、场景代次、相机条件和状态。状态至少包括空闲、在途和可消费；CPU读取回调数据后复制到自己持有的结果缓冲，再释放槽位。取消业务消费只增加场景代次，已经提交的GPU复制仍按其完成事件回收资源。

```text
提交：找到空闲槽，保存(sequence, sceneEpoch)，发出请求；满队列则跳过
完成：先检查错误；成功时在API允许的数据寿命内复制结果
发布：请求epoch等于当前epoch，且sequence大于已发布序号时替换结果
回收：无论是否发布，都在复制完成后把槽标为空闲
消费：检查数据年龄、相机条件和场景变化；不满足时使用保守结果
```

例如序号9先完成并发布，序号8随后完成，8只回收槽位，不覆盖9。这可以避免完成顺序把“最新结果”退回过去。场景卸载后即使旧请求成功，也因代次不同而丢弃发布；其源资源和回读内存仍须保留到复制完成。

Unity 6000.0的`AsyncGPUReadbackRequest`结果只在成功完成后的一帧内可访问，随后请求由内部释放。轮询时同时检查`done`与`hasError`，需要长期保留的数据及时复制；持有请求结构体并不会延长`GetData`返回视图的寿命。`WaitForCompletion`会引入等待，应只用于明确接受阻塞的关闭或工具流程。

三个槽的状态可以按提交与完成事件逐项追踪。帧10提交请求10到槽0，帧11提交11到槽1，帧12提交12到槽2；在任何请求完成前，帧13没有空槽，跳过新请求。若12先完成，复制并发布12后释放槽2；10随后完成只释放槽0，不把已发布序号降到10。帧14可把新请求14写入槽0，前提是10的复制已经物理完成。

若此时场景代次从4改为5，仍在途的11携带代次4，完成后只能回收。新请求同时携带代次5；业务取消改变发布资格，并没有让GPU停止写旧槽。逐槽保存代次和序号可区分“结果不再需要”与“存储已经安全复用”。

## 验证方法

用递增帧编号写入请求，CPU同时显示生产帧、完成帧与使用帧。测试取消、场景卸载、请求失败和环容量耗尽。结果过期时采用保守行为，源资源必须活到复制结束。

实现状态：[shader_models.py](../examples/revision/shader_models.py)与[test_shader.py](../examples/revision/test_shader.py)检查满队列、乱序完成、请求失败和代次失效后的回收。它是CPU状态模型，不模拟实际GPU复制；Unity回调、资源释放和帧内数据寿命需在目标工程验证。

## 相关主题

- [[13_渲染架构/GPU资源生命周期]]
- [[02_GPU与光栅化管线/基于深度的可见性优化]]
- [[03_Shader编程/Compute Shader]]
- [[03_Shader编程/GPU归约与前缀和]]

## 参考资料

- [Unity 6000.0 AsyncGPUReadbackRequest](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Rendering.AsyncGPUReadbackRequest.html)：2026-10-22核读Description，支持done/hasError检查与结果只保持一帧的生命周期。
- 状态模型以逻辑取消和物理完成分离为前提，运行 `python -B 知识库/examples/revision/test_shader.py`。
