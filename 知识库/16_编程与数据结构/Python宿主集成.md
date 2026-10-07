# Python宿主集成

系统Python能导入的包，在DCC里不一定可用。宿主固定解释器、ABI与UI绑定，工具首先匹配这套环境，再决定后台计算和主线程对象操作的边界。

## Python 怎样接入制作环境

### Python 环境

DCC 常嵌入特定 Python 版本，并附带自己的 Module、Qt Binding 和动态库。系统 Python 能运行，不代表 Maya/Blender 内能导入相同包。

工具需要记录：

- Host/DCC 与 Python Version；
- `sys.path` 与 Package Root；
- Virtual Environment/Package Lock；
- Native Wheel 的平台和 ABI；
- Qt/PySide Version；
- Plugin 加载顺序。

不要在用户全局 `site-packages` 随意 `pip install`。项目可使用受控目录、Wheelhouse 或 Launcher 注入路径，并固定依赖 Hash。

### Python 的 Context 与数据 API

Maya `cmds`、Blender `bpy.ops` 等命令 API 可能依赖 Selection、Mode 和当前 UI。批处理优先使用显式对象和 Data API。

纯 Python 循环处理数百万顶点会慢。优先：

- 使用 DCC 提供的批量 API；
- NumPy/Native Extension；
- 一次读取连续数组，减少跨语言调用；
- 把昂贵工作放在 C++/Compute/专用工具，Python 负责调度。

频繁调用一次处理一个点的 Native Binding，成本可能主要来自边界切换，而不是算法。

### GIL 与并发

本机采用的常规 CPython 3.12 构建带有 Global Interpreter Lock，同一进程中的线程通常不能并行执行 CPU 密集 Python 字节码。较新版本还提供可选 free-threaded 构建，是否启用以及扩展兼容性要按实际解释器核对。

Thread 仍适合 IO 等待；释放 GIL 的 Native 库可并行；CPU-heavy 任务可使用 Process Pool，但要承担数据序列化和进程启动成本。

DCC API 多数要求主线程调用。不要从后台线程直接修改 Scene。可后台解析文件，再把对象修改排回主线程。

## 环境探针

完整Python标准库探针输出解释器路径与版本，用于识别实际宿主；不安装依赖或修改全局环境。

```python
import sys
import platform
print(sys.executable)
print(sys.version)
print(platform.machine())
```

## 验证方法

在系统解释器与目标宿主分别运行探针，再检查wheel平台与ABI。纯数据计算可后台执行，DCC对象访问依其线程约定。较新free-threaded构建与扩展兼容性按实际环境核对。

实现状态：正文代码是机制片段或明确标注的伪代码，完整类型、资源与调用宿主按所述环境补齐。实际CPU与编译检查见对应实验链接；目标引擎运行与GPU测量为UNVERIFIED。

## 相关主题

- [[15_资产与工具管线/编辑器工具的事务与批处理]]
- [[16_编程与数据结构/进程与调度]]
- [[16_编程与数据结构/C++工程边界]]
- [[16_编程与数据结构/CSharp运行模型]]
- [[16_编程与数据结构/跨语言接口]]

## 参考资料

- ISO C++ Core Guidelines.
- Microsoft .NET and C# documentation.
- Unity Manual, *Scripting backend*, *IL2CPP* and *Managed code stripping*.
- Python Documentation, *Embedding*, *Extending* and *GIL*.
