# Unreal 网格绘制与自定义 Pass

在 Unreal 中加一种渲染效果，选择面很宽：改材质、加后处理、扩 GBuffer、加 Shading Model、加独立 Pass。选错层次的代价很高——做得太浅，效果无法参与光照与阴影；做得太深，每次引擎升级都要重新合并改动。

判断依据是效果需要进入哪些阶段、需要读写哪些数据，而不是"改底层更专业"。理解这条决策需要先看清网格数据如何走到 GPU。

## 从组件到绘制命令

Unreal 的网格绘制是一条逐级降维的转换链，每一级都在剥离状态、逼近硬件命令：

```text
UPrimitiveComponent        游戏线程，可变状态
  → FPrimitiveSceneProxy   渲染线程镜像
  → FMeshBatch             解耦 Pass 与 Proxy 的中间描述
  → FMeshDrawCommand       无状态，可排序、缓存、合并
  → RHICommandList         图形 API 命令
```

### FPrimitiveSceneProxy

Proxy 是组件在渲染线程的镜像。游戏线程随时改变组件属性，渲染线程需要一份稳定快照，Proxy 承担这个职责。

它通过两个回调向渲染器提交几何：`DrawStaticElements` 用于静态、可长期缓存的网格；`GetDynamicMeshElements` 用于每帧重新收集的动态网格。

场景渲染器先做可见性剔除，再调用 `GatherDynamicMeshElements` 遍历可见 Proxy。各 Proxy 子类在 `GetDynamicMeshElements` 中构造 `FMeshBatch` 并投递给 `FMeshElementCollector`。Collector 由 `FSceneRenderer` 创建，两者一一对应。

### FMeshBatch

`FMeshBatch` 的存在意义是**解耦 Pass 与 Proxy**。Proxy 只描述"我有什么几何和材质"，不关心会被哪些 Pass 使用；Pass 只消费 MeshBatch，不需要知道几何来自静态网格、骨骼网格还是程序化组件。

一个 MeshBatch 持有一组 `FMeshBatchElement`（通常只用一个），它们共享同一材质与同一 Vertex Factory。Element 保存单次绘制所需的 Index Buffer、图元数量与逐实例的 Shader 参数。

### FMeshDrawCommand

这是整条链路的设计核心：**FMeshDrawCommand 是完全无状态的**。

它只记录绘制所需的 Shader、资源绑定和绘制参数，不像 Component 那样需要维护变化与更新。无状态带来三个能力：可以按任意键排序、可以跨帧缓存、可以合并为更少的实际绘制。

`FSceneRenderer` 通过 `SetupMeshPass` 为每个 Pass 创建 `FMeshPassProcessor`，由它把 MeshBatch 转换为 MeshDrawCommand。转换在 `FMeshDrawCommandPassSetupTask` 中并行完成，最后由 `SubmitMeshDrawCommands` 翻译为 RHI 命令。

Pass 类型在 `MeshPassProcessor.h` 的 `EMeshPass` 枚举中集中声明。这个枚举既是注册表也是顺序表，添加自定义 Pass 的第一步就是在此登记。

### 排序键

MeshDrawCommand 的排序由一个打包成整数的排序键决定，通常自高位到低位依次编码：Pass 内的优先级、是否半透明、管线状态、Vertex Factory、Shader 绑定、材质资源。

高位字段决定粗粒度顺序，低位字段让状态相同的命令彼此相邻，从而被合并成更少的绘制。半透明 Pass 的排序键需要把深度编码进去，因为混合结果依赖顺序。

排序键设计直接影响合批效率。相同材质的物体在场景中散布时，按状态排序能显著减少 SetPass；但对半透明而言，正确顺序优先于合批。

## Vertex Factory

Vertex Factory 回答一个问题：顶点数据以什么布局存在，Shader 如何读取它。

静态网格、骨骼网格、GPU 蒙皮、实例化静态网格、地形、粒子——它们的顶点数据组织方式完全不同，但都要能配合同一批材质。Vertex Factory 就是这个适配层：材质定义"表面长什么样"，Vertex Factory 定义"顶点从哪来"，两者的组合决定实际编译哪些 Shader 变体。

这个笛卡尔积是 Unreal Shader 数量庞大的根源之一，也是 `ShouldCompilePermutation` 存在的原因——它逐一过滤掉无意义的组合。

### 三套顶点流

`FVertexFactory` 为不同 Pass 准备了不同精简程度的顶点声明：

- 完整流：Position、Tangent、UV、Color 等全部属性；
- `PositionOnly`：仅位置，供 Depth Only Pass 使用；
- `PositionAndNormal`：位置加法线，供需要法线的深度类 Pass 使用。

Depth Prepass 与 Shadow Depth 只需位置，使用精简流可以显著降低顶点带宽。这是引擎层面对深度 Pass 的针对性优化。

### 顶点元素顺序必须与 Shader 对应

`GetVertexElements` 按属性槽位依次添加顶点元素，`FLocalVertexFactory` 的约定是位置占 ATTRIBUTE0、切线基占 ATTRIBUTE1 与 2、顶点色占 ATTRIBUTE3：

