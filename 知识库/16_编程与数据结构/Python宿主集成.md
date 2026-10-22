# Python宿主集成

系统Python能导入的包，在DCC里不一定可用。宿主固定解释器、ABI与UI绑定，工具首先匹配这套环境，再决定后台计算和主线程对象操作的边界。

## 宿主环境与接口

### Python 环境

DCC 常嵌入特定 Python 版本，并附带自己的模块、Qt绑定和动态库。系统 Python 能运行，不代表 Maya/Blender 内能导入相同包。

工具需要记录：

- 宿主/DCC 与 Python 版本；
- `sys.path` 与包根目录；
- 虚拟环境/依赖锁定；
- 本机扩展wheel 的平台和 ABI；
- Qt/PySide 版本；
- 插件加载顺序。

不要在用户全局 `site-packages` 随意 `pip install`。项目可使用受控目录、Wheelhouse 或 Launcher 注入路径，并固定依赖哈希。

### 宿主上下文与数据接口

Maya `cmds`、Blender `bpy.ops` 等命令 API 可能依赖选择、Mode 和当前 UI。批处理优先使用显式对象和数据接口。

纯 Python 循环处理数百万顶点会慢。优先：

- 使用 DCC 提供的批量 API；
- NumPy/原生扩展；
- 一次读取连续数组，减少跨语言调用；
- 由 C++、计算着色器或专用工具处理昂贵计算，Python 负责调度。

频繁调用一次处理一个点的 Native Binding，成本可能主要来自边界切换，而不是算法。

### GIL 与并发

常规带GIL的CPython构建具有全局解释器锁，同一进程中的线程通常不能并行执行 CPU 密集 Python 字节码。较新版本还提供可选 free-threaded 构建，是否启用以及扩展兼容性要按实际解释器核对。

线程仍适合 IO 等待；释放 GIL 的 Native 库可并行；CPU密集任务可使用进程池，但要承担数据序列化和进程启动成本。

DCC API 多数要求主线程调用。不要从后台线程直接修改场景。可后台解析文件，再把对象修改排回主线程。

## 环境探针

完整Python标准库探针输出解释器路径与版本，用于识别实际宿主；不安装依赖或修改全局环境。

```python
import sys
import platform
print(sys.executable)
print(sys.version)
print(platform.machine())
```

## 宿主状态与后台结果

后台任务只处理可序列化的纯数据，提交时记录场景版本与目标对象ID。任务完成后回到宿主允许的线程，再检查场景版本和对象是否仍有效；用户已经关闭文件或删除对象时丢弃过期结果。把宿主对象直接捕获到线程闭包里，会把寿命和线程限制一起带到后台。

包导入错误先区分纯Python路径与本机扩展加载。`sys.path`正确只能让解释器找到模块；扩展wheel还必须匹配解释器ABI、平台架构及其依赖DLL。路径修补不能解决二进制不兼容。上面的探针记录解释器信息；导入目标包后再输出该模块的 `__file__`，可以识别加载了系统包还是宿主包。

CPython3.13开始提供可选自由线程构建。GIL是否启用、扩展是否支持该构建，要查看正在运行的解释器；这项能力不会自动解除DCC场景API的主线程要求。宿主规定的线程边界仍由宿主文档决定。

## 验证方法

在系统解释器与目标宿主分别运行探针，再检查wheel平台与ABI。纯数据计算可后台执行，DCC对象访问依其线程约定。较新free-threaded构建与扩展兼容性按实际环境核对。


## 实现与证据

环境探针为完整标准库代码；本批机制实验在Python3.11运行，未在Maya或Blender宿主执行。PEP703核读只支持可选自由线程机制，具体DCC线程行为由宿主验收。

## 相关主题

- [[15_资产与工具管线/编辑器工具的事务与批处理]]
- [[16_编程与数据结构/进程与调度]]
- [[16_编程与数据结构/C++工程边界]]
- [[16_编程与数据结构/CSharp运行模型]]
- [[16_编程与数据结构/跨语言接口]]

## 参考资料

- [PEP703](https://peps.python.org/pep-0703/)：Build Configuration Changes与扩展兼容；2026-10-22核读。
- [Python Extending and Embedding](https://docs.python.org/3.11/extending/index.html)：嵌入解释器与扩展接口。
