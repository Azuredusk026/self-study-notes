# Unreal对象生命周期

普通C++指针指向UObject，并不自然成为GC根。Unreal通过可追踪引用维护可达性，原生对象智能指针则是另一套机制。字段标记、显式引用收集和销毁状态需要沿目标版本核对。

## Unreal 的 UObject 生命周期

Unreal 在 C++ 之上为 `UObject` 建立了一套独立的自动内存管理，与原生 C++ 的 RAII 并行存在。两套机制的边界是工程中最容易出错的地方。

### 标记—清除

核心算法是标记—清除：以 Root 集合中的对象为起点，递归遍历引用链，能到达的标记为可达；清理阶段回收所有未标记对象。

标记遍历引用关系，清理执行对象销毁。两者耗时都受对象数量、引用边、cluster与配置影响。UE5部分版本提供增量可达性分析，不能把标记永久描述为单帧不可拆。目标源码、GC配置与实际时间线要一起核对。

### 什么算作引用

引用链只认引擎能够识别的引用，普通的 C++ 指针不在其列：

- `UObject*` 成员被 `UPROPERTY` 宏标记，自动纳入引用链；
- 对象实现 `AddReferencedObjects` 接口，手动登记引用；
- 未由反射系统追踪的非UObject宿主，可以通过FGCObject等机制显式收集引用。反射结构体中的UPROPERTY引用是否可达，还取决于其宿主是否被追踪。

裸 `UObject*` 成员不被 GC 感知——对象可能在持有者毫不知情时被回收，留下悬垂指针。这是 UE 新手最常见的崩溃原因，且现象具有延迟性：崩溃发生在某次 GC 之后，而非写下代码之处。

对象不被回收的条件相应地有三条：加入 Root 集合、被 Root 直接或间接引用、被存活的 `FGCObject` 引用。放在 `UPROPERTY` 修饰的 `TArray`、`TMap` 中的 UObject 同样受保护。

### 与智能指针的分工

Unreal 有两套并行的生命周期管理，用错会同时失去两者的保障：

| 对象类型 | 管理方式 |
|---|---|
| `UObject` 派生类 | GC管理，反射字段中的UPROPERTY/TObjectPtr或显式引用收集 |
| 非 UObject 的 C++ 类 | 引用计数智能指针（Shared / Weak / Unique） |
| Slate 控件 | 引用计数智能指针 |

**不要用共享指针持有 UObject**——它不参与 GC 引用链，两套机制会各自按自己的规则判断存亡。

引用计数侧的经典问题同样存在：两个对象互相持有强引用会形成循环，引用计数永不归零，需要其中一方改为弱引用。对象要在自己的成员函数中获得指向自身的共享指针时，必须通过专门的自引用机制，且该对象必须已经被共享指针持有——在构造函数中调用会失败，因为此时引用计数尚未建立。

## 引用声明

UE5风格声明片段保留引擎可追踪字段，具体类型与生成头由模块提供。

```cpp
UPROPERTY()
TObjectPtr<UObject> ownedObject;
```

## 验证方法

构造持有、释放与弱引用用例，强制GC后检查可达对象和销毁状态。UE5版本可支持增量可达性分析，标记不能写成永久单帧保证；阶段配置、TObjectPtr写屏障与引用收集按目标版本源码检查，实际运行UNVERIFIED。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[16_编程与数据结构/对象生命周期]]
- [[23_引擎运行系统/引擎世界与对象模型]]
- [[16_编程与数据结构/内存布局与分配]]
- [[23_引擎运行系统/Unity对象生命周期]]
- [[16_编程与数据结构/对象池]]

## 参考资料

- Epic Games, *Unreal Object Handling* and *Smart Pointer Library* documentation.

- Microsoft .NET Documentation, *Garbage collection fundamentals*.
- Unity Manual, *Memory management*, *Object pooling*, *Native containers* and lifecycle documentation.
- ISO C++ Core Guidelines, resource management sections.

- [官方增量可达性分析与TObjectPtr写屏障，2026-10-07核读当前页面；目标运行UNVERIFIED](https://dev.epicgames.com/documentation/en-us/unreal-engine/incremental-garbage-collection-in-unreal-engine)。
