# C++工程边界

头文件能编译，插件加载却仍可能失败，因为链接符号、对象布局和分配器跨越了不同边界。C++工程先区分编译、链接与运行加载，再固定ABI、类型布局和资源释放方。

## C++ 从源码到模块边界

### C++ 构建链

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

### Header 与 Translation Unit

Header 通常放声明、Inline/Template 和必要类型；`.cpp` 放实现。Header 被多少文件包含，影响增量编译范围。

减少不必要 Include：

- 能 Forward Declaration 时不引入完整定义；
- 私有实现可使用 PImpl 隔离依赖；
- 稳定公共接口与高频变化实现分开；
- Template 必须在实例化位置看到定义，不能简单全部移进 `.cpp`。

Include Guard/`#pragma once` 防止同一 Translation Unit 重复包含，但不解决跨 Translation Unit 的 One Definition Rule。

### Static 与 Dynamic Library

Static Library 在 Link 时把所需 Object 合入目标。部署简单，但多个程序可能各自包含一份，更新需要重新链接。

Dynamic Library 在运行时加载，多个模块可共享并独立替换，但需要处理：

- Export/Import Symbol；
- 搜索路径与依赖 DLL；
- Calling Convention；
- CRT/Allocator 边界；
- C++ ABI、Compiler 和 Build Config；
- Library 卸载时仍存活的对象/回调。

跨 DLL 分配、另一侧释放若使用不同 Heap/CRT，可能崩溃。边界常提供成对 `Create/Destroy`，由分配方负责释放。

### ABI 与 C Interface

C++ 类、STL Container、Exception 和 Name Mangling 容易受编译器/版本影响。长期稳定插件接口常暴露简单 C ABI：

- 固定位宽整数和 POD Struct；
- Pointer + Length；
- Opaque Handle；
- 显式 Version/Size；
- 调用方提供 Buffer 或成对释放函数；
- Error Code + Error Message 查询。

不要跨边界直接传 `std::string`、`std::vector` 或编译器私有对象，除非所有模块严格锁定同一工具链。

### Win32 与 COM 边界

Win32 GUI 程序从消息队列取出事件，经 `TranslateMessage` 和 `DispatchMessage` 送到窗口过程 `WndProc`。`WPARAM`、`LPARAM` 的解释取决于消息类型，可能保存整数、位域或指针。窗口创建、输入、缩放和销毁都通过消息发生；引擎平台层应把它们转换成稳定事件，再交给上层系统。

COM 用接口和二进制契约连接不同组件。对象通过 `QueryInterface` 查询支持的接口，用 `AddRef/Release` 管理引用计数，接口以 GUID 标识。DirectX 与许多 Windows API 返回 COM 对象，C++ 中应使用智能指针封装引用计数，并明确线程 Apartment、初始化与释放顺序。

## C++ 类型与资源怎样工作

### C++ 类型与布局

STL 提供容器、迭代器和算法，模板在编译期生成具体类型代码。继承与虚函数支持运行时多态，但会引入对象布局、间接调用和 ABI 约束；数据导向热路径更常用显式数据与批处理。

Struct 的 Padding 由成员对齐要求决定，成员顺序会改变 `sizeof`。Union 让多个成员共享同一段存储，必须记录当前有效成员；现代 C++ 更适合用 `std::variant` 表达带标签联合。任何跨文件、网络、GPU 或插件边界的数据结构都应固定宽度、布局和版本，不能直接依赖编译器默认内存表示。

### C++ 对象模型与虚函数

普通非虚成员函数不存放在每个对象内。对象主要保存非静态数据成员和编译器需要的隐藏信息。含虚函数的对象通常带一个虚表指针，指向该动态类型的虚函数表。通过基类指针或引用调用虚函数时，程序根据动态类型查表完成运行时分派。

标准规定的是多态行为，不规定虚表的具体内存布局。常见实现可以帮助理解成本，但不能作为跨编译器 ABI 契约。

关键规则：

- 派生类使用 `override` 让编译器检查是否真正重写；
- `final` 可以禁止继续重写或继承；
- 纯虚函数 `= 0` 使类型成为抽象类；
- 通过基类指针删除派生对象时，基类析构函数必须是虚函数；
- 构造和析构期间的虚调用只分派到当前构造层级；
- 对象按值赋给基类会发生 Object Slicing，派生部分被丢弃。

虚调用的主要代价是一次间接调用，并可能限制内联。真正风险通常是对象分散、指针追逐和所有权不清。稳定扩展点适合接口多态，海量同构对象的热循环更适合连续数据与显式类型分组。

### Copy、Move 与异常安全

资源类型应优先遵守 Rule of Zero：让标准容器和智能指针管理资源，类型本身不手写析构、复制和移动。直接持有资源的 C++ 类型，需要一起设计析构、复制构造、复制赋值、移动构造和移动赋值。这是五法则（Rule of Five）。优先用标准资源包装类型承担所有权，减少手写这些操作的需要。

Move 把资源所有权转移到新对象，源对象仍需保持可析构、可赋值的有效状态。`std::move` 只是把表达式转换为右值引用，不会自动搬运；是否移动取决于目标类型是否实现移动操作。

容器和工具代码常讨论三种异常保证：失败后没有资源泄漏；失败后对象仍有效但值可能变化；失败后状态完全不变。RAII、先构造临时结果再交换，以及不抛异常的 Move 能帮助实现更强保证。

## 所有权与模块接口

RAII和唯一、共享、弱引用的完整语义见 [[16_编程与数据结构/对象生命周期]]。插件边界还要确定分配与释放属于同一运行库，卸载前没有存活回调或对象。

## C ABI契约

声明片段使用固定位宽版本和不透明句柄，创建与释放由同一模块实现。调用约定与导出宏按平台补齐。

```cpp
struct AssetApi { uint32_t version; uint32_t size; };
extern "C" int CreateAsset(const AssetApi* api, void** handle);
extern "C" void DestroyAsset(void* handle);
```

## 验证方法

分别制造缺符号、ABI版本不匹配与加载缺库，确认诊断阶段准确。测试空指针、字段size和成对释放；编译器私有容器不跨稳定插件接口。通用所有权见对象生命周期。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[16_编程与数据结构/对象生命周期]]
- [[15_资产与工具管线/资产构建CI]]
- [[16_编程与数据结构/CSharp运行模型]]
- [[16_编程与数据结构/Python宿主集成]]
- [[16_编程与数据结构/跨语言接口]]

## 参考资料

- ISO C++ Core Guidelines.
- Microsoft .NET and C# documentation.
- Unity Manual, *Scripting backend*, *IL2CPP* and *Managed code stripping*.
- Python Documentation, *Embedding*, *Extending* and *GIL*.
