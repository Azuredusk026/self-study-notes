---
title: "Render Pass"
aliases:
  - 渲染通道
category: "Rendering"
tags: [技术美术, Rendering, Pipeline]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Render Pass

## 定义与解释

Render Pass 是一次具有明确渲染目标、状态和职责的渲染阶段。它可以写入颜色、深度、G-Buffer、阴影图或后处理中间结果，是组织复杂渲染管线的基本单位。

## 核心原理

Render Pass 的核心是定义这一阶段读什么、写什么、何时清理或保留附件，以及和前后阶段的数据依赖。阴影 Pass、Depth Prepass、G-Buffer Pass、Lighting Pass、Transparent Pass 和 Post Process Pass 都是常见例子。

在现代图形 API 和 SRP 中，Pass 组织会影响带宽、同步、Tile Memory、Load/Store 行为和调试可读性。TA 需要从 Frame Debugger 或 RenderDoc 中看懂每个 Pass 的目的，而不是只看最终画面。

## 用途

- 在渲染调试中定位与 Render Pass 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Render Target]] | Render Target 是输出目标；Render Pass 是一次读写目标的阶段。 |
| [[渲染管线]] | 渲染管线由多个 Pass 和状态变化组成。 |

## 常见误区

1. 把 Pass 当成纯 Shader 文件概念，忽略目标和状态。
2. 新增 Pass 时不评估清屏、带宽和排序影响。
3. 调试问题只看材质，不看该材质实际进入了哪些 Pass。

## 相关条目

- [[Render Target]]：Render Pass 通常写入一个或多个 Render Target。
- [[Framebuffer]]：底层附件绑定与 Pass 输出相关。
- [[CommandBuffer]]：命令缓冲可插入或组织 Pass。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
