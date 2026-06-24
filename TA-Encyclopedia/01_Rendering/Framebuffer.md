---
title: "Framebuffer"
aliases:
  - 帧缓冲
category: "Rendering"
tags: [技术美术, Rendering, Buffer]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Framebuffer

## 定义与解释

Framebuffer 是 GPU 渲染时绑定的一组输出附件，可以包含颜色、深度、模板等缓冲。它定义了当前 Pass 的写入目标，是屏幕渲染和离屏渲染的底层组织方式。

## 核心原理

Framebuffer 本身不是某张纹理，而是一组附件绑定关系。渲染命令执行时，片元输出会写入当前绑定的颜色附件，深度和模板测试会访问对应附件。

现代引擎通常把 Framebuffer 概念封装在 Render Target、RenderTexture、Render Pass 或平台图形 API 对象中。TA 不一定直接创建 Framebuffer，但需要理解为什么某个 Pass 写到屏幕、某个 Pass 写到中间纹理，以及附件格式、清屏、Load/Store 行为如何影响性能和结果。

## 用途

- 在渲染调试中定位与 Framebuffer 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Render Target]] | Render Target 是可写颜色目标；Framebuffer 是附件集合和绑定状态。 |
| [[Render Pass]] | Render Pass 描述一次或一组附件读写；Framebuffer 提供实际附件。 |

## 常见误区

1. 把 Framebuffer 误解成唯一的屏幕缓冲。
2. 忽略附件格式和清屏策略对带宽的影响。
3. 在多 Pass 调试时搞不清当前 Pass 写入哪个目标。

## 相关条目

- [[Render Target]]：Render Target 常作为 Framebuffer 的颜色附件。
- [[Depth Buffer]]：Depth Buffer 可作为 Framebuffer 的深度附件。
- [[Render Pass]]：Render Pass 描述对这些附件的读写生命周期。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
