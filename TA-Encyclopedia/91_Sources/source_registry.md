---
title: "Source Registry"
aliases: []
category: "Sources"
tags: [sources, registry]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Source Registry

用于登记引用来源，便于回查和更新。当前环境未联网查证时，不虚构链接；涉及具体版本或厂商实现的内容统一标记为 `todo-verify`。

| ID | 标题 | 类型 | 链接/位置 | 主题 | 可信度 | 记录日期 | 备注 |
|---|---|---|---|---|---|---|---|
| SRC-0001 | Unity Shader Variant 官方文档 | official | 待补充 | Shader Variant | todo-verify | 2026-06-24 | 需要查证 Unity 不同版本中 `shader_feature`、`multi_compile` 和变体剔除行为。 |
| SRC-0002 | Unreal Engine Material Permutation / Shader Compilation 官方文档 | official | 待补充 | Shader Variant, Precision | todo-verify | 2026-06-24 | 需要查证 Unreal 不同版本中材质 permutation、静态开关和移动端精度策略。 |
| SRC-0003 | Vulkan Render Pass / Dynamic Rendering 规范 | official | 待补充 | Render Pass, Vulkan | todo-verify | 2026-06-24 | 需要查证传统 Render Pass、Subpass 与 Dynamic Rendering 的版本边界。 |
| SRC-0004 | AIGC 工具链官方文档 | official | 待补充 | Stable Diffusion, ComfyUI, LoRA, ControlNet | todo-verify | 2026-06-24 | AIGC 工具和模型能力更新快，具体版本能力需要后续联网核验。 |
| SRC-0005 | Unity URP/HDRP/SRP 官方文档 | official | 待补充 | URP, HDRP, SRP, CommandBuffer | todo-verify | 2026-06-24 | 需要按 Unity 版本查证 Render Graph、Renderer Feature、RTHandle 和 CommandBuffer 推荐用法。 |
| SRC-0006 | Unreal Niagara / Custom Depth 官方文档 | official | 待补充 | Niagara, Custom Depth | todo-verify | 2026-06-24 | 需要按 Unreal 版本查证 Niagara GPU 模拟、数据接口和 Custom Depth/Stencil 行为。 |
| SRC-0007 | Git LFS 托管平台文档 | official | 待补充 | Git LFS | todo-verify | 2026-06-24 | LFS 配额、锁文件和计费策略依 GitHub/GitLab/Perforce Helix 等平台不同。 |
| SRC-0008 | Stable Diffusion / ComfyUI / IP-Adapter 项目文档 | official | 待补充 | Diffusion Model, Sampler, CFG Scale, Img2Img, Inpainting, IP-Adapter | todo-verify | 2026-06-24 | 具体参数、节点和模型适配关系需要按工具版本核验。 |
| SRC-0009 | Blender Python API 文档 | official | 待补充 | Blender Python | todo-verify | 2026-06-24 | 需要按 Blender 版本核验 `bpy` API 和 Add-on 打包方式。 |
| SRC-0010 | Unreal Python / Editor Utility Widget 官方文档 | official | 待补充 | Unreal Python, Editor Utility Widget | todo-verify | 2026-06-24 | 需要按 Unreal 版本核验 API 覆盖范围和编辑器工具权限。 |
| SRC-0011 | Perforce Helix Core 官方文档 | official | 待补充 | Perforce | todo-verify | 2026-06-24 | 部署、锁文件、权限和流工作流需要按团队环境确认。 |
| SRC-0012 | Unity / Unreal 动画系统官方文档 | official | 待补充 | Root Motion, Additive Animation, Blend Shape, Morph Target | todo-verify | 2026-06-24 | 具体导入选项、动画层和曲线行为需要按引擎版本确认。 |
