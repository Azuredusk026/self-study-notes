---
title: "RenderTexture"
aliases:
  - Render Texture
category: "04_Engine"
tags: [技术美术, Unity, Rendering]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# RenderTexture

## 定义与解释

RenderTexture 是 Unity 中可作为渲染目标的纹理资源，用于相机输出、后处理、中间缓冲、反射、UI 显示和离屏渲染。

## 核心原理

RenderTexture 的核心是让渲染结果写入纹理，而不是直接写到屏幕。相机、CommandBuffer、Blit 或自定义 Pass 可以把颜色和深度写入 RT，后续材质再采样它。

TA 需要关注分辨率、格式、深度缓冲、MSAA、HDR、生命周期和释放。临时 RT 过多会造成显存和带宽压力，格式选择错误会导致颜色截断、精度不足或平台不兼容。

## 用途

- 在引擎项目中定位与 RenderTexture 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Unreal_Render_Target]] | 两者都是引擎中的渲染目标资源，但 API 和编辑器工作流不同。 |
| [[Texture Sampling]] | RenderTexture 写入后常作为纹理采样。 |

## 常见误区

1. 使用全分辨率 HDR RT 而不评估带宽。
2. 临时 RenderTexture 未释放。
3. 深度、MSAA 或颜色格式设置与效果需求不匹配。

## 相关条目

- [[Render Target]]：RenderTexture 是 Unity 中的 Render Target 形式。
- [[CommandBuffer]]：CommandBuffer 常读写 RenderTexture。
- [[后处理]]：后处理通常依赖中间 RenderTexture。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
