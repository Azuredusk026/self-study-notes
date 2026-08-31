# Changelog

## Unreleased

### P0 - 治理与架构

- 建立根 `AGENTS.md` 和 Autonomous Implementation Mode。
- 完成全 Vault 文件审计、Markdown 标题提取和 PPTX 页面索引。
- 建立来源迁移台账、诊断报告和正式文章清单。
- 建立新的知识地图、维护方法和统一术语表。
- 将旧 `TA-Encyclopedia` 标记为迁移来源，不再按旧模板新增条目。

### P1 - 数学、采样与信号

- 重构向量矩阵、空间变换、旋转和插值。
- 重构信号频率、采样混叠、噪声和 FFT。
- 补充 Monte Carlo、重要性采样、低差异序列和球谐函数。

### P1 - GPU 与光栅化管线

- 重构 CPU/GPU 提交和图形管线阶段。
- 补充深度模板、Early-Z、Hi-Z、透明和剔除机制。
- 完整整理 MSAA、FXAA、TAA 和时域重建基础。

### P1 - Shader 编程

- 重构 Shader 语言、资源和阶段数据流。
- 补全 Unity Shader 变体收集、剥离和预热机制。
- 重构 Compute Shader 与 GPU 线程执行模型。

### P1 - 光照模型与 PBR

- 重构经典光照、BRDF 和微表面模型。
- 整理 PBR 材质参数、贴图语义和能量关系。
- 补充切线空间、法线贴图和 IBL 预计算流程。

### P1 - 光照、阴影与 GI

- 重构直接光、光源衰减和多光源成本。
- 完整整理 Shadow Map、PCF、PCSS、Bias 和 CSM。
- 整理 Lightmap、Probe、屏幕空间和动态 GI 方案。

### P1 - 纹理技术

- 聚合纹理采样、过滤、Mipmap、寻址和平台压缩格式。
- 重构 UV、图集、纹理流送和虚拟纹理。

### P1 - 颜色管理与后处理

- 重构 sRGB、Linear、Alpha、HDR 和曝光。
- 完整整理 Tone Mapping、Bloom、调色和屏幕空间效果。

### P1 - 引擎渲染与资源架构

- 重构 Forward、Deferred、Tiled 和 Clustered 渲染路径。
- 补全 Command Buffer、Render Graph、Batching 和 GPU Instancing。
- 整理 Unity/Unreal 扩展入口与资源依赖、分包和异步加载。

### P1 - 性能分析与优化

- 重构帧时间、CPU/GPU 瓶颈、同步和 GPU 成本判断。
- 建立 Profiler、RenderDoc、GPU Counter 和单帧分析流程。
- 整理优化验证、性能回归和移动端 Tile-based GPU 实践。

### P2 - 几何与网格

- 重构网格数据、顶点拆分、索引缓存和网格简化机制。
- 整理屏幕占比 LOD、地形分层和材质成本。
- 吸收 Houdini HeightField、HDA 与 PDG 程序化资产流程。

### P2 - 动画系统

- 重构骨骼层级、蒙皮矩阵与 CPU/GPU Skinning。
- 整理状态混合、Root Motion、IK 和 Retargeting。
- 补全动画压缩、面部 Rig、布料和毛发二级运动。

### P2 - VFX 与模拟

- 重构粒子生命周期、CPU/GPU 模拟和 Alive/Dead List 调度。
- 整理 GPU 排序、碰撞、事件与 Niagara/VFX Graph 架构。
- 补全常用 VFX 材质、透明混合、Overdraw 与平台降级。

### P2 - NPR 与风格化渲染

- 重构 Toon Ramp、分层光照、材质区域和风格一致性。
- 补全 Face SDF、头发高光、角色阴影与调试约定。
- 整理模型/屏幕描边、Billboard 假深度、Impostor 和植被风动。

### P2 - 光追与现代渲染

- 重构 Ray 求交、BVH 构建遍历与 BLAS/TLAS 更新。
- 补全实时采样、时空降噪和 ReSTIR Reservoir 复用。
- 整理 GPU-Driven、Meshlet/Mesh Shader、Visibility Buffer 与 Nanite。
