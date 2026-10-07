# Unity与Unreal渲染扩展入口

引擎扩展的重点是确认插入位置、输入输出资源、相机范围、平台路径和版本边界；类名会随版本变化，这些约束不会。

## Unity 的管线与资源入口

### Unity Built-in Pipeline

常见入口：

- Camera Event + CommandBuffer；
- `OnRenderImage`；
- Replacement Shader；
- GrabPass；
- Surface Shader 和多 Pass ShaderLab。

这些入口适用于 Built-in 管线。URP/HDRP 使用各自扩展接口，接入前确认当前管线。GrabPass 尤其容易产生昂贵的屏幕拷贝。

### Scriptable Render Pipeline

SRP 让 C# 代码显式组织可见性、Draw、Render Target 和 Pass。URP/HDRP 都建立在 SRP 上，但提供不同功能和扩展约束。

一条自定义管线只需两样东西：一个继承 `RenderPipeline` 的实例类，一个继承 `RenderPipelineAsset` 的资产类。前者重写 `Render` 方法组织渲染流程，后者负责创建实例并作为资产被项目引用。

`ScriptableRenderContext` 连接 C# 管线与底层渲染代码。`Cull` 执行场景剔除并返回可供后续绘制使用的 `CullingResults`；绘制和命令缓冲执行请求由上下文组织，再通过 `Submit` 提交渲染工作。提交返回与 GPU 完成是不同时间点。调试时分别检查剔除结果、绘制记录、提交和 GPU 资源生命周期。

#### URP Renderer Feature/Pass

常见流程：

1. Renderer Feature 创建并配置 Pass；
2. 根据 Camera 和设置决定是否 Enqueue；
3. Pass 声明需要的 Color/Depth/Normal；
4. 在指定 RenderPassEvent 执行；
5. 使用 RTHandle/Render Graph 管理分辨率和资源。

需要考虑：

- Base/Overlay Camera Stack；
- Scene View、Preview、Reflection Camera；
- XR Single Pass；
- Dynamic Resolution 和 Render Scale；
- MSAA Resolve；
- 新旧 Compatibility/Render Graph 路径。

Feature 不是唯一入口。不需要编辑器配置界面、或希望完全由代码控制插入时机时，也可以在管线回调中直接向 Renderer 入队 Pass。Feature 的价值在于把 Pass 暴露为资产上的可配置项，便于美术调整和按 Renderer 切换。

##### 全屏 Blit 的浪费

后处理中常见的写法是先把源拷到临时目标，再带材质拷回去：

```text
Blit(source, temp);        // 纯拷贝
Blit(temp, source, mat);   // 带效果
```

第一次拷贝存在的原因是同一张 RT 不能同时作为采样源和写入目标。常规全屏采样路径不能把同一子资源同时作为输入和输出。专用 framebuffer fetch 或反馈回路扩展有自己的约束，不能依赖某台开发机偶然得到正确结果。

需要保留原输入时，这次拷贝有明确用途。多效果串联可以在两张 RT 间交替写入，或合并兼容效果，减少专门的保留拷贝。是否能省掉拷贝取决于后续使用者和读写关系；移动端需测量全屏读写带宽及附件存储成本。

#### HDRP Custom Pass

HDRP 提供 Custom Pass Injection Point 和专用 Buffer 接口。它的材质、Custom Buffer 和曝光体系与 URP 不同，不能直接移植 Renderer Feature。

### Unity Shader 与渲染层

- ShaderLab Pass/LightMode 决定某个 Pass 在管线何处被选择；
- Render Queue 和 Sorting 控制绘制顺序；
- Rendering Layer/Layer Mask 控制对象、灯和 Feature 范围；
- Volume Framework 管理相机区域内的后处理参数。

## Unreal 的材质与绘制入口

### Unreal Material

Material Graph 生成目标 Shading Model 和 Pass 所需 Shader。Material Domain、Blend Mode、Shading Model、Two Sided 等设置会影响生成哪些变体和管线路径。

Unlit Material 只表示不走常规受光模型，不代表没有 Base Pass、Depth、Translucency 或后处理成本。

### Custom Depth 和 Stencil

