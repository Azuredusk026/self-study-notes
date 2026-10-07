# Unity渲染帧组织

同一个Renderer Feature在不同相机上出现两次，或者读不到预期颜色，先追踪实际renderer与相机角色。SRP提供组织入口，URP/HDRP各有资源与通道约束。沿管线资产、相机数据、剔除、绘制与提交查源码，比只按类名猜执行位置更可靠。

## 版本与证据

本篇采用 Unity 6.0（6000.0）文档与 URP 17 接口范围。Graphics 仓库的开发分支只用于查找类型；复现时将包版本与项目 manifest 锁定，再查看相同版本源码。核对日期为 2026-10-04，接口与官方文档已核对，本文示例为调用流程轮廓。

## 从资产到相机渲染

```text
RenderPipelineAsset.CreatePipeline
  → RenderPipeline 实例
  → 相机列表与剔除参数
  → ScriptableRenderContext.Cull
  → Renderer 组织阴影、深度、场景绘制和后处理
  → 记录图通道或兼容路径命令
  → ScriptableRenderContext.Submit
  → 底层提交与 GPU 执行
```

管线资产保存配置，运行时实例保存执行逻辑。URP 的 renderer data 选择具体 renderer 与 features。相机数据包括尺寸、render scale、HDR、MSAA、目标切片和堆栈角色；这些字段会改变实际通道和资源创建。

`Cull` 返回剔除结果。绘制路径消费结果和过滤设置，再组织提交。`Submit` 返回后 GPU 可能仍在执行，所以资源复用不能仅按 C# 方法结束时间判断。

## URP 前向与延迟路径

前向路径将材质与局部光照一起求值，Forward+ 提前建立灯光列表。延迟路径先写 GBuffer 再消费材质信息；透明通常仍需要专门的前向处理。具体 MRT 数量、渲染层、阴影遮罩和准确格式由包版本及配置决定。

深度、颜色和法线输入请求可能引入预通道、拷贝或已有结果复用。`ConfigureInput` 表达需求，但实际生成时机由 renderer 决定。相机颜色读取并不保证每个注入点都可用；检查当前颜色是否为 back buffer，以及是否已转换成可采样纹理。

## HDRP 的扩展边界

HDRP Custom Pass 使用固定注入点和对应的颜色、深度及 custom buffer。Volume 与曝光体系会影响输入内容。URP 的 renderer feature 代码需按 HDRP 资源与生命周期重新组织。

Custom Pass 前后读取的 scene color 可能分别处于不同曝光或后处理阶段。测试时先输出原输入，再逐项添加效果，确认颜色空间和预曝光关系。

## 相机堆栈与分辨率

Base/Overlay、反射、预览和 Scene View 相机可能重复触发 feature。每个通道应明确接受哪些相机，历史按相机或视图保存。XR 单通道实例化还要求正确的数组切片和屏幕坐标宏。

RTHandle 的分配尺寸与当前 viewport 可能不同。采样需使用对应缩放和 Blitter 路径。动态分辨率改变逻辑输出，历史是否重建由算法与资源描述决定；TAA 和超分的分辨率边界要同时检查。

## 设置与构建

| 配置 | 影响 | 核验方式 |
|---|---|---|
| Renderer 路径 | 前向、Forward+、延迟及资源需求 | 检查实际 renderer data 和捕获通道 |
| HDR / MSAA | 颜色格式、样本数、resolve | 查看相机目标与实际附件 |
| Depth / Opaque texture | 预通道或拷贝 | 查 Frame Debugger 生成和消费者 |
| Render Graph / Compatibility | 记录 API 与资源管理 | 在两种路径分别回归 |
| 关键字与 stripping | 可用变体和首次使用 | 构建日志、真机材质及 PSO 记录 |

Shader 关键字、剥离与预热的通用机制见编译专题。设置索引保留版本与实际作用，项目级建议需来自目标场景的实验。

## 验证方法

建立一个不透明网格、透明网格、主光与一盏附加光的场景。分别切换渲染路径、深度纹理、MSAA 和后处理，记录 Frame Debugger 通道与资源。再加入 Overlay、反射相机和动态分辨率，检查通道重复和历史串相机。

Development 构建用于定位，发布配置用于最终成本测量。记录包版本、图形 API、设备、画质和捕获日期。

## 相关主题

- [[22_渲染引擎实现/Unity与Unreal渲染扩展入口]]
- [[22_渲染引擎实现/URP Render Graph自定义Pass]]
- [[13_渲染架构/Forward Rendering与Forward+]]
- [[13_渲染架构/Deferred Rendering]]

示例与验证范围：代码按文中前提解释机制，完整类型、资源和项目状态需由接入工程补齐。本轮以正文、公式和调用范围复读为主，未执行此页的目标引擎运行与GPU性能实验。

## 参考资料

- [Unity 6 URP](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/urp-introduction.html)，管线配置与资源。
- [Unity ScriptableRenderContext](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Rendering.ScriptableRenderContext.html)。
- [UnityCsReference](https://github.com/Unity-Technologies/UnityCsReference/blob/master/Runtime/Export/RenderPipeline/ScriptableRenderContext.cs)，剔除与提交入口。
- Unity Graphics 包源码：`UniversalRenderPipeline.cs`、`UniversalRenderer.cs`、`ScriptableRenderer.cs`。
