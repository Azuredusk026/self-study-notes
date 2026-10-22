# Unreal自定义Mesh Pass

一个效果需要筛选特定网格、选择着色器并写入独立附件时，Mesh Pass把这些规则集中成一组绘制。文章沿组件、网格描述、处理器和绘制命令展开，说明哪些状态能缓存、哪些数据必须在本帧更新。

## 版本与证据范围

接口模型依据UE5.4官方Mesh Drawing Pipeline与RDG文档，2026-10-22核读。下文代码为机制片段，具体处理器签名、Vertex Factory字段与渲染器调度位置必须在项目相同版本源码中核对。完整引擎编译、运行、GPU捕获及性能为UNVERIFIED；不把示意代码作为可直接应用的引擎补丁。

## 组件与绘制命令

组件状态经过逐层转换，形成能交给RHI的绘制描述：

```text
UPrimitiveComponent        游戏线程，可变状态
  → FPrimitiveSceneProxy   渲染侧表示
  → FMeshBatch             解耦 Pass 与 Proxy 的中间描述
  → FMeshDrawCommand       无状态，可排序、缓存、合并
  → RHICommandList         图形 API 命令
```

### FPrimitiveSceneProxy

Proxy 是组件在渲染线程的镜像。游戏线程随时改变组件属性，渲染线程需要一份稳定快照，Proxy 承担这个职责。

它通过两个回调向渲染器提交几何：`DrawStaticElements` 用于静态、可长期缓存的网格；`GetDynamicMeshElements` 用于每帧重新收集的动态网格。

场景渲染器先做可见性剔除，再调用 `GatherDynamicMeshElements` 遍历可见 Proxy。各 Proxy 子类在 `GetDynamicMeshElements` 中构造 `FMeshBatch` 并投递给 `FMeshElementCollector`。收集器保存这次收集所需的临时网格，具体分配和并行任务归属以项目源码为准。

### FMeshBatch

`FMeshBatch` 的存在意义是**解耦 Pass 与 Proxy**。Proxy 只描述“我有什么几何和材质”，不关心会被哪些 Pass 使用；Pass 只消费 MeshBatch，不需要知道几何来自静态网格、骨骼网格还是程序化组件。

一个 MeshBatch 持有一组 `FMeshBatchElement`（通常只用一个），它们共享同一材质与同一 Vertex Factory。Element 保存单次绘制所需的 Index Buffer、图元数量与逐实例的 Shader 参数。

### FMeshDrawCommand

这是整条链路的设计核心：**FMeshDrawCommand 是自包含的绘制描述**。

它只记录绘制所需的 Shader、资源绑定和绘制参数，不像 Component 那样需要维护变化与更新。显式保存状态和参数带来三个能力：可以按任意键排序、可以跨帧缓存、可以合并为更少的实际绘制。

`FSceneRenderer` 通过 `SetupMeshPass` 为每个 Pass 创建 `FMeshPassProcessor`，由它把 MeshBatch 转换为 MeshDrawCommand。转换在 `FMeshDrawCommandPassSetupTask` 中并行完成，最后由 `SubmitMeshDrawCommands` 翻译为 RHI 命令。

Pass 类型在 `MeshPassProcessor.h` 的 `EMeshPass` 枚举中集中声明。枚举用于标识通道类型。类型注册、处理器创建与渲染器执行调度需要分别核对；枚举排列不能独立证明运行时顺序。

### 排序键

MeshDrawCommand 使用对应通道的排序键组织绘制。具体位字段与优先级随通道和引擎版本变化，应核对 `FMeshDrawCommandSortKey` 和处理器生成逻辑。不能从一个通道推定全部绘制都按同一字段顺序排序。

高位字段决定粗粒度顺序，低位字段可让状态相近的命令彼此相邻。实际合并还要求Shader绑定、绘制参数和实例化条件兼容；排在一起只是机会，不保证合并。半透明 Pass 的排序键需要把深度编码进去，因为混合结果依赖顺序。

排序键设计直接影响合批效率。相同材质的物体在场景中散布时，按状态排序可以减少状态切换，收益由实际命令序列确认；但对半透明而言，正确顺序优先于合批。

