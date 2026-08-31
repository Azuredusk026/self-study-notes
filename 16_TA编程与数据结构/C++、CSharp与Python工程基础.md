# C++、CSharp 与 Python 工程基础

TA 不需要用一种语言解决全部问题。C++、C# 和 Python 常处在不同运行环境：引擎底层与 Unreal、Unity 工具与 Gameplay、DCC/离线批处理。关键是理解它们的构建、生命周期和边界成本。

## 按运行位置选语言

**C++** 适合：

- 引擎 Runtime、Unreal Module、Native Plugin；
- 性能敏感的数据处理；
- 图形 API、DCC SDK 和系统库接入；
- 需要精确内存布局与生命周期的代码。

**C#** 适合：

- Unity Runtime/Editor Tool；
- .NET CLI、资产检查和服务工具；
- 需要成熟 UI、反射、序列化和异步库的应用。

**Python** 适合：

- Maya/Blender/Houdini/Unreal 自动化；
- 快速批处理、数据整理和工具胶水；
- 调用现有库、生成配置和报告；
- 可接受解释器成本的离线流程。

“Python 慢、C++ 快”不足以做选择。瓶颈可能在 DCC API、磁盘、网络或外部进程。先 Profile，再决定是否把热点移到 Native/Vectorized 库。

## C++ 构建链

一个典型流程：

```text
Source
 -> Preprocess
 -> Compile
 -> Object File
 -> Link
 -> Executable / Static Library / Dynamic Library
```

Preprocessor 展开 `#include`、宏和条件编译。Compiler 对每个 Translation Unit 生成 Object。Linker 解析跨文件 Symbol、Library 和最终地址。

常见错误对应不同阶段：

- Syntax/Type Error：编译阶段；
- Unresolved External：声明可见，但链接不到定义/Library；
- Multiple Definition：同一强 Symbol 重复；
- Missing DLL/Entry Point：运行加载阶段；
- ABI Mismatch：能链接或加载，但类型布局/调用约定不一致。

排错先判断阶段，不要看到“编译失败”就反复改代码。

## Header 与 Translation Unit

Header 通常放声明、Inline/Template 和必要类型；`.cpp` 放实现。Header 被多少文件包含，影响增量编译范围。

减少不必要 Include：

- 能 Forward Declaration 时不引入完整定义；
- 私有实现可使用 PImpl 隔离依赖；
- 稳定公共接口与高频变化实现分开；
- Template 必须在实例化位置看到定义，不能简单全部移进 `.cpp`。

Include Guard/`#pragma once` 防止同一 Translation Unit 重复包含，但不解决跨 Translation Unit 的 One Definition Rule。

## Static 与 Dynamic Library

Static Library 在 Link 时把所需 Object 合入目标。部署简单，但多个程序可能各自包含一份，更新需要重新链接。

Dynamic Library 在运行时加载，多个模块可共享并独立替换，但需要处理：

- Export/Import Symbol；
- 搜索路径与依赖 DLL；
- Calling Convention；
- CRT/Allocator 边界；
- C++ ABI、Compiler 和 Build Config；
- Library 卸载时仍存活的对象/回调。

跨 DLL 分配、另一侧释放若使用不同 Heap/CRT，可能崩溃。边界常提供成对 `Create/Destroy`，由分配方负责释放。

## ABI 与 C Interface

C++ 类、STL Container、Exception 和 Name Mangling 容易受编译器/版本影响。长期稳定插件接口常暴露简单 C ABI：

- 固定位宽整数和 POD Struct；
- Pointer + Length；
- Opaque Handle；
- 显式 Version/Size；
- 调用方提供 Buffer 或成对释放函数；
- Error Code + Error Message 查询。

不要跨边界直接传 `std::string`、`std::vector` 或编译器私有对象，除非所有模块严格锁定同一工具链。

## C++ 所有权

RAII 让资源生命周期绑定对象作用域。Constructor 获取资源，Destructor 释放资源。它不仅用于内存，也用于 File、Lock、GPU Handle 和 Transaction。

常见指针语义：

- `T*`/Reference：通常不表达所有权；
- `std::unique_ptr<T>`：唯一所有权；
- `std::shared_ptr<T>`：共享引用计数；
- `std::weak_ptr<T>`：观察共享对象，不增加强引用。

`shared_ptr` 不是默认安全选择。它增加原子引用计数、控制块和环引用风险。能用明确 Owner 和 Borrowed Reference 时更简单。

## C# 的运行模型

C# 编译为 .NET Assembly 与中间语言，随后由 Runtime JIT 或 AOT 成本机代码。具体路径取决于平台和引擎。

Unity 中需要区分 Mono、IL2CPP 和平台 AOT：

- Editor/部分平台可使用 JIT；
- IL2CPP 把 IL 转换为 C++ 再编译；
- AOT 对运行时泛型实例、反射和动态代码生成有额外限制；
- Managed Stripping 可能删除只通过反射访问的类型。

因此只在 Editor 运行成功的反射/动态加载代码，不一定能在目标平台工作。需要 Link 配置、显式引用和设备构建测试。