```cpp
if (Data.PositionComponent.VertexBuffer != nullptr)
{
    Elements.Add(AccessStreamComponent(Data.PositionComponent, 0, InOutStreams));
}
for (int32 AxisIndex = 0; AxisIndex < 2; AxisIndex++)
{
    if (Data.TangentBasisComponents[AxisIndex].VertexBuffer != nullptr)
    {
        Elements.Add(AccessStreamComponent(
            Data.TangentBasisComponents[AxisIndex],
            TangentBasisAttributes[AxisIndex], InOutStreams));
    }
}
if (Data.ColorComponent.VertexBuffer)
{
    Elements.Add(AccessStreamComponent(Data.ColorComponent, 3, InOutStreams));
    OutColorStreamIndex = Elements.Last().StreamIndex;
}
InitDeclaration(Elements);
```

这里的顺序必须与 `.ush` 中输入结构的语义槽位一一对应。顺序错位不会报编译错误，表现为顶点属性被解释成错误的数据——常见现象是模型撕裂、UV 错乱或顶点色变成法线数据。用 RenderDoc 查看 Input Assembler 的顶点布局是最直接的排查方式。

顶点色的类型必须是 `VET_Color`。用其他类型传入时，ES3 与 Metal 平台会按平台约定做通道交换，导致颜色分量顺序错误。

### 初始化顺序

Proxy 在 `CreateRenderThreadResources` 中填好 `FDataType` 后，必须先 `SetData` 再 `InitResource`：

```cpp
FXXXVertexFactory::FDataType Data;
InitVertexFactoryComponents(/* ... */, Data /* ... */);
VertexFactory.SetData(RHICmdList, Data);  // 必须在前
VertexFactory.InitResource(RHICmdList);
```

`InitRHI` 会读取 Data 的内容来填充 Uniform Buffer 并创建顶点声明，顺序颠倒会得到空绑定。

### Manual Vertex Fetch

平台支持时，Vertex Factory 会定义 `MANUAL_VERTEX_FETCH`，顶点数据通过 SRV 由 Shader 主动读取，而非经由固定的 Input Assembler 阶段。这对 GPU-Driven 路径和需要随机访问顶点的场景是必要的。

由此产生了两条数据通路，扩展 Vertex Factory 时两条都要覆盖，否则会出现"在部分平台正常、另一些平台数据全零"的现象。

## 扩展 GBuffer

需要为自定义光照携带额外的逐像素数据时，扩展 GBuffer 是直接的做法。它同时涉及 C++ 的布局声明与 HLSL 的编解码，两侧必须严格一致。

关键改动集中在三处：`GBufferInfo.h/.cpp` 声明新的 Slot 与格式，`ShaderGenerationUtil.cpp` 添加对应的写入配置，以及 `.ush` 中的打包与解包函数。任一侧遗漏都会让数据看似写入却读不出来——用 RenderDoc 直接查看该 Render Target 的内容是判断卡在哪一侧的最快方法。

代价是实打实的：每增加一张 RGBA8 的全屏 Target，1080p 下约增加 8 MB 显存与相应的每帧读写带宽。移动端尤其敏感。

### Shading Model 数量上限

Unreal 默认的 Shading Model 上限是 16。这个数字不是随意规定的——ShadingModelID 存储在 GBufferB 的 Alpha 通道低 4 位，$2^4=16$ 就是硬上限。

突破它需要同步修改六处，只改其中一部分会编译通过但行为错误：

| 位置 | 改动 |
|---|---|
| `GBufferInfo.cpp` | GBufferB 格式由 RGBA8 改为 RGBA16 |
| `GBufferInfo.h` | 新增 8 位的 `EGBufferCompression` 类型 |
| `ShaderGenerationUtil.cpp` | 为新压缩类型添加配置项 |
| `GBufferInfo.cpp` | ShadingModelID 占 8 位，`SelectiveOutputMask` 起始位由 4 改为 8 |
| `EngineTypes.h` | 数量上限警告由 16 改为 256 |
| `DeferredShadingCommon.ush` | 掩码由 `0xF` 改为 `0xFF`，编解码由 `0xFF` 改为 `0xFFFF`，BasePass 中的移位由 4 改为 8 |

只改 C++ 侧的典型症状是：引擎里能选到新 Shading Model，但 ID 读出来不对、分支不生效——因为编解码仍按 4 位掩码截断。

这条改动链清楚地显示了 GBuffer 布局的牵连范围：一个位宽变更会波及格式、压缩配置、相邻字段偏移、掩码和移位五类代码。

> [!warning] 待补充
> 上述改动基于 Unreal Engine 5.4。GBuffer 布局与 `GBufferInfo` 的组织在 UE5 各版本间有过调整，Substrate 材质系统启用后的路径更是完全不同。移植到其他版本前需要核对对应版本的源码。

## 自定义 Mesh Pass

当效果需要独立的绘制批次——例如只有特定对象参与、需要写入专属 Buffer、或需要不同的渲染状态——就需要新增 Mesh Pass。