## Vertex Factory

Vertex Factory 回答一个问题：顶点数据以什么布局存在，Shader 如何读取它。

静态网格、骨骼网格、GPU 蒙皮、实例化静态网格、地形、粒子——它们的顶点数据组织方式完全不同，但都要能配合同一批材质。Vertex Factory 就是这个适配层：材质定义“表面长什么样”，Vertex Factory 定义“顶点从哪来”，两者的组合决定实际编译哪些 Shader 变体。

这个笛卡尔积是 Unreal Shader 数量庞大的根源之一，也是 `ShouldCompilePermutation` 存在的原因——它逐一过滤掉无意义的组合。

### 三套顶点流

`FVertexFactory` 为不同 Pass 准备了不同精简程度的顶点声明：

- 完整流：Position、Tangent、UV、Color 等全部属性；
- `PositionOnly`：仅位置，供 Depth Only Pass 使用；
- `PositionAndNormal`：位置加法线，供需要法线的深度类 Pass 使用。

不透明且没有位移的深度绘制可以使用仅位置流。Masked 材质还要 UV 和 Alpha 测试，世界位置偏移也需要对应输入，处理器应按材质与 Vertex Factory 能力选择精简流。这是引擎层面对深度 Pass 的针对性优化。

### 顶点属性契约

顶点声明把缓冲中的字节解释为位置、法线和UV。每个元素必须同时给出缓冲流、字节偏移、步长、格式与Shader属性槽位。`FLocalVertexFactory`的具体槽位由该版本的`.ush`输入与C++声明共同约定；自定义工厂沿同一契约建立自己的输入。

下面是API中立布局示例，位置和法线为三个32位浮点数，UV为两个32位浮点数，总步长32字节：

```text
stream 0, stride 32 bytes
position: offset 0,  float3, attribute 0
normal:   offset 12, float3, attribute 1
uv:       offset 24, float2, attribute 2
```

这个示例描述一份自定义数据，不声称它就是`FLocalVertexFactory`的实际布局。若把法线偏移写成16，Shader会把法线后两项和UV第一项拼成一个向量；资源绑定本身仍合法，模型却会出现错误光照。用纯轴向法线和规则UV网格输入，检查顶点输入及顶点Shader输出，能够直接定位字节解释错误。

### 初始化与引用寿命

Vertex Factory创建声明之前，缓冲和数据描述必须已经建立。初始化读取尚未填充的描述，会生成空绑定；缓存绘制命令引用的缓冲如果提前释放，则会在后续帧使用失效资源。建立、更新、注销和释放都要落在目标版本允许的渲染线程或命令入口。

更新常量缓冲中的内容可以保留原绑定；替换缓冲对象或材质Shader会改变缓存命令引用的对象，必须触发相应缓存失效。判断“只改一个参数”是否安全，要看参数改变的是已绑定内存的值，还是绑定对象本身。

### Manual Vertex Fetch

平台支持时，Vertex Factory 会定义 `MANUAL_VERTEX_FETCH`，顶点数据通过 SRV 由 Shader 主动读取，而非经由固定的 Input Assembler 阶段。这能支持GPU根据索引随机读取顶点；是否采用它由Vertex Factory和平台路径决定。

由此产生了两条数据通路，扩展 Vertex Factory 时两条都要覆盖，否则会出现“在部分平台正常、另一些平台数据全零”的现象。

## 材质数据与附件边界

独立Mesh Pass可以把选中对象的遮罩写入单独纹理，后续全屏通道再消费它。这种需求只涉及本通道的输出格式。若数据需要参与已有延迟光照，就要检查GBuffer编解码和所有消费者，问题的维护范围会扩大到材质系统。

以1920×1080、单采样RGBA8附件为例，逻辑存储量为`1920×1080×4 = 8,294,400`字节，约7.91 MiB。实际分配还受对齐、压缩、分块与别名影响；读写带宽也不能仅用这份容量代替。多增加一个附件，会影响写入、后续读取与可能的片上驻留，需结合目标后端捕获验证。

