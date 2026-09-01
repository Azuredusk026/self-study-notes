# Unity 与 Unreal 渲染扩展入口

引擎扩展的重点不是记住某个类名，而是确认插入位置、输入输出资源、相机范围、平台路径和版本边界。

## Unity Built-in Pipeline

常见入口：

- Camera Event + CommandBuffer；
- `OnRenderImage`；
- Replacement Shader；
- GrabPass；
- Surface Shader 和多 Pass ShaderLab。

它们仍可能出现在旧项目中，但不代表适合新 URP/HDRP。GrabPass 尤其容易产生昂贵的屏幕拷贝。

## Scriptable Render Pipeline

SRP 让 C# 代码显式组织可见性、Draw、Render Target 和 Pass。URP/HDRP 都建立在 SRP 上，但提供不同功能和扩展约束。

### URP Renderer Feature/Pass

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

### HDRP Custom Pass

HDRP 提供 Custom Pass Injection Point 和专用 Buffer 接口。它的材质、Custom Buffer 和曝光体系与 URP 不同，不能直接移植 Renderer Feature。

## Unity Shader 与渲染层

- ShaderLab Pass/LightMode 决定某个 Pass 在管线何处被选择；
- Render Queue 和 Sorting 控制绘制顺序；
- Rendering Layer/Layer Mask 控制对象、灯和 Feature 范围；
- Volume Framework 管理相机区域内的后处理参数。

## Unreal Material

Material Graph 生成目标 Shading Model 和 Pass 所需 Shader。Material Domain、Blend Mode、Shading Model、Two Sided 等设置会影响生成哪些变体和管线路径。

Unlit Material 只表示不走常规受光模型，不代表没有 Base Pass、Depth、Translucency 或后处理成本。

## Custom Depth 和 Stencil

Unreal 可以让选定对象写 Custom Depth/Stencil，再在 Post Process Material 中读取，用于描边、遮挡显示和分类效果。

需要处理：

- Translucent 是否写 Custom Depth；
- Stencil 位和项目分配；
- TAA 前后执行位置；
- 分辨率和 Upsampling；
- 被遮挡和可见部分的深度比较。

## Post Process Material

通过 Blendable Location 插入后处理。不同位置提供不同 Scene Color 状态：HDR、Tone Mapping 前后、Translucency 前后可能不同。

材质必须明确读取的 Scene Texture 是否在当前路径可用。

## Niagara

Niagara 是 Unreal 的数据驱动 VFX 系统，包含 System、Emitter、Particle 和 Render 阶段。Simulation 可以在 CPU 或 GPU。

GPU Simulation 适合大量粒子，但：

- 与 CPU Gameplay 交互受限；
- GPU Readback 有延迟；
- Collision、Sort 和透明 Overdraw 仍昂贵；
- Data Interface 访问需要理解同步和资源生命周期。

## Unreal Render Dependency Graph

RDG 与一般 Render Graph 思路一致：Pass 声明资源依赖，系统管理 Barrier、Transient Resource 和 Pass Culling。

修改引擎渲染时要先确认目标代码仍走 RDG，避免手动资源生命周期与图系统冲突。

## 修改 Shading Model 还是材质实现

### 材质/Unlit 实现

适合原型、局部风格化和不需要深度集成的效果。迭代快，但可能无法参与完整 GBuffer、光照、阴影和路径追踪。

### 自定义 Shading Model

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

## 相关主题

- [[13_引擎架构与资源系统/Render Pass、Command Buffer与Render Graph]]
- [[03_Shader编程/Shader编译、关键字与变体]]
- [[11_NPR与风格化渲染/描边、Billboard与场景风格化]]
- [[14_性能分析与优化/Profiler、RenderDoc与单帧分析]]

## 参考资料

- Unity Manual, URP/HDRP custom rendering documentation.
- Unreal Engine Documentation, *Materials*, *Custom Depth* and *Render Dependency Graph*.
- Unity and Unreal release notes for the target project version.
