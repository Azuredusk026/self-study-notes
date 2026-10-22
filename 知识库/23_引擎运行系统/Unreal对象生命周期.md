# Unreal对象生命周期

普通C++指针指向UObject，并不自然成为GC根。Unreal通过可追踪引用维护可达性，原生对象智能指针则是另一套机制。字段标记、显式引用收集和销毁状态需要沿目标版本核对。

## 版本与GC模型

本页采用UE5.6的Object Pointers与Incremental Garbage Collection文档，2026-10-22核读。增量可达性分析在该版本文档中为实验特性，实际启用设置、模块代码与运行时表现分别核验。

Unreal 在 C++ 之上为 `UObject` 建立了一套独立的自动内存管理，与原生 C++ 的 RAII 并行存在。两套机制的边界是工程中最容易出错的地方。

### 标记—清除

核心算法是标记—清除：以 Root 集合中的对象为起点，递归遍历引用链，能到达的标记为可达；清理阶段回收所有未标记对象。

标记遍历引用关系，清理执行对象销毁。两者耗时都受对象数量、引用边、cluster与配置影响。UE5部分版本提供增量可达性分析，不能把标记永久描述为单帧不可拆。目标源码、GC配置与实际时间线要一起核对。

### 可追踪引用

引用链只认引擎能够识别的引用，普通的 C++ 指针不在其列：

- `UObject*` 成员被 `UPROPERTY` 宏标记，自动纳入引用链；
- 对象实现 `AddReferencedObjects` 接口，手动登记引用；
- 未由反射系统追踪的非UObject宿主，可以通过FGCObject等机制显式收集引用。反射结构体中的UPROPERTY引用是否可达，还取决于其宿主是否被追踪。

裸 `UObject*` 成员不被 GC 感知——对象可能在持有者毫不知情时被回收，留下悬垂指针。这是 UE 新手最常见的崩溃原因，且现象具有延迟性：崩溃发生在某次 GC 之后，而非写下代码之处。

可达性可由Root、被追踪的强引用、`FGCObject`引用收集或`TStrongObjectPtr`保持。容器中的强引用仍依赖其宿主被追踪；单独在普通C++结构里写一个`TObjectPtr`字段，不会自动把结构纳入对象图。

### 与智能指针的分工

Unreal 有两套并行的生命周期管理，用错会同时失去两者的保障：

| 对象类型 | 管理方式 |
|---|---|
| `UObject` 派生类 | GC管理，反射字段中的UPROPERTY/TObjectPtr或显式引用收集 |
| 非 UObject 的 C++ 类 | 原生所有权智能指针；Shared/Weak属于共享引用计数体系，Unique表示独占所有权 |
| Slate 控件 | 引用计数智能指针 |

**不要用共享指针持有 UObject**——它不参与 GC 引用链，两套机制会各自按自己的规则判断存亡。

引用计数侧的经典问题同样存在：两个对象互相持有强引用会形成循环，引用计数永不归零，需要其中一方改为弱引用。对象要在自己的成员函数中获得指向自身的共享指针时，必须通过专门的自引用机制，且该对象必须已经被共享指针持有——在构造函数中调用会失败，因为此时引用计数尚未建立。

## 强引用、弱引用与软引用

强引用表示当前确实需要对象存活，弱引用用于观察，软引用保存资产路径并允许稍后加载。软引用有路径不代表资产已经驻留；`Get()`返回空时，要区分尚未加载、加载失败和对象已经失效。

以下为UE5.6的UCLASS成员片段，宿主由存活世界持有。模块头、`GENERATED_BODY`和类型注册由工程提供，调用发生在游戏线程。

```cpp
UPROPERTY()
TObjectPtr<UObject> OwnedObject;
TWeakObjectPtr<UObject> ObservedObject;

void CreateOwned()
{
    OwnedObject = NewObject<UObject>(this);
    ObservedObject = OwnedObject;
}
void ReleaseOwned()
{
    OwnedObject = nullptr;
}
```

创建后，宿主到`OwnedObject`的反射字段构成强引用。清空该字段只删除这一条边；如果没有其他强引用，对象才有资格在GC中回收。`ObservedObject`便于在回收后拒绝访问，它不保持对象存活。`Outer`表达对象归属，不能用它替代从存活宿主出发的可追踪强引用。