主要工作量在于登记：在 `EMeshPass` 枚举中添加类型并确定执行顺序，实现继承自 `FMeshPassProcessor` 的处理器决定哪些 MeshBatch 进入本 Pass、使用什么 Shader 与渲染状态，注册处理器创建函数，并在场景渲染器的合适位置调度这个 Pass。

处理器的筛选逻辑通常基于材质的 Shading Model、Blend Mode 或 Primitive 上的自定义标记。筛选条件写得过宽会让无关对象进入 Pass 造成浪费，过窄则效果缺失。

### 与 RDG 的配合

新 Pass 的资源应当通过 Render Dependency Graph 声明。RDG 依据声明的读写关系自动插入 Barrier、管理 Transient 资源、剔除无人消费的 Pass。

手工管理资源生命周期会与图系统冲突：手动创建的资源不参与别名复用，手动插入的 Barrier 可能与 RDG 生成的重复或矛盾。修改引擎渲染代码前，先确认目标代码路径是否仍走 RDG。

RDG 的 Pass 剔除还有一个容易困惑的表现：如果新 Pass 写入的资源没有任何后续 Pass 读取，整个 Pass 会被静默剔除，表现为"代码执行了但 RenderDoc 里找不到这个 Pass"。

## 实现层次的选择

| 层次 | 能参与 | 升级成本 | 适用 |
|---|---|---|---|
| 材质 / Unlit | 自身着色 | 无 | 原型、局部风格化 |
| Post Process Material | 屏幕空间后处理 | 低 | 描边、屏幕效果 |
| Custom Depth / Stencil | 对象分类与遮罩 | 低 | 选中高亮、遮挡显示 |
| 扩展 GBuffer | 延迟光照的额外数据 | 中 | 自定义光照参数 |
| 自定义 Shading Model | 完整光照管线 | 高 | 皮肤、卡通等专用光照 |
| 自定义 Mesh Pass | 独立绘制批次 | 高 | 专用 Buffer、特殊状态 |

越往下能力越强，与引擎版本的耦合也越深。自定义 Shading Model 与 Mesh Pass 都需要修改引擎源码，意味着每次升级都要重新合并；材质与后处理层的方案则可以完全留在项目内。

实践中常见的组合是：主体效果用自定义 Shading Model 进入光照管线，辅助数据通过扩展 GBuffer 携带，描边等屏幕效果用 Post Process Material 实现——把需要深度集成的部分下沉，其余留在上层。

### 延迟路径对风格化渲染的约束

风格化渲染与延迟渲染在设计哲学上存在冲突，这个冲突值得单独说明，因为它决定了架构选型。

卡通渲染本质是各类技巧的堆叠：有的项目只需指定亮暗两色，有的用一维 Ramp 控制过渡，有的用二维 Ramp 让不同部位有不同过渡曲线，再加上描边、面部 SDF、鼻尖高光、各类头发高光与边缘光。

延迟渲染要求所有材质把数据写进统一的 GBuffer，再由统一的光照阶段消费。要让一个固定的 GBuffer 同时支持这些做法，它会迅速膨胀到无法承受——而且仍然无法覆盖尚未出现的新技巧。

一种解法是按光源类型拆分职责：

- **主光的着色交给材质**，走前向路径。主光决定大明暗，是风格差异最集中的地方，交给材质图意味着项目可以自由决定着色方式，不必把代码写死在引擎里；
- **多光源仍走延迟**。附加光的计算不会有太多花样，且前向路径下多光源代价高，延迟更合适。

关键在于让材质能够访问光照相关数据。做法是在 Light Pass 之后插入一个专用 Pass，把阴影等信息传递进去，材质图便可读取这些数据完成主光着色。

这与"在自发光里做卡渲"的区别正在于此：后者完全脱离光照管线，拿不到阴影与多光源；前者保留了这些能力，同时把着色决策权交还给项目。

这个案例说明了扩展层次选择的实质——不是在"浅"与"深"之间二选一，而是按数据流拆分，让每部分落在最合适的层次。

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

- [[13_引擎架构与资源系统/Render Pass、Command Buffer与Render Graph]]
- [[13_引擎架构与资源系统/Forward、Deferred与Clustered渲染]]
- [[13_引擎架构与资源系统/Unity与Unreal渲染扩展入口]]
- [[13_引擎架构与资源系统/GBuffer布局设计与通道压缩]]
- [[13_引擎架构与资源系统/Draw Call、Batching与GPU Instancing]]
- [[03_Shader编程/Shader编译、关键字与变体]]
- [[11_NPR与风格化渲染/NPR材质与分层光照]]

## 参考资料

- Epic Games, *Mesh Drawing Pipeline* documentation.
- Unreal Engine source, `MeshPassProcessor.h`, `MeshBatch.h`, `LocalVertexFactory.cpp`, `GBufferInfo.cpp`, `DeferredShadingCommon.ush`.
- Epic Games, *Render Dependency Graph* documentation.
- 向往, Unreal Engine 渲染系统源码剖析系列。