Shading Model ID的位宽属于具体材质路径的编码约定。扩展前逐项查明写入格式、字段掩码、相邻位偏移、解码分支和平台消费者，再用ID往返测试确认。UE5不同版本、传统GBuffer与Substrate使用的表示存在差异；仅修改枚举数量不能证明新ID可以正确传输。布局的通用机制见[[13_渲染架构/GBuffer布局]]。

## 自定义 Mesh Pass

当效果需要独立的绘制批次——例如只有特定对象参与、需要写入专属 Buffer、或需要不同的渲染状态——就需要新增 Mesh Pass。

接入时先注册通道类型与处理器创建函数，再由 `FMeshPassProcessor` 筛选 MeshBatch，并选择 Shader 和渲染状态。场景渲染器显式调度通道，资源消费者和同步决定合法位置。枚举注册与实际执行顺序是两项工作。

处理器的筛选逻辑通常基于材质的 Shading Model、Blend Mode 或 Primitive 上的自定义标记。筛选条件写得过宽会让无关对象进入 Pass 造成浪费，过窄则效果缺失。

### 处理器的可验收路径

以“只画不透明选中对象到遮罩”为例，处理器先读取项目持有的选择标志，再检查材质混合模式。通过筛选的MeshBatch才进入Shader选择，Shader再与该批次的Vertex Factory配对。以下伪代码展开决策；`BuildMeshDrawCommands`对应UE处理器接口，参数细节由目标版本提供。

```text
AddMeshBatch(batch, primitive):
    if primitive.selectionFlag == false: return
    if batch.material.blendMode != Opaque: return
    shaderPair = permutation[batch.vertexFactoryType, MaskPass]
    if shaderPair missing: report material/factory/platform; return
    state = {depthTest: sceneDepthConvention, depthWrite: false,
             blend: replace, rasterCull: materialCullMode}
    bindings = {view: currentView, geometry: batch.buffers,
                primitive: primitive.uniforms}
    BuildMeshDrawCommands(batch, shaderPair, state, bindings)
```

设输入为三个批次：甲是选中不透明网格，乙是不透明未选中网格，丙是选中透明网格。筛选后只有甲产生命令，乙在选择标志处退出，丙在混合模式处退出。若甲仍未显示，就沿Shader配对、顶点输入、深度测试和输出消费者继续查；此时增加筛选范围只会引入无关对象。

通道绑定的遮罩必须先清零，否则未覆盖像素可能保留其他内容。使用场景深度测试得到可见部分遮罩；要显示被遮挡对象，则另定义深度规则。这个选择改变的是效果含义，不能仅靠关闭深度测试修复所有“缺失”。

缓存命令还要求`selectionFlag`变化能触发重建，或把选择信息放在可更新的实例数据并在Shader中处理。前者增加CPU重建，后者可能提交最终不产生有效像素的网格。固定同一选中集合比较处理器输入数、命令数与实际Draw，才能量化两者成本。

### 与 RDG 的配合

新 Pass 的资源应当通过 Render Dependency Graph 声明。RDG 依据声明的读写关系自动插入 Barrier、管理 Transient 资源、剔除无人消费的 Pass。

跨帧资源可以由外部所有者创建，再通过RDG的注册入口导入；图在声明的使用范围内追踪访问和转换，外部所有者负责图外寿命。导入资源通常不能像图内临时资源一样自由缩短分配寿命。真正需要避免的是未向图声明的读写，以及绕过图状态追踪的手工屏障：前者会让依赖和剔除失真，后者可能与图生成的转换冲突。接入通道时，先确认资源的所有者、导入方式与最终访问状态。

没有可观察输出或外部副作用的通道可以被 RDG 剔除。记录代码已经运行，执行回调却可能被省略。捕获中找不到通道时，检查后续消费者、外部资源及导出声明。

## 实现层次的选择

