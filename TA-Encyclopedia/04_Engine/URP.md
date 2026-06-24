---
title: "URP"
aliases:
  - Universal Render Pipeline
category: "04_Engine"
tags: [技术美术, Unity, Rendering]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# URP

## 一句话定义

URP 是 Unity 面向跨平台实时渲染的 Scriptable Render Pipeline，常用于移动端、主机、PC 和轻量级项目。

## 为什么需要它

TA 关心 URP，不只是因为它是 Unity 常用渲染管线，还因为它决定了 Shader 写法、Renderer Feature 插入点、后处理方式、阴影质量、相机堆叠、资源包体和移动端性能策略。

## 核心原理

URP 把渲染流程拆成可配置的 Renderer、Render Pass、光照和后处理阶段。项目可以通过 Pipeline Asset 控制阴影、HDR、Depth Texture、Opaque Texture、MSAA 等选项，也可以通过自定义 Renderer Feature 注入额外 Pass。

> 待核验：URP 不同 Unity 版本的 Renderer Feature API、Render Graph 支持和内置 Pass 名称可能有差异。

## 技术美术中的典型用途

- 移动端角色和场景渲染。
- 自定义描边、遮挡高亮、屏幕特效。
- Shader Variant 控制和移动端性能优化。
- 与 [[Shader_Graph|Shader Graph]]、[[Render Pass]]、[[RenderTexture]] 配合实现项目效果。

## Unity 中的相关场景

URP 相关工作通常包括配置 Pipeline Asset、Renderer Data、Volume 后处理、Renderer Feature、自定义 Shader 和 Frame Debugger 分析。

## Unreal Engine 中的相关场景

Unreal 没有 URP 对应物，但可以从“项目级渲染管线配置”的角度对比 Unreal 的 Forward/Deferred、Post Process Volume 和材质系统。

## 常见误区

1. 以为 URP 自动等于高性能：错误的阴影、后处理和透明策略仍会很贵。
2. 只调 Shader，不检查 Pipeline Asset 中的 Depth、Opaque、HDR 等开关。
3. 把 Built-in 管线 Shader 直接迁移到 URP，忽略 SRP 宏和光照函数差异。

## 面试可能怎么问

### URP 中 Renderer Feature 可以做什么？

回答要点：它可以向 URP Renderer 注入自定义渲染 Pass，例如描边、角色遮挡、高亮、后处理或自定义 Render Target 处理。

## 实践建议

做一个 URP Renderer Feature：先渲染角色 Mask，再用全屏 Pass 做 Sobel 描边。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Unity]] | Unity 是引擎平台；本条目可能是其中某个系统或工作流。 |
| [[Unreal_Engine]] | Unreal 是引擎平台；本条目可能与其对应系统形成实现差异。 |

## 相关条目

- [[Unity]]
- [[SRP]]
- [[CommandBuffer]]
- [[RenderTexture]]
- [[Shader Variant]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