## Assembly 与模块边界

Unity Assembly Definition 可减少无关脚本重编译，并约束 Runtime/Editor/Test 依赖。建议：

- Runtime 不引用 Editor Assembly；
- Domain/Core 不依赖具体 UI；
- 平台集成放独立 Assembly；
- Tests 只引用所需模块；
- 循环依赖通过接口或职责重划解决，不靠把所有代码并回一个 Assembly。

模块化的目标是稳定依赖和可测试，不是让目录数量变多。

## C# 的值与引用

`class` 实例通常是引用类型，变量保存对象引用；`struct` 是值类型，赋值和传参可能复制。

大 Struct 频繁复制会产生 CPU 成本；可变 Struct 也容易出现“修改了副本”的错误。小型、不可变、表达单值的数据更适合 Struct。

Boxing 会把值类型包装为 Managed Object，例如通过非泛型接口或 `object` 使用。热循环中的 Boxing 会产生分配和 GC 压力。

## Python 环境

DCC 常嵌入特定 Python 版本，并附带自己的 Module、Qt Binding 和动态库。系统 Python 能运行，不代表 Maya/Blender 内能导入相同包。

工具需要记录：

- Host/DCC 与 Python Version；
- `sys.path` 与 Package Root；
- Virtual Environment/Package Lock；
- Native Wheel 的平台和 ABI；
- Qt/PySide Version；
- Plugin 加载顺序。

不要在用户全局 `site-packages` 随意 `pip install`。项目可使用受控目录、Wheelhouse 或 Launcher 注入路径，并固定依赖 Hash。

## Python 的 Context 与数据 API

Maya `cmds`、Blender `bpy.ops` 等命令 API 可能依赖 Selection、Mode 和当前 UI。批处理优先使用显式对象和 Data API。

纯 Python 循环处理数百万顶点会慢。优先：

- 使用 DCC 提供的批量 API；
- NumPy/Native Extension；
- 一次读取连续数组，减少跨语言调用；
- 把昂贵工作放在 C++/Compute/专用工具，Python 负责调度。

频繁调用一次处理一个点的 Native Binding，成本可能主要来自边界切换，而不是算法。

## GIL 与并发

CPython 的 Global Interpreter Lock 使同一进程中多个 Python Thread 通常不能并行执行 CPU-bound Python Bytecode。

Thread 仍适合 IO 等待；释放 GIL 的 Native 库可并行；CPU-heavy 任务可使用 Process Pool，但要承担数据序列化和进程启动成本。

DCC API 多数要求主线程调用。不要从后台线程直接修改 Scene。可后台解析文件，再把对象修改排回主线程。

## 跨语言边界

常见方式：

- C# P/Invoke 调 C ABI Native DLL；
- C++/CLI 连接 .NET 与 Native，仅适合支持平台；
- pybind11/CPython Extension 暴露 C++ 给 Python；
- Socket/HTTP/gRPC 把进程隔离；
- CLI + JSON/Protobuf/文件交换；
- Embedded Interpreter 在 Host 内执行脚本。

边界设计要明确 Ownership、Thread、Encoding、Error、Cancellation 和 Version。高频小调用应合并为 Batch，避免 Serialization/Interop 成为瓶颈。

## Error Handling

C++ Exception、C# Exception 和 Python Exception 不应未经转换跨 ABI/进程边界。

在边界捕获并转成稳定结果：

- Status/Error Code；
- 简短用户消息；
- 详细 Stack/Native Error；
- Operation/Asset ID；
- 可重试与否。

不要用 Exception 表示普通 Validation Failure，也不要吞掉异常后返回空数据，让下游继续生成错误资产。

## 配置与路径

使用结构化配置和 `Path` API，不手工拼接分隔符。区分：

- Project-relative Asset Path；
- Absolute Local Path；
- URI/Depot Path；
- Case-sensitive Canonical Path；
- Display Path。

Windows 开发环境可能掩盖大小写错误，Linux CI/目标平台会失败。路径规范化不等于全部转小写，权威大小写应来自资产数据库或版本库。

## 测试与调试

- 纯规则写 Unit Test，不启动 DCC/Engine。
- Host API 通过 Adapter 和 Fixture 做 Integration Test。
- Native 边界测试空指针、长度、编码、版本和分配释放。
- Unity 测 Editor、Mono/IL2CPP 和目标设备差异。
- Python 测受控 Host Version，不只测系统解释器。
- 构建日志保留 Compiler/Linker Command、Dependency Version 和 Environment 摘要。

## 相关主题

- [[15_资产与工具管线/编辑器工具与批处理架构]]
- [[16_TA编程与数据结构/内存、对象生命周期与对象池]]
- [[16_TA编程与数据结构/复杂度、树、图与空间划分]]

## 参考资料

- ISO C++ Core Guidelines.
- Microsoft .NET and C# documentation.
- Unity Manual, *Scripting backend*, *IL2CPP* and *Managed code stripping*.
- Python Documentation, *Embedding*, *Extending* and *GIL*.
