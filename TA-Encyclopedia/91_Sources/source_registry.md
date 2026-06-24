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

用于登记引用来源，便于回查和更新。涉及具体版本、API 行为、工具节点能力、平台配额或厂商实现时，应优先引用官方文档；如果只登记了入口但还没有完成逐版本结论整理，状态标记为 `source-verified/version-review-needed`。

| ID | 标题 | 类型 | 链接/位置 | 主题 | 可信度 | 记录日期 | 备注 |
|---|---|---|---|---|---|---|---|
| SRC-0001 | Unity Shader Variant 官方文档 | official | https://docs.unity3d.com/Manual/shader-variants.html | Shader Variant | source-verified/version-review-needed | 2026-06-24 | 已校验官方入口；不同 Unity 版本中的 `shader_feature`、`multi_compile`、变体剔除和构建行为仍需按项目版本复核。 |
| SRC-0002 | Unreal Engine Material / Shader Compilation 官方文档 | official | https://dev.epicgames.com/documentation/en-us/unreal-engine/materials-in-unreal-engine | Shader Variant, Precision, Material | source-registered/version-review-needed | 2026-06-24 | 已登记官方文档入口；Material permutation、Static Switch、移动端精度策略需按 Unreal 版本复核。 |
| SRC-0003 | Vulkan Render Pass / Dynamic Rendering 规范 | official | https://registry.khronos.org/vulkan/specs/latest/html/vkspec.html | Render Pass, Vulkan | source-verified/version-review-needed | 2026-06-24 | 已校验 Khronos 最新规范入口；传统 Render Pass、Subpass、Dynamic Rendering 和 Vulkan 版本边界需按项目目标平台复核。 |
| SRC-0004 | AIGC 工具链官方文档入口 | official | https://docs.comfy.org/ | Stable Diffusion, ComfyUI, LoRA, ControlNet | source-verified/version-review-needed | 2026-06-24 | 已校验 ComfyUI 官方文档入口；具体节点、模型和工作流能力更新快，需要按工具版本复核。 |
| SRC-0005 | Unity URP/HDRP/SRP 官方文档 | official | https://docs.unity3d.com/Manual/scriptable-render-pipeline-introduction.html; https://docs.unity3d.com/Manual/urp/render-graph.html; https://docs.unity3d.com/ScriptReference/Rendering.CommandBuffer.html | URP, HDRP, SRP, CommandBuffer, Render Graph | source-verified/version-review-needed | 2026-06-24 | 已校验 SRP、URP Render Graph、CommandBuffer 官方入口；Renderer Feature、RTHandle、Render Graph 推荐用法需按 Unity 版本复核。 |
| SRC-0006 | Unreal Niagara / Custom Depth 官方文档 | official | https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-overview?application_version=5.6; https://dev.epicgames.com/documentation/en-us/unreal-engine/custom-depth-stencil-in-unreal-engine?application_version=5.6 | Niagara, Custom Depth | source-registered/version-review-needed | 2026-06-24 | 已登记 Epic 官方文档入口；Niagara GPU 模拟、数据接口、Custom Depth/Stencil 行为需按 Unreal 版本复核。 |
| SRC-0007 | Git LFS 官方文档 | official | https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage; https://docs.github.com/en/billing/concepts/product-billing/git-lfs | Git LFS | source-verified/version-review-needed | 2026-06-24 | 已校验 GitHub Docs 入口；LFS 单文件限制、存储/带宽计费和平台策略需按实际托管平台复核。 |
| SRC-0008 | Diffusers / IP-Adapter / LoRA 文档 | official | https://huggingface.co/docs/diffusers/main/en/index; https://huggingface.co/docs/diffusers/main/en/api/loaders/lora; https://huggingface.co/docs/diffusers/main/en/using-diffusers/ip_adapter | Diffusion Model, Sampler, LoRA, IP-Adapter | source-verified/version-review-needed | 2026-06-24 | 已校验 Hugging Face Diffusers 文档入口；参数、加载方式、适配器能力需按库版本和模型版本复核。 |
| SRC-0009 | Blender Python API 文档 | official | https://docs.blender.org/api/current/ | Blender Python | source-registered/version-review-needed | 2026-06-24 | 已登记官方文档入口；`bpy` API 和 Add-on 打包方式需按 Blender 版本复核。 |
| SRC-0010 | Unreal Python / Editor Utility Widget 官方文档 | official | https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python?application_version=5.6; https://dev.epicgames.com/documentation/en-us/unreal-engine/editor-utility-widgets-in-unreal-engine?application_version=5.6 | Unreal Python, Editor Utility Widget | source-verified/version-review-needed | 2026-06-24 | 已校验 Editor Utility Widget 官方入口并登记 Python 文档入口；API 覆盖范围和编辑器权限需按 Unreal 版本复核。 |
| SRC-0011 | Perforce Helix Core 官方文档 | official | https://help.perforce.com/helix-core/server-apps/cmdref/current/Content/CmdRef/Home-cmdref.html | Perforce | source-verified/version-review-needed | 2026-06-24 | 已校验 Perforce Helix Core 文档入口；部署、锁文件、权限和流工作流需按团队环境确认。 |
| SRC-0012 | Unity / Unreal 动画系统官方文档 | official | https://docs.unity3d.com/Manual/AnimationSection.html; https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-and-rigging-in-unreal-engine | Root Motion, Additive Animation, Blend Shape, Morph Target | source-registered/version-review-needed | 2026-06-24 | 已登记官方文档入口；导入选项、动画层、曲线和运行时行为需按引擎版本确认。 |
| SRC-0013 | Direct3D 12 官方文档 | official | https://learn.microsoft.com/en-us/windows/win32/direct3d12/directx-12-programming-guide | DirectX, Direct3D 12 | source-verified/version-review-needed | 2026-06-24 | 已校验 Microsoft Learn 入口；具体资源绑定、同步、Root Signature 和平台支持需按目标 Windows/硬件环境复核。 |
| SRC-0014 | Metal 官方文档入口 | official | https://developer.apple.com/metal/ | Metal | source-verified/version-review-needed | 2026-06-24 | 已校验 Apple Developer Metal 入口；具体 API、GPU Family 和平台能力需按 Apple 平台版本复核。 |
