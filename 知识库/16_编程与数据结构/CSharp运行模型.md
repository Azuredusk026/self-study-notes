# CSharp运行模型

Editor能通过反射创建类型，AOT构建却可能缺少实例或被剥离。C#运行模型先看IL如何变成本机代码，再看值类型复制、装箱、委托可达性与异步状态机。托管回收和原生资源释放有不同职责。

## C# 怎样编译并管理对象

### C# 的运行模型

C# 编译为 .NET Assembly 与中间语言，随后由 Runtime JIT 或 AOT 成本机代码。具体路径取决于平台和引擎。

Unity 中需要区分 Mono、IL2CPP 和平台 AOT：

- Editor/部分平台可使用 JIT；
- IL2CPP 把 IL 转换为 C++ 再编译；
- AOT 对运行时泛型实例、反射和动态代码生成有额外限制；
- Managed Stripping 可能删除只通过反射访问的类型。

因此只在 Editor 运行成功的反射/动态加载代码，不一定能在目标平台工作。需要 Link 配置、显式引用和设备构建测试。

### Assembly 与模块边界

Unity Assembly Definition 可减少无关脚本重编译，并约束 Runtime/Editor/Test 依赖。建议：

- Runtime 不引用 Editor Assembly；
- Domain/Core 不依赖具体 UI；
- 平台集成放独立 Assembly；
- Tests 只引用所需模块；
- 循环依赖通过接口或职责重划解决，不靠把所有代码并回一个 Assembly。

模块化的目标是稳定依赖和可测试，不是让目录数量变多。

### C# 的值与引用

`class` 实例通常是引用类型，变量保存对象引用；`struct` 是值类型，赋值和传参可能复制。

大 Struct 频繁复制会产生 CPU 成本；可变 Struct 也容易出现“修改了副本”的错误。小型、不可变、表达单值的数据更适合 Struct。

Boxing 会把值类型包装为 Managed Object，例如通过非泛型接口或 `object` 使用。热循环中的 Boxing 会产生分配和 GC 压力。

Unboxing 要求对象实际装箱的值类型与目标类型匹配。它先检查类型，再从包装对象中取出值；不能把装箱的 `int` 直接拆成 `long`。泛型集合和泛型接口让值类型使用专门实例，通常可以避免装箱。

值类型作为接口调用、传给 `object`、使用非泛型集合或某些格式化路径时可能发生隐式装箱。判断时应查看 IL、Profiler 分配或生成代码，不能只凭源码表面推测。

### C# 委托、事件与资源释放

Delegate 是类型安全的函数引用，可以组合多个调用目标。Event 在 Delegate 外增加发布边界，订阅方只能订阅和取消，只有声明事件的类型能够触发。长生命周期发布者持有短生命周期订阅者时，未取消订阅会让对象保持可达。

`IDisposable` 用于确定性释放文件句柄、Native Buffer、锁等非托管资源。`using`/`using var` 会在作用域结束时调用 `Dispose`。Finalizer 只提供兜底，执行时间不确定，并增加 GC 成本；安全封装原生句柄时优先使用 `SafeHandle`。

`async`/`await` 把异步操作的后续过程编译成状态机。它不会自动创建线程。IO 等待可以在不占用工作线程时挂起，CPU 密集工作仍需要明确调度。`Task` 表示未来结果，异常会保存在 Task 中，调用方应 `await` 或显式观察。

### C# 泛型、LINQ 与相等性

C# 泛型在编译和运行时保留类型信息，能提供类型安全，并减少值类型通过 `object` 传递产生的装箱。约束用于声明类型参数必须提供的能力，例如接口、引用类型、值类型或无参构造。

LINQ 提高表达力，但许多操作使用延迟执行、Iterator、Delegate 和闭包。重复枚举会重复计算，捕获变量可能分配闭包对象，`ToList` 会立即分配结果。编辑器与离线工具可以优先可读性，实时热路径需要用 Profiler 核对。

引用类型默认按引用身份比较，`string` 和实现了值相等的类型除外。自定义 Key 若重写 `Equals`，必须提供一致的 `GetHashCode`；参与 Hash 的字段在放入 Dictionary 后不应变化。

## 显式资源释放

C#机制片段使用IDisposable宿主，读取失败或正常退出都由using释放流。

```csharp
using var stream = File.OpenRead(path);
var bytes = new byte[checked((int)stream.Length)];
stream.ReadExactly(bytes);
```

## 验证方法

比较IL与Profiler分配，测试struct副本、装箱、订阅释放和异常路径。Unity接入同时检查Mono/IL2CPP与目标AOT，实际引擎运行为UNVERIFIED。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[16_编程与数据结构/对象生命周期]]
- [[23_引擎运行系统/Unity对象生命周期]]
- [[16_编程与数据结构/C++工程边界]]
- [[16_编程与数据结构/Python宿主集成]]
- [[16_编程与数据结构/跨语言接口]]

## 参考资料

- ISO C++ Core Guidelines.
- Microsoft .NET and C# documentation.
- Unity Manual, *Scripting backend*, *IL2CPP* and *Managed code stripping*.
- Python Documentation, *Embedding*, *Extending* and *GIL*.
