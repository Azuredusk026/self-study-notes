---
title: "SRP Batcher"
aliases: []
category: "04_Engine"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# SRP Batcher

## 定义与解释

SRP Batcher 是 Unity SRP 中减少材质常量绑定和 CPU 渲染提交开销的优化机制。

## 核心原理

SRP Batcher 的核心是要求 Shader 常量缓冲布局稳定，让不同材质在同一 Shader Variant 下能快速切换参数。它优化的是 CPU 设置渲染状态和上传常量的路径，不是减少所有 Draw Call。

TA 需要检查 Shader 是否兼容 SRP Batcher、材质是否使用相同 Variant、MaterialPropertyBlock 是否影响路径、以及项目瓶颈是否真的在 CPU 渲染提交。它和 GPU Instancing、动态合批不是同一类优化。

## 用途

- 在引擎项目中定位与 SRP Batcher 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[GPU Instancing]] | GPU Instancing 合并实例绘制；SRP Batcher 优化 SRP 材质常量绑定。 |
| [[Draw Call]] | SRP Batcher 不一定减少 Draw Call 数量，而是降低提交成本。 |

## 常见误区

1. 把 SRP Batcher 当成减少 Draw Call 的万能开关。
2. Shader 常量缓冲布局不兼容却期待生效。
3. 没有用 Profiler 验证瓶颈是否在 CPU Render Loop。

## 相关条目

- [[SRP]]：SRP Batcher 依赖 SRP 渲染框架。
- [[MaterialPropertyBlock]]：MPB 可能影响批处理路径。
- [[GPU Instancing]]：Instancing 是另一类批处理优化。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
