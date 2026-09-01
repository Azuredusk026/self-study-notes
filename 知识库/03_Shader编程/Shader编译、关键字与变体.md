# Shader 编译、关键字与变体

Shader 变体不是“同一个 Shader 的几个参数”。它们是条件编译后得到的不同 GPU 程序。变体管理要同时考虑编译时间、包体、运行时切换和首次使用卡顿。

## 从源码到 GPU 程序

典型过程：

```text
Shader 源码
  → 预处理和宏展开
  → 引擎生成 Pass / 平台代码
  → 前端编译到中间表示
  → 平台后端或驱动生成 GPU 指令
  → 创建 Pipeline State
```

Unity/Unreal 可能在构建时完成大部分编译，但驱动仍可能在运行时创建或缓存平台程序和 Pipeline State。不同平台的缓存边界不同。

## Variant 和 Permutation

假设有 $n$ 个互相独立的二元 Feature，理论组合数是 $2^n$。如果每组 Keyword 有不同选项，组合数是各组数量的乘积。

并不是源码中写了十个 `if` 就一定有 $2^{10}$ 个变体。只有参与编译期 Keyword/Permutation 的条件才会展开组合。

变体数量还会乘上：

- Pass；
- 光照、阴影、雾等引擎 Keyword；
- 平台和图形 API；
- 质量等级；
- Instancing、XR 等系统选项。

## Unity 中的 `multi_compile`

`multi_compile` 用于运行时可能出现的 Keyword 组合。构建时通常先生成声明的全部组合，再由构建剥离规则删除确认不需要的部分。

适合：

- 引擎全局功能；
- 运行时确实会切换、无法由材质静态确定的功能；
- 需要明确保证变体存在的场景。

风险是组合数快速增长。

## Unity 中的 `shader_feature`

`shader_feature` 更适合由材质决定的功能。构建系统可以根据项目中使用该 Shader 的材质剥离未使用组合。

风险：运行时通过脚本启用一个构建时没有被任何已收集材质使用的 Keyword，目标变体可能已经被剥离。

不同 Unity 版本还区分 Local/Global Keyword、`shader_feature_local` 等形式。使用前应按项目版本核对官方文档。

## 动态分支还是变体

| 选择 | 优点 | 代价 |
|---|---|---|
| 编译变体 | 当前程序没有未选功能代码，可做更强编译优化 | 编译、包体、内存和预热压力 |
| 运行时分支 | 减少程序数量，功能组合简单 | 可能增加指令、寄存器和 Wave 发散 |
| 分拆 Shader | 责任清楚，变体更少 | 材质和管线管理更复杂，可能破坏共享 |

决定时要看条件是否在 Draw 内一致、两边代码多重、切换频率和平台瓶颈。没有一种方案永远更快。

## 收集不能只扫描当前场景

扫描当前打开场景的材质，只能覆盖静态可见的一部分。还可能遗漏：

- Addressables、AssetBundle 或 DLC 中的材质；
- 运行时实例化的 Prefab；
- 脚本动态开启的 Keyword；
- 粒子、UI、后处理和引擎内部 Pass；
- 不同 Quality、Lightmap、Fog、Shadow、XR 组合；
- 编辑器没直接引用，但运行时按名称加载的 Shader。

可靠做法需要把**内容依赖、代码路径、平台配置和运行时采样记录**结合起来。

## 剥离流程

一个实用流程：

1. 建立 Keyword 所有者和使用约定。
2. 从材质、场景、可寻址资源和构建内容收集静态组合。
3. 从代码中登记运行时可能切换的组合。
4. 根据平台和质量等级剥离不可能出现的组合。
5. 输出构建前后数量和剥离原因。
6. 在真机构建中覆盖关键场景。
7. 对缺失变体、粉色材质和首次出现卡顿做自动检查。

剥离规则不能只写“删除没见过的组合”。它还要能解释为什么一个组合在目标版本中不可能出现。

## ShaderVariantCollection 和 Warmup

Unity 的 Shader Variant Collection 可以记录一组 Shader、Pass 和 Keyword 组合，并请求 Warmup。

Warmup 的作用是提前触发部分 Shader/平台对象准备，减少第一次出现时的卡顿。但它有几个限制：

- 收集内容不完整仍会漏变体；
- 预热太多会增加启动时间和内存；
- 驱动 Pipeline Cache 和引擎 Shader 缓存不是同一个层次；
- 不同 API、驱动和 Unity 版本的实际编译时机不同。

因此需要在目标设备上测量启动、场景进入和首次特效出现的帧时间。

## 变体预算和报表

构建报告至少记录：

- 每个 Shader、SubShader、Pass 的变体数；
- 剥离前后数量；
- 哪些 Keyword 贡献最大；
- 编译耗时和缓存命中；
- 包体中的 Shader 数据；
- 目标设备首次使用卡顿。

只看总变体数不够。少数超大 Shader、常用但预热遗漏的变体，往往比很多从不加载的小 Shader 更危险。

## 个人贡献怎么描述

需要区分：

- 使用公司已有收集插件；
- 编写剥离规则；
- 设计 Keyword 和 Shader 架构；
- 建立构建报表；
- 负责真机验证和回归。

这些工作都有效，但所有权和技术深度不同。文档和简历应准确说明自己负责的部分。

## 相关主题

- [[03_Shader编程/Shader语言与数据流]]
- [[13_引擎架构与资源系统/Unity与Unreal渲染扩展入口]]
- [[13_引擎架构与资源系统/资源打包、依赖与异步加载]]
- [[14_性能分析与优化/渲染优化验证与移动端实践]]

## 参考资料

- Unity Manual, *Shader variants and keywords*.
- Unity Manual, *Shader variant stripping*.
- Unity Scripting API, `IPreprocessShaders` and `ShaderVariantCollection`.