验证时在存活宿主上创建对象，先触发GC确认强引用仍在，再清空强引用并触发GC，检查弱引用有效性变化。若对象仍存活，沿引用链查找其他持有者。测试结果需要同时记录宿主的存活方式，否则宿主与目标一同回收会掩盖设计问题。

## 增量标记与写屏障

GC把可达性扫描分散到多帧以后，游戏逻辑可能在两段扫描之间新增引用。假设A已经扫描，后来A又引用B，而B还没有标记；若GC看不到这次赋值，就可能把本来可达的B当成垃圾。`TObjectPtr`写屏障把这种新增关系通知给回收器，维持扫描期间的可达性。

因此使用增量可达性分析时，需要按目标版本要求迁移可追踪字段并检查显式引用收集。把字段类型改完只完成了接口准备，帧预算是否满足、写屏障是否覆盖项目自定义引用，还要用实际GC压力场景确认。保持对象存活也不意味着它的任意字段可以跨线程无锁访问，数据竞争仍由线程所有权控制。

## 加载完成与销毁状态

软引用只保存资产定位信息。教学流程先保留TSoftObjectPtr路径，发起异步加载并保存请求句柄；回调在游戏线程检查宿主弱引用和本次请求代数。若玩家已切换选择，请求代数落后，即使资产加载成功也不安装。接受结果时写入存活宿主的UPROPERTY TObjectPtr强字段，随后按加载系统契约释放请求句柄。否则只拿到临时裸指针，后续GC仍可能回收资产。句柄保持与取消行为按所用StreamableManager接口核对，本文没有执行该异步工程片段。

可达也不等于可继续执行玩法。Actor收到Destroy后先进入玩法退出流程，EndPlay用于解绑事件、停止计时器和取消异步工作，底层内存由后续生命周期处理。异步回调除弱引用有效性外，还要检查本任务仍允许在当前世界和玩法状态执行。直接delete UObject绕过引擎生命周期；在GC阶段做跨世界玩法操作也容易访问已经退出的对象。BeginDestroy等底层清理与EndPlay职责不同，具体资源释放时序应由派生类型和目标版本接口决定。

## 验证方法

构造持有、释放与弱引用用例，强制GC后检查可达对象和销毁状态。UE5版本可支持增量可达性分析，标记不能写成永久单帧保证；阶段配置、TObjectPtr写屏障与引用收集按目标版本源码检查，实际运行UNVERIFIED。

## 相关主题

- [[16_编程与数据结构/对象生命周期]]
- [[23_引擎运行系统/引擎世界与对象模型]]
- [[16_编程与数据结构/内存布局与分配]]
- [[23_引擎运行系统/Unity对象生命周期]]
- [[16_编程与数据结构/对象池]]

## 参考资料

- Epic Games，[UE5.6 Actor Lifecycle](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-actor-lifecycle?application_version=5.6)：2026-10-23核读EndPlay与GC阶段职责。
- Epic Games，[UE5.6 Asynchronous Asset Loading](https://dev.epicgames.com/documentation/en-us/unreal-engine/asynchronous-asset-loading-in-unreal-engine?application_version=5.6)：2026-10-23核读软引用与StreamableManager持有；请求代数为本文教学策略。

- Epic Games，[UE5.6 Unreal Smart Pointer Library](https://dev.epicgames.com/documentation/en-us/unreal-engine/smart-pointers-in-unreal-engine?application_version=5.6)，Smart Pointer Types；2026-10-22核读。Shared/Weak与Unique的所有权差异及UObject适用边界由此核对。

- Epic Games，[UE5.6 Object Pointers](https://dev.epicgames.com/documentation/en-us/unreal-engine/object-pointers-in-unreal-engine?application_version=5.6)，指针对照表、TObjectPtr、TWeakObjectPtr、TSoftObjectPtr与TStrongObjectPtr；2026-10-22核读。
- Epic Games，[UE5.6 Incremental Garbage Collection](https://dev.epicgames.com/documentation/en-us/unreal-engine/incremental-garbage-collection-in-unreal-engine?application_version=5.6)，Incremental Reachability Analysis、Enable Incremental Reachability Analysis；2026-10-22核读。支持写屏障及实验状态，不证明本项目已经执行引擎GC实验。
