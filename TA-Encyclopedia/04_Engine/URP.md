---
title: "URP"
aliases:
  - Universal Render Pipeline
category: "04_Engine"
tags: [技术美术, Unity, Rendering]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# URP

## 定义与解释

URP 是 Unity 面向跨平台和可扩展项目的通用渲染管线，强调性能、可配置和移动端友好。

## 核心原理

URP 基于 SRP 构建，通过 Pipeline Asset、Renderer Data、Renderer Feature、Shader Library 和 Volume 组织光照、阴影、后处理和自定义 Pass。它比 Built-in 更可控，比 HDRP 更轻量。

TA 需要关注 URP Asset 设置、Renderer Feature、Forward/Deferred 路径、Depth/Opaque Texture、Shader Graph、Light Mode Pass 和平台质量分级。许多效果是否可用，取决于管线设置和 Renderer 配置，而不只是 Shader 代码。

## 用途

- 在引擎项目中定位与 URP 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[HDRP]] | URP 更轻量跨平台；HDRP 更高端但更重。 |
| [[SRP]] | SRP 是框架；URP 是具体实现。 |

## 常见误区

1. 从 Built-in 迁移后不更新 Shader 和材质。
2. 效果依赖 Depth/Opaque Texture 但管线未启用。
3. Renderer Feature 插入时机不对导致缓冲不可用。

## 相关条目

- [[SRP]]：URP 是 SRP 的官方实现。
- [[ScriptableRendererFeature]]：URP 通过 Renderer Feature 扩展。
- [[HDRP]]：HDRP 是另一条官方 SRP 管线。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
