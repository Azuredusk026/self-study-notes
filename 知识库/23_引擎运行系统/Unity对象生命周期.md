# Unity对象生命周期

Unity对象比较为null时，C#包装引用仍可能存在，因为原生对象已经销毁。创建与Destroy涉及引擎注册、回调和资源引用，不等于new或托管GC。理解两层身份才能正确判断释放与复用。

## 版本与对象身份

本文按Unity 6000.0的`Object.operator ==`和`Object.Destroy`文档解释生命周期，2026-10-22核读。C#示例为机制片段，完整Unity工程编译与运行尚未执行（UNVERIFIED）。

### Unity Object的两层身份

`GameObject`、`Component`、`Texture`、`Mesh` 等 UnityEngine.Object 通常有托管包装对象和引擎原生对象。C# 引用释放只影响托管对象可达性，原生资源的释放还由引擎对象与资源所有权决定。

Unity 特殊的 Null 比较会检查原生对象是否已被销毁。对象看似 `== null` 时托管包装对象仍可能存在，普通 C# `ReferenceEquals` 语义不同。

## Instantiate 的成本

设一个Prefab包含根节点、两个子节点、Renderer与用户脚本。实例化时，先要复制这组对象及序列化字段，让副本的层级和内部引用指向副本；随后对象进入相应子系统，启用回调又可能执行用户逻辑。因此一次创建可以沿下面几类工作定位：

1. 托管包装对象与脚本对象分配；
2. 原生GameObject、Transform、Component 分配；
3. Prefab与序列化字段复制与引用解析；
4. 变换层级注册；
5. Renderer、Physics、Animation、Audio 等子系统注册；
6. `Awake`、`OnEnable` 等生命周期回调；
7. 脚本在回调中继续分配、查找和加载；
8. 后续渲染/物理结构更新。

成本不是“new 一个 C# 对象”。复杂 Prefab 的 Component、子层级和回调往往比单次托管分配成本更高。

GPU资源是否在此刻创建或上传取决于资产与引擎状态，不能笼统说每次 Instantiate 都上传全部 Mesh/Texture。

## Destroy 的成本

Unity `Destroy`安排对象销毁。Unity 6000.0文档规定，实际销毁在当前Update循环结束以后、渲染以前发生；带延时参数时还要等待指定时间。销毁可能触发：

- `OnDisable`/`OnDestroy`；
- 层级关系和子系统注销；
- 原生资源引用变化；
- 托管包装对象随后由GC回收；
- 批量销毁造成帧末峰值。

`DestroyImmediate` 主要用于受控编辑器场景，运行时或遍历集合期间调用可能破坏状态。

原生资产是否卸载还取决于其他引用、AssetBundle/Addressables Handle 和资源管理策略。

## 销毁后的有效性检查

保存一个`UnityEngine.Object`引用，销毁它，再跨过销毁处理时机，能够观察两种身份的区别。以下C#协程片段放在一个持续存活的`MonoBehaviour`中；它只销毁自己创建的测试对象，不销毁协程宿主。

```csharp
System.Collections.IEnumerator ProbeLifetime()
{
    var target = new UnityEngine.GameObject("LifetimeProbe");
    UnityEngine.Object wrapper = target;
    UnityEngine.Object.Destroy(target);
    yield return null;
    UnityEngine.Debug.Log(wrapper == null);                    // 预期true
    UnityEngine.Debug.Log(object.ReferenceEquals(wrapper, null)); // 预期false
}
```

协程保留包装引用，所以CLR仍能观察到它；Unity重载的比较还检查底层原生对象，因而判为无效。`?.`和`??`采用C#引用空值语义，不能替代Unity对象有效性检查。访问引擎属性以前显式判断Unity对象，可避免拿着尚存的包装引用调用已销毁对象。

对象停用后，包装与原生对象仍然存在；禁用不是销毁。池中对象因此仍占有组件和资源，复用时要重置事件订阅、动画和物理状态，并按具体API管理协程和异步请求的结束。

假设池中敌人E在第7次借出期间请求头像，请求尚未完成就归还；第8次借出又把同一对象分配给另一个敌人。旧请求完成时，E仍有效，Unity空值检查当然通过，却会把旧头像覆盖到新敌人。让借出代数每次递增，请求捕获7，完成时要求`target仍有效 && currentGeneration==7`。当前已为8就丢弃交付，并释放该请求自己的资源句柄。取消用于减少无用工作，代数检查用于拒绝迟到结果，二者承担不同职责。

## 验证方法

分别记录Instantiate、Activate、Destroy与原生资源释放时间。销毁后比较ReferenceEquals与引擎null检查，测试场景卸载和Asset句柄未释放。实际Unity运行UNVERIFIED。

## 相关主题

- [[16_编程与数据结构/对象生命周期]]
- [[16_编程与数据结构/对象池]]
- [[16_编程与数据结构/内存布局与分配]]
- [[23_引擎运行系统/Unreal对象生命周期]]

## 参考资料

- Unity 6000.0 [Object.operator ==](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Object-operator_eq.html)，Description中的托管与原生对象检查；2026-10-22核读。
- Unity 6000.0 [Object.Destroy](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Object.Destroy.html)，Description中的销毁时机、组件与子对象行为；2026-10-22核读。
