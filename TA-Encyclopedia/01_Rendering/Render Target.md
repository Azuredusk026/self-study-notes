---
title: "Render Target"
aliases:
  - 渲染目标
category: "Rendering"
tags: [技术美术, Rendering, Buffer]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Render Target

## 定义与解释

Render Target 是 GPU 可以写入的渲染目标，通常是纹理或缓冲。它用于离屏渲染、后处理、阴影、G-Buffer、反射和各种中间结果。

## 核心原理

Render Target 的机制是把某张纹理或缓冲绑定为当前颜色输出，让 Shader 或固定功能阶段把结果写进去。后续 Pass 可以再把它作为纹理读取，实现多阶段图像处理。

Render Target 的成本由分辨率、格式、数量、MSAA、读写次数和生命周期决定。TA 在做后处理或工具效果时需要确认 RT 格式是否支持 HDR、是否需要深度、是否会造成额外拷贝，以及移动端带宽是否可接受。

## 用途

- 在渲染调试中定位与 Render Target 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Texture Sampling]] | Render Target 写入后常作为纹理采样；采样和写入是不同阶段。 |
| [[Depth Buffer]] | Depth Buffer 记录深度；Render Target 多指颜色或通用输出纹理。 |

## 常见误区

1. 随意使用全分辨率 HDR RT，忽略带宽和显存。
2. 读写同一 RT 时不理解管线限制或隐式拷贝。
3. 格式选择错误导致颜色截断、精度不足或平台不支持。

## 相关条目

- [[Framebuffer]]：Render Target 常作为 Framebuffer 的颜色附件。
- [[Render Pass]]：Render Pass 定义 Render Target 的读写阶段。
- [[G-Buffer]]：G-Buffer 由多个语义 Render Target 组成。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
