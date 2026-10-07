# GPU资源生命周期

纹理对象在CPU上已经析构，GPU仍可能持有未完成的读取。反过来，图内句柄结束也不意味着物理内存立刻释放。要把这几种寿命分开：内容何时有效、分配何时可复用，以及最后一条GPU访问何时完成。上传、回读、临时纹理和历史都沿这条规则管理。

## 内容与完成边界

### 帧内与跨帧资源

帧内模糊中间纹理只服务于少数通道，可以由渲染图管理。TAA 历史、阴影缓存和常驻材质纹理跨帧使用，需要外部所有者管理创建、重建和回收。动态分辨率、格式变化或相机切换可能使历史失效，应在采样前检测描述变化并清除。

```text
逻辑资源创建 → 首次完整写入 → 后续读取 → 最后访问
                                       ↓
                              GPU 完成后物理回收
```

## 数据传输

### 上传与回读

D3D12 upload heap、Vulkan host-visible 内存适合 CPU 写入，再交 GPU 使用。并非所有 host-visible 内存都同样快，也不能假设 CPU/GPU 共享物理内存便无需同步。

Vulkan 非 coherent 内存的 CPU 写入需按规范 flush，对齐范围涉及 `nonCoherentAtomSize`。GPU 写入后的 CPU 读取需先确认执行完成，再按需要 invalidate。coherent 免除部分缓存管理，不免除执行依赖。

离散 GPU 常把频繁使用的数据复制到 device-local 内存；统一内存设备要按平台缓存和存储模式选择。回读可先复制到 readback/staging 资源，再在完成值满足后读取。

### 环形上传区间

下面是数据结构伪代码。分配器记录每段最后使用的提交完成值，只有已完成段可以复用。

```text
Allocate(bytes, alignment):
    begin = AlignUp(writeCursor, alignment)
    region = FindFreeRange(begin, bytes)
    if region overlaps an in-flight range:
        grow the ring or wait for its completion value
    writeCursor = region.end
    return region

Submit(region, value):
    inFlight.push(region, value)

Collect(completedValue):
    while oldest.value <= completedValue:
        free(oldest.region)
```

分配与提交可能由多个线程执行，需要统一排序或锁。环回时不能跨越未完成区间。等待会限制吞吐，扩容会增加峰值内存，选择依据是预算与可接受等待。

## 分配与复用

### 池复用与堆别名

资源池重用一个已创建纹理对象，可以减少频繁创建。堆别名让不同资源对象共享物理内存，要求寿命不重叠、分配兼容并处理别名屏障。池里没有CPU使用者，只说明应用暂时不取它；GPU上一帧可能仍在访问。因此池命中也要检查完成值。

渲染图资源导入可以表达外部纹理的读写，是否参与具体分配优化由引擎决定。CPU 引用计数不能独立证明 GPU 使用结束。

### 驻留与内存预算

虚拟地址、已分配堆和实际驻留内存不同。超出设备预算可能触发迁移、淘汰或分配失败。统计时区分常驻资源、缓存、在途上传、帧临时峰值和引擎保留池。单看进程总内存难以解释 GPU 抖动。

## 验证方法

- 将 GPU 负载拉长，快速循环上传和销毁，确认旧帧内容不会被覆盖。
- 记录资源创建数、池命中、待回收字节和完成值；停止提交后待回收量应逐步下降。
- 开关图内别名，检查图像一致性和内存峰值。
- 改变分辨率、相机数量和历史格式，检查旧历史是否被安全替换。
- 异步回读附帧号，确认 CPU 不把延迟结果用于错误的当前帧。

## 相关主题

- [[13_渲染架构/Command Buffer与帧提交]]
- [[13_渲染架构/Render Graph]]
- [[16_编程与数据结构/内存布局与分配]]、[[16_编程与数据结构/对象生命周期]]、[[23_引擎运行系统/Unreal对象生命周期]]、[[23_引擎运行系统/Unity对象生命周期]]、[[16_编程与数据结构/对象池]]

示例状态：本页代码用于解释对应的数据和调用约束，完整资源创建、类型与调用环境由项目提供。除文中另列的实际实验外，本页未执行目标引擎编译、GPU捕获或性能计时。

## 参考资料

- [D3D12 Heap Types](https://learn.microsoft.com/en-us/windows/win32/direct3d12/upload-and-readback-of-texture-data)。
- [Vulkan Memory Allocation](https://docs.vulkan.org/spec/latest/chapters/memory.html)，coherent、flush、invalidate 与绑定。
- Unreal RDG 官方文档，外部资源导入、导出和 transient allocator。
