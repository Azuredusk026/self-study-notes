---
title: "HDRP"
aliases:
  - High Definition Render Pipeline
category: "04_Engine"
tags: [技术美术, Unity, Rendering]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# HDRP

## 定义与解释

HDRP 是 Unity 面向高端平台和高质量画面的 Scriptable Render Pipeline，提供更完整的物理光照、后处理、体积和高级渲染特性。

## 核心原理

HDRP 的核心是以可配置但较重的渲染架构组织光照、材质、阴影、体积、后处理和调试视图。它强调 HDR、物理相机、复杂材质模型和高质量管线特性。

TA 需要关注 HDRP Asset、Frame Settings、Volume、Shader Graph Master Stack、材质类型、光照单位和平台性能预算。HDRP 不等于画面自动更好，项目资产规范、灯光标定和性能目标必须同步升级。

## 用途

- 在引擎项目中定位与 HDRP 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[URP]] | HDRP 更重、更高质量；URP 更轻、更跨平台。 |
| [[SRP]] | SRP 是可编程管线框架；HDRP 是官方高端实现。 |

## 常见误区

1. 切换 HDRP 后沿用 Built-in/URP 材质规范。
2. 忽略 HDRP 光照单位和曝光体系。
3. 只看编辑器高画质，不评估目标平台成本。

## 相关条目

- [[SRP]]：HDRP 是 Unity SRP 的具体管线。
- [[URP]]：URP 面向更广平台和轻量需求。
- [[Unity]]：HDRP 属于 Unity 渲染生态。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
