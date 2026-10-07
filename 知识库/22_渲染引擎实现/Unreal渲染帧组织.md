# Unreal渲染帧组织

游戏线程里对象已经改变，渲染帧却还用旧状态，先看更新怎样交给场景代理与渲染任务。Renderer组织可见性和通道，RDG安排资源，RHI表达后端请求。把这几个边界连起来，才能知道修改应放在哪一层，以及捕获里的命令对应哪份场景数据。

## 版本与证据范围

本篇按 UE5 官方 Renderer、RDG 与 Mesh Drawing Pipeline 文档中的稳定概念组织。具体方法签名、源码行号、GPUScene 和 Nanite 路径以项目 checkout 为准。文档核对日期为 2026-10-04，未将未运行的示例标记为引擎实验。

## 数据与线程边界

```text
游戏线程：Component 与游戏状态
  → SceneProxy / 场景更新
渲染线程及任务：可见性、MeshBatch、通道组织
  → RDG 声明与编译
RHI 命令列表：资源、绘制与同步请求
  → D3D12 / Vulkan / Metal 后端
GPU 队列：执行与完成
```

SceneProxy 是渲染侧表示，不能假设它是游戏组件的实时可变镜像。更新按引擎跨线程消息与资源生命周期完成。RHI 线程是软件任务分工，实际后端队列由平台能力决定。

## 网格与全屏功能

网格通道常经过 MeshBatch、PassProcessor、MeshDrawCommand，再提交排序和缓存后的命令。后处理或计算功能常直接以 RDG 全屏或计算通道表达，两者可以使用同一帧的资源。

`EMeshPass` 类型注册不自动决定运行时顺序；场景渲染器需要显式调度。源码改动应记录注册、处理器、Shader 类型、资源、消费者和执行位置。

## Shader 与参数

Global Shader 适合独立的全屏或计算功能。Material Shader 与 VertexFactory 组合表达不同几何输入及材质逻辑。Permutation 控制编译组合，`ShouldCompilePermutation` 根据平台能力排除无效组合。

参数结构让引擎生成绑定信息，RDG 参数还提供资源访问声明。静态开关会影响 Shader 组合，附件格式和深度混合状态进一步影响 PSO。减少组合需要同时检查构建日志、包体、运行内存和首用卡顿。

## 自定义功能的定位

一个原型先确认输入和输出：后处理颜色、独立对象 buffer，还是参与 GBuffer 和光照。可用项目插件或现有扩展入口表达时，按该版本接口接入；涉及核心材质编码、网格通道注册与布局时，需要对照引擎源码。

```text
定义输入/输出
  → 选择 Material / View Extension / RDG / Mesh Pass 入口
  → 注册 Shader 与参数
  → 声明资源消费者
  → 捕获通道、参数和输出
```

这是接入步骤轮廓，具体入口可用范围需项目版本核对。不要把一种版本的类名当成所有 UE5 的统一配方。

## 配置与观测

| 配置或工具 | 用途 | 核验 |
|---|---|---|
| `r.ShaderDevelopmentMode` | 开发期 Shader 诊断 | 发布配置关闭，记录编译日志 |
| `r.RDG.*` 调试变量 | 图执行、资源与剔除诊断 | 用控制台帮助或源码核对当前版本 |
| stat GPU / GPU profiler | 通道耗时 | 与捕获负载、构建类型配对 |
| Unreal Insights | CPU 任务、线程等待与加载 | 看关键路径和事件关联 |
| RenderDoc / 平台工具 | 实际资源与 GPU 命令 | 检查目标后端是否支持捕获 |

变量名和默认值由版本决定；参数表应记录项目实际值、来源和预期通道变化。编辑器和 Shipping 性能要分别记录。

## 验证方法

- 给新通道唯一事件名，在 GPU 捕获中确认实际位置与资源格式。
- 停用输出消费者，检查通道和资源是否按图语义变化。
- 在双视图、阴影、透明和不同画质下检查 Shader 组合。
- 捕获游戏线程、渲染线程与 GPU，判断卡顿是编译、记录、等待还是执行。
- 升级引擎时重新检查类型注册、参数结构、消费者和平台实现。

## 相关主题

- [[22_渲染引擎实现/Unreal RDG Pass实现]]
- [[22_渲染引擎实现/Unreal自定义Mesh Pass]]
- [[14_性能分析与优化/PSO首次使用为什么卡顿]]

示例与验证范围：代码按文中前提解释机制，完整类型、资源和项目状态需由接入工程补齐。本轮以正文、公式和调用范围复读为主，未执行此页的目标引擎运行与GPU性能实验。

## 参考资料

- [Unreal RDG](https://dev.epicgames.com/documentation/en-us/unreal-engine/render-dependency-graph-in-unreal-engine)。
- [Unreal Mesh Drawing Pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/mesh-drawing-pipeline-in-unreal-engine)。
- Epic Games，Shader Development、Unreal Insights 与 Graphics Programming 官方文档。
- 源码定位：`Renderer/Private`、`RenderGraphBuilder.h`、`RHICommandList.h`、`MeshPassProcessor.h`。
