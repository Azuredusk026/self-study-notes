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

这两端之间还有 Ubershader：每个材质只保留一个包含全部功能的程序，运行时用 Uniform 开关控制行为。它的内存与包体最小，代价是大量分支阻碍编译优化、运行效率下降，并且更难调试。全量缓存变体与 Ubershader 是两个极端，实际项目通常落在中间，按功能的稳定性与切换频率分别选择。

## Unreal 的变体构成

Unreal 不用 Keyword 字符串描述变体，而是把它拆成几个正交维度的乘积。理解这个乘法结构才能判断从哪里削减。

```text
变体数上限 =
  ShaderPlatform 数
  × (母材质数 × 每个母材质的静态开关组合 × 材质质量级别数)
  × (VertexFactory 数 × 其静态开关组合)
  × (ShaderType 数 × 其静态开关组合)
```

这是理论上限而非精确值——部分项互相依赖，只有实际被引用的材质实例才产生变体，Shader Library 还会去重编译结果相同的 Shader。但它清楚地说明了问题性质：**这是连乘，任何一项增长都会放大全局**。

各维度的含义：

- **ShaderPlatform**：ES3.1、Vulkan、Metal 等。Cook 时为所有支持平台各生成一份，运行时由 RHI 决定用哪一份；
- **材质静态开关与质量级别**：美术在材质图中设置，Cook 时展开所有组合；
- **VertexFactory**：决定顶点数据如何进入 Shader。静态开关不同的 VF 在 C++ 层面视为不同 VF；
- **ShaderType**：Base Pass、Shadow Depth 等不同 Pass 使用不同 Shader 类，同样支持静态开关。

**会**产生新变体的改动：平台变化、材质图结构变化、网格类型变化、绘制 Pass 变化、静态开关变化。

**不会**产生新变体的改动：材质参数值、Uniform 值、网格数据本身。

这条界线很实用——美术调整材质参数不增加变体，但勾选一个静态开关会让该母材质的变体数翻倍。

### 内存与包体分别占在哪

两者的构成不同，优化手段也不同：

| 占用项 | 性质 | 说明 |
|---|---|---|
| ShaderMap 与 FShader 对象 | 常驻内存 | 序列化时为每个 Shader 创建对象，构成基础开销 |
| Shader 源码 / 字节码 | 内存 + 包体 | Shared/Native 模式下存于 Shader Library，按需异步请求 |
| 反射信息映射表 | 常驻内存 | Native 模式下引擎无法读取平台中间格式，需单独序列化绑定信息，启动时全量读入 |
| PSO | RHI 层内存 | 驱动侧的已编译对象，由 LRU 限制总量 |

包体侧主要是 Shader 字节码体积：OpenGL 保存源码，Vulkan 保存 SPIR-V，Metal 在 Native 模式下保存编译后的中间格式。

大型移动项目中，进入包体的 Shader 可达数百 MB，内存占用数十至上百 MB。包体影响安装转化率，内存影响 OOM 崩溃率，两者都是可以量化的业务指标。

### 四个优化方向

1. **减少变体数量**：从连乘公式的各项入手——删除材质用不到的 Usage 标记、合并母材质、减少静态开关、收敛质量级别数、控制 VF 与 ShaderType 的开关数量。删除不必要的材质 Usage 常是收益最快的一项，因为每个 Usage 都会引入一整套 VF 组合；
2. **压缩**：对 Shader Library 整体压缩，显著减小包体，代价是运行时少量解压开销；
3. **按机型分包**：提前判断各机型实际需要的 Shader 集合，分包下发，同时减小包体与内存；
4. **按需加载与剔除**：按平台、材质级别、画质、场景分别剔除，并调节 PSO 的 LRU 参数。

前两项在构建期生效，后两项在运行期生效。四者可以叠加。

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

第三条值得展开：引擎层面的 Shader 预热与驱动层面的 Pipeline State 编译是两件事。预热了变体不代表 PSO 已就绪，反之亦然。首次出现卡顿到底来自哪一层，需要分别验证。

### 剥离规则的实现位置

Unity 在构建期通过 `IPreprocessShaders` 回调逐 Pass 提供变体列表，允许实现方删除条目：

```csharp
class VariantStripper : IPreprocessShaders
{
    public int callbackOrder => 0;

    public void OnProcessShader(Shader shader, ShaderSnippetData snippet,
                                IList<ShaderCompilerData> data)
    {
        var keyword = new ShaderKeyword("_EXPENSIVE_FEATURE");
        for (int i = data.Count - 1; i >= 0; i--)
        {
            if (!data[i].shaderKeywordSet.IsEnabled(keyword)) continue;
            if (targetIsMobile)
                data.RemoveAt(i);
        }
    }
}
```

回调按 Shader 与 Pass 分批调用，`data` 是可变列表，移除即代表该变体不进入构建。倒序遍历是必要的，正序删除会跳过元素。

剥离必须给出理由而非"没见过就删"。安全的判据是平台能力、质量档位、功能开关的互斥关系这类可静态证明的约束。删错的表现是运行时找不到变体，画面显示为粉色材质或直接不绘制，而且往往只在特定机型的特定场景复现。

验证方法是记录剥离前后的数量与每条规则的命中数，并在真机构建中跑一遍关键场景，检查是否出现粉色材质与首次加载卡顿。

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
- [[14_性能分析与优化/PSO缓存与运行时卡顿]]
- [[13_引擎架构与资源系统/Unreal网格绘制与自定义Pass]]

## 参考资料

- Unity Manual, *Shader variants and keywords*.
- Unity Manual, *Shader variant stripping*.
- Unity Scripting API, `IPreprocessShaders` and `ShaderVariantCollection`.
- Epic Games, *Shader Development* and *Mesh Drawing Pipeline* documentation.
- Unreal Engine source, `FMaterialShaderMap`, `FShaderLibrary` serialization paths.
