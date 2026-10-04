# Unity Render Graph 与自定义通道

Unity 6 URP 的渲染图通道通过记录阶段声明纹理访问，在执行回调中录制绘制命令。两阶段之间资源由图管理，通道应以句柄传递依赖，避免把隐藏的全局纹理读写留给图猜测。

## 适用环境

接口范围为 Unity 6.0 / URP 17 的 Render Graph 路径，核对日期 2026-10-04。以下代码为自定义 `ScriptableRenderPass` 内的方法片段，使用官方记录模式；类壳、材质资产和 feature 入队代码由项目提供。本轮未执行完整 Unity 工程编译。

## 记录、执行与输出交接

```text
Renderer Feature.Create：建立材质和通道
  → AddRenderPasses：按相机条件入队
  → RecordRenderGraph：声明输入、输出和回调
  → 图编译：剔除、分配、同步与合并
  → 回调：读取 PassData，记录实际绘制
```

Feature 的 `Create` 可能因编辑器重建多次调用，需处理已有资源。长期对象在 Dispose 时释放；图内纹理由图管理。旧式 `Execute` 路径不能直接当成渲染图回调使用。

## 最小材质 Blit

输入是当前相机颜色，输出是图内的新颜色纹理。输出句柄交回相机资源，使后续通道消费它。所选注入点需位于可采样颜色可用的阶段。

```csharp
public override void RecordRenderGraph(RenderGraph graph, ContextContainer frameData)
{
    UniversalResourceData resources = frameData.Get<UniversalResourceData>();
    if (resources.isActiveTargetBackBuffer) return;
    TextureHandle source = resources.activeColorTexture;
    TextureDesc descriptor = graph.GetTextureDesc(source);
    descriptor.name = "CustomColor";
    descriptor.clearBuffer = false;
    TextureHandle destination = graph.CreateTexture(descriptor);
    using (IRasterRenderGraphBuilder builder =
        graph.AddRasterRenderPass<PassData>("CustomColor", out PassData data))
    {
        data.Source = source;
        data.Material = m_Material;
        builder.UseTexture(source, AccessFlags.Read);
        builder.SetRenderAttachment(destination, 0, AccessFlags.Write);
        builder.SetRenderFunc((PassData passData, RasterGraphContext context) =>
        {
            Blitter.BlitTexture(context.cmd, passData.Source,
                new Vector4(1, 1, 0, 0), passData.Material, 0);
        });
    }
    resources.cameraColor = destination;
}
```

`PassData` 包含 `TextureHandle Source` 与 `Material Material`。方法省略命名空间，主要来自 Rendering、RenderGraphModule 与 Universal。材质需兼容 URP Blitter 和 XR 采样路径。完整覆盖才允许不清除目标，片元丢弃或局部 viewport 时应处理未写区域。

颜色格式与样本数继承输入，MSAA 输入是否可以直接采样需按资源状态和算法确认。回调中的缩放向量示例适用于完整区域；RTHandle 缩放、XR 和动态尺寸用官方 Blitter 约定核对。

## 常见错误

只创建和写出纹理，却没有后续读者或相机资源交接，通道可能被剔除。诊断时可以暂时禁用剔除，正式路径应建立消费者。

把同一颜色同时作为采样源和附件写入可能构成反馈回路。通常分配不同输出或采用明确支持的 local read 路径。外部全局纹理发布还涉及依赖跟踪，优先使用明确的传递和引擎支持的全局声明接口。

材质参数在记录后、执行前被其他相机修改，会让回调读到不符合该相机的状态。逐视图数据保存在 PassData 或受控参数缓冲中。

## Frame Debugger 与图查看器

Frame Debugger 展示绘制、附件和结果，图查看器展示逻辑通道、资源寿命及合并。看不到通道时先确认相机筛选、入队、消费者和剔除。合并可能改变捕获中看到的 API 通道边界，应结合图名称定位。

## 验证方法

- 用纯色材质确认注入位置，再换成采样原输入的材质。
- 故意去掉输出交接，检查通道剔除；恢复后检查资源依赖。
- 添加两个相机与 Overlay，确认每个视图的数据独立。
- 切换 MSAA、render scale 与 XR，查看实际尺寸、切片和 resolve。
- 检查图内新纹理数量与峰值，确认没有每帧常驻资源泄漏。

## 相关主题

- [[13_引擎架构与资源系统/Unity SRP、URP与HDRP帧组织]]
- [[13_引擎架构与资源系统/渲染图、依赖编译与资源调度]]
- [[13_引擎架构与资源系统/资源绑定、描述符与材质数据组织]]

## 参考资料

- [Unity 6 Write a Render Pass](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/render-graph-write-render-pass.html)。
- [Unity 6 Render Graph](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/render-graph.html)。
- Unity Graphics 包源码：`ScriptableRenderPass.cs`、`UniversalResourceData.cs`、`DrawObjectsPass.cs`；复现时锁定 URP 17 源码。
