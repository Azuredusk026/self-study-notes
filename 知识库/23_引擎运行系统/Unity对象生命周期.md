# Unity对象生命周期

Unity对象比较为null时，C#包装引用仍可能存在，因为原生对象已经销毁。创建与Destroy涉及引擎注册、回调和资源引用，不等于new或托管GC。理解两层身份才能正确判断释放与复用。

## Unity Object 的两层身份

`GameObject`、`Component`、`Texture`、`Mesh` 等 UnityEngine.Object 通常有 Managed Wrapper 和 Native Engine Object。C# 引用释放只影响 Managed 可达性，不等于 Native Resource 立刻释放。

Unity 特殊的 Null 比较会考虑 Native Object 是否已被销毁。对象看似 `== null` 时 Managed Wrapper 仍可能存在，普通 C# `ReferenceEquals` 语义不同。

## Instantiate 的成本

创建 Prefab/GameObject 可能涉及：

1. Managed Wrapper/脚本对象分配；
2. Native GameObject、Transform、Component 分配；
3. Prefab/Serialized Field 复制与引用解析；
4. Transform Hierarchy 注册；
5. Renderer、Physics、Animation、Audio 等子系统注册；
6. `Awake`、`OnEnable` 等生命周期回调；
7. 脚本在回调中继续分配、查找和加载；
8. 后续渲染/物理结构更新。

成本不是“new 一个 C# 对象”。复杂 Prefab 的 Component、子层级和回调往往比单次 Managed Allocation 更贵。

GPU Resource 是否此刻真正创建/上传取决于 Asset 和引擎状态，不能笼统说每次 Instantiate 都上传全部 Mesh/Texture。

## Destroy 的成本

Unity `Destroy` 通常标记 Native Object 在安全时机销毁，不一定立即释放。销毁可能触发：

- `OnDisable`/`OnDestroy`；
- Hierarchy 和子系统注销；
- Native Resource 引用变化；
- Managed Wrapper 未来由 GC 回收；
- 批量销毁造成帧末峰值。

`DestroyImmediate` 主要用于受控 Editor 情景，Runtime 或遍历集合时滥用可能破坏状态。

Native Asset 是否卸载还取决于其他引用、AssetBundle/Addressables Handle 和资源管理策略。

## 有效性检查

Unity C#机制片段对UnityEngine.Object使用引擎重载的比较，再调用对象；普通C#对象另用CLR空值语义。

```csharp
if (gameObject != null)
{
    gameObject.SetActive(false);
}
```

## 验证方法

分别记录Instantiate、Activate、Destroy与原生资源释放时间。销毁后比较ReferenceEquals与引擎null检查，测试场景卸载和Asset句柄未释放。实际Unity运行UNVERIFIED。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[16_编程与数据结构/对象生命周期]]
- [[16_编程与数据结构/对象池]]
- [[16_编程与数据结构/内存布局与分配]]
- [[23_引擎运行系统/Unreal对象生命周期]]

## 参考资料

- Epic Games, *Unreal Object Handling* and *Smart Pointer Library* documentation.

- Microsoft .NET Documentation, *Garbage collection fundamentals*.
- Unity Manual, *Memory management*, *Object pooling*, *Native containers* and lifecycle documentation.
- ISO C++ Core Guidelines, resource management sections.