| 层次 | 能参与 | 升级成本 | 适用 |
|---|---|---|---|
| 材质 / Unlit | 自身着色 | 受材质接口变化影响 | 原型、局部风格化 |
| Post Process Material | 屏幕空间后处理 | 低 | 描边、屏幕效果 |
| Custom Depth / Stencil | 对象分类与遮罩 | 低 | 选中高亮、遮挡显示 |
| 扩展 GBuffer | 延迟光照的额外数据 | 中 | 自定义光照参数 |
| 自定义 Shading Model | 完整光照管线 | 高 | 皮肤、卡通等专用光照 |
| 自定义 Mesh Pass | 独立绘制批次 | 高 | 专用 Buffer、特殊状态 |

各层修改的是不同契约。新增内置`EMeshPass`并接入核心调度涉及引擎源码；通过现有动态绘制入口组织通道，修改范围主要落在提交入口，能力与缓存方式以该版本接口为准。材质与后处理通常由项目资产维护。选择时先列出所需输入、输出附件和绘制对象，再确定需要触及哪一层。

需要修改光照模型时，可由自定义 Shading Model 处理主体着色，用 GBuffer 携带附加参数。描边等屏幕效果可以单独放在后处理。选择依据是各部分需要的数据与执行阶段。

### 材质与通道的职责

屏幕描边读取深度和法线时，后处理入口已经具备主要输入。需要独立对象遮罩时，先建立对象绘制通道，再把遮罩交给全屏合成。若效果改变每个表面的光照响应，则要检查材质与光照阶段是否能传递所需参数。

风格化主光与附加光可以采用不同模型，但这是一项项目管线设计：必须交代主光阴影的生产者、材质读取方式、附加光累积和曝光阶段。延迟路径是否合适取决于所需参数能否被当前布局表达，以及修改后的带宽和维护成本；风格化本身不决定必须使用前向或延迟。

## 引擎改动的工程管理

源码级改动的真实成本不在首次实现，而在长期维护：

- 把改动集中在尽量少的文件，并用统一的注释标记包裹，便于升级时定位；
- 记录改动清单，标明每处改动的目的与对应的引擎版本；
- 新增 Shading Model 时同步检查所有分支该 ID 的代码路径，遗漏处会走到默认分支；
- 开启 `r.ShaderDevelopmentMode=1` 便于 Shader 调试，但不要带进发布配置。

## 验证方法

- 用 RenderDoc 确认新 Pass 出现在预期位置，检查其输入输出资源与渲染状态。
- 检查 Input Assembler 的顶点布局，确认属性槽位与 Shader 输入结构对应。
- 直接查看扩展的 GBuffer Target 内容，判断问题在写入侧还是读取侧。
- 统计 MeshDrawCommand 数量与合并后的实际绘制数，评估排序键的合批效果。
- 切换 Manual Vertex Fetch 的开关，两条通路都要验证。
- Pass 在 RenderDoc 中完全消失时，先检查其输出资源是否被后续 Pass 消费。
- 在移动端与桌面端分别验证，两者的 GBuffer 布局与可用 Pass 不同。

## 相关主题

- [[13_渲染架构/渲染命令的组织方式]]
- [[13_渲染架构/渲染路径与光源组织]]
- [[22_渲染引擎实现/引擎渲染扩展导读]]
- [[13_渲染架构/GBuffer布局]]
- [[13_渲染架构/Draw Call与合批]]
- [[03_Shader编程/Shader Variant管理]]
- [[11_NPR与风格化渲染/NPR材质与分层光照]]

## 参考资料

- Epic Games，[UE5.4 Mesh Drawing Pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/mesh-drawing-pipeline-in-unreal-engine?application_version=5.4)，Cached and Dynamic Mesh Batches、FMeshPassProcessor、Shader Bindings、Cached Mesh Draw Commands；2026-10-22核读。支持缓存与处理器职责，具体源码签名另验。
- Epic Games，[UE5.4 Render Dependency Graph](https://dev.epicgames.com/documentation/en-us/unreal-engine/render-dependency-graph-in-unreal-engine?application_version=5.4)，Shader Parameter Structs、Resource Lifetimes和Raster Passes；2026-10-22核读。
- 源码复现入口：项目checkout的`MeshPassProcessor.h`、`MeshBatch.h`、所用Vertex Factory及目标PassProcessor。本文未对一个完整引擎checkout执行补丁与编译。
