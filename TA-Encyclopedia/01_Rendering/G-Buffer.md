---
title: "G-Buffer"
aliases: []
category: "01_Rendering"
confidence: medium
tags: [rendering, deferred, g-buffer]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# G-Buffer

## 定义与解释

G-Buffer 是 Deferred Rendering 中用于保存可见表面几何和材质属性的一组屏幕空间缓冲。它不是某一张固定纹理，而是随引擎管线和材质模型变化的数据布局。

## 常见内容

- Base Color
- Normal
- Roughness/Metallic
- Depth
- Emission

## 核心原理

G-Buffer 的机制是把不透明几何的关键属性先写入多个 Render Target，例如深度、法线、Base Color、Roughness、Metallic、AO、Emission 或引擎自定义数据。后续光照和屏幕空间效果通过读取这些缓冲重建每个像素的材质状态。

G-Buffer 的设计是带宽、精度和材质表达能力的取舍。通道越多，自定义数据越灵活，但显存、带宽和平台压力越大；压缩或打包过度又会带来精度问题。TA 需要会看 Buffer Visualization，并知道哪些效果依赖哪些通道。

## 用途

- 在渲染调试中定位与 G-Buffer 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Framebuffer]] | Framebuffer 是附件绑定集合；G-Buffer 是延迟渲染写入的一组语义缓冲。 |
| [[Depth Buffer]] | Depth Buffer 是深度附件；G-Buffer 还包含法线和材质属性。 |

## 常见误区

1. 认为所有引擎的 G-Buffer 通道都一样。
2. 在 G-Buffer 中加入过多自定义数据而不评估带宽。
3. 调试后处理时不检查其依赖的 G-Buffer 通道是否可用。

## 相关条目

- [[Deferred_Rendering]]：G-Buffer 是延迟渲染的核心数据载体。
- [[Render Target]]：G-Buffer 通常由多张 Render Target 组成。
- [[PBR]]：G-Buffer 常存储 PBR 材质参数。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
