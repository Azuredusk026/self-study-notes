# GPU异步回读

CPU立即读取刚算出的GPU结果，会等待前面整条队列。异步回读先安排复制，后续再使用已完成请求；它把等待转成数据年龄，因此完成值、容量与失效策略是同一条实现链。

## 异步回读与延迟数据

结果需要回到 CPU 时（例如 CPU 侧执行剔除），同步回读会让 CPU 硬等 GPU，形成流水线停顿。异步回读避免了等待，但结果要几帧之后才能取到。

工程做法是维护一个环形队列：本帧使用最新已完成的回读结果，同时提交本帧的新请求。队列长度取决于可容忍的延迟。

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

## 验证方法

用递增帧编号写入请求，CPU同时显示生产帧、完成帧与使用帧。测试取消、场景卸载、请求失败和环容量耗尽。结果过期时采用保守行为，源资源必须活到复制结束。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[13_渲染架构/GPU资源生命周期]]
- [[02_GPU与光栅化管线/基于深度的可见性优化]]
- [[03_Shader编程/Compute Shader]]
- [[03_Shader编程/GPU归约与前缀和]]

## 参考资料

- Microsoft Learn, *Compute Shader Overview* and *HLSL Shader Model 6 Wave Intrinsics*.
- Khronos, *Vulkan Specification*, Compute Pipelines and Memory Model.
- NVIDIA and AMD GPU architecture/performance guides.
- LearnOpenGL, `src/8.guest/2022/5.computeshader_helloworld`.
