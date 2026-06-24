---
title: "SRP"
aliases:
  - Scriptable Render Pipeline
category: "04_Engine"
tags: [技术美术, Unity, Rendering]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# SRP

## 定义与解释

SRP（Scriptable Render Pipeline）是 Unity 的可编程渲染管线框架，让渲染流程由 C# 管线资产和渲染器代码组织。

## 核心原理

SRP 的核心是把原本固定的内置渲染流程开放给管线实现。URP、HDRP 和自定义管线通过 Render Pipeline Asset、Renderer、Pass、Shader Library 和资源配置定义渲染顺序、光照、后处理和平台策略。

TA 需要理解项目使用哪条 SRP、哪些 Shader 和材质兼容、哪些 Renderer Feature 生效、哪些管线设置影响资产。SRP 提供扩展能力，也带来版本升级和管线差异成本。

## 用途

- 在引擎项目中定位与 SRP 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[URP]] | URP 是具体管线；SRP 是框架。 |
| [[HDRP]] | HDRP 也是 SRP 实现，但目标平台和特性不同。 |

## 常见误区

1. 以为 SRP 是单一渲染管线。
2. 升级管线版本前不检查 Shader 和 Renderer Feature 兼容性。
3. 把 Built-in 管线经验直接套到 URP/HDRP。

## 相关条目

- [[URP]]：URP 是 Unity 官方 SRP 实现。
- [[HDRP]]：HDRP 是高端 SRP 实现。
- [[ScriptableRendererFeature]]：URP 使用 Renderer Feature 扩展 SRP 流程。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