Unreal 可以让选定对象写 Custom Depth/Stencil，再在 Post Process Material 中读取，用于描边、遮挡显示和分类效果。

需要处理：

- Translucent 是否写 Custom Depth；
- Stencil 位和项目分配；
- TAA 前后执行位置；
- 分辨率和 Upsampling；
- 被遮挡和可见部分的深度比较。

### Post Process Material

通过 Blendable Location 插入后处理。不同位置提供不同 Scene Color 状态：HDR、Tone Mapping 前后、Translucency 前后可能不同。

材质必须明确读取的 Scene Texture 是否在当前路径可用。

### Niagara

Niagara 是 Unreal 的数据驱动 VFX 系统，包含 System、Emitter、Particle 和 Render 阶段。Simulation 可以在 CPU 或 GPU。

GPU Simulation 适合大量粒子，但：

- 与 CPU Gameplay 交互受限；
- GPU Readback 有延迟；
- Collision、Sort 和透明 Overdraw 仍昂贵；
- Data Interface 访问需要理解同步和资源生命周期。

### Unreal Render Dependency Graph

RDG 与一般 Render Graph 思路一致：Pass 声明资源依赖，系统管理 Barrier、Transient Resource 和 Pass Culling。

修改引擎渲染时要先确认目标代码仍走 RDG，避免手动资源生命周期与图系统冲突。

### 修改 Shading Model 还是材质实现

#### 材质/Unlit 实现

适合原型、局部风格化和不需要深度集成的效果。迭代快，但可能无法参与完整 GBuffer、光照、阴影和路径追踪。

#### 自定义 Shading Model

可以进入引擎材质和光照管线，但需要修改枚举、GBuffer 编码、Base Pass、Deferred Lighting、Shader 编译和编辑器。升级维护成本高。

选择取决于效果需要进入哪些 Pass，而不是“改底层更专业”。

## 版本核验

Unity URP/HDRP 和 Unreal 每个大版本都会调整接口、Render Graph 和默认路径。笔记应记录：

- 引擎版本；
- Render Pipeline/Renderer；
- Desktop/Mobile；
- Forward/Deferred；
- XR、Nanite、Lumen 等开关。

不带版本的内部实现只能作为概念说明。

### Unity 渲染功能的生命周期入口

下面以提供 `SetupRenderPasses` 的 URP 版本为例。Feature 创建 Pass，在资源句柄可用的回调中配置目标，再决定每个相机是否入队：

```csharp
sealed class OutlineFeature : ScriptableRendererFeature
{
    OutlinePass pass;

    public override void Create() => pass = new OutlinePass();

    public override void SetupRenderPasses(
        ScriptableRenderer renderer, in RenderingData data)
    {
        if (data.cameraData.cameraType != CameraType.Game) return;
        pass.Setup(renderer.cameraColorTargetHandle);
    }

    public override void AddRenderPasses(
        ScriptableRenderer renderer, ref RenderingData data)
    {
        if (data.cameraData.cameraType != CameraType.Game) return;
        renderer.EnqueuePass(pass);
    }
}
```

Pass 内部需要声明读写的颜色、深度或法线资源，并选择稳定的插入事件。启用 Render Graph 的 URP 版本还要在 `RecordRenderGraph` 中声明资源使用。相机堆叠、Scene View 和 XR 会改变调用次数与资源生命周期。验证时记录每个相机的 Pass 入队次数，并在 Frame Debugger 中确认插入位置和资源状态。

## 相关主题

- [[13_渲染架构/Render Pass、Command Buffer与Render Graph]]
- [[03_Shader编程/Shader Variant管理]]
- [[11_NPR与风格化渲染/描边、Billboard与场景风格化]]
- [[14_性能分析与优化/帧捕获与性能分析工具]]

## 参考资料

- Unity Manual, URP/HDRP custom rendering documentation.
- Unreal Engine Documentation, *Materials*, *Custom Depth* and *Render Dependency Graph*.
- Unity and Unreal release notes for the target project version.
- Unity Blog, *SRP Batcher: Speed up your rendering*.
- Unity Manual, *Scriptable Render Pipeline* and `ScriptableRenderContext` API reference.
