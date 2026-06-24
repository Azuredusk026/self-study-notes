---
title: "Render Target"
aliases:
  - 渲染目标
category: "Rendering"
tags: [技术美术, Rendering, Buffer]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Render Target

## 一句话定义

Render Target 是渲染结果写入的纹理或缓冲。

## 为什么需要它

除了最终屏幕，很多效果需要把中间结果写入纹理，例如 Shadow Map、G-Buffer、后处理颜色、角色遮罩、反射纹理和小地图。TA 需要理解 Render Target 的格式、分辨率、生命周期和带宽成本。

## 核心原理

- 输入：Draw Call 或全屏 Pass。
- 处理过程：GPU 将 Shader 输出写入指定颜色、深度或模板附件。
- 输出：可被后续 Pass 读取的纹理或缓冲。
- 所在层级：GPU 资源和引擎渲染系统。

## 技术美术中的典型用途

- 自定义后处理和描边。
- UI 或小地图相机渲染。
- 角色遮挡、深度纹理、法线纹理。
- 优化中间纹理分辨率和格式。

## Unity 中的相关场景

Unity 中常用 RenderTexture、Camera Target Texture、URP RTHandle。TA 需要注意格式、MSAA、Depth Buffer、是否启用 sRGB。

## Unreal Engine 中的相关场景

Unreal 中 Render Target 资源常用于 Scene Capture、材质采样、绘制到纹理、后处理和 Niagara 数据交互。

## 常见误区

1. 认为 Render Target 免费：高分辨率 HDR Render Target 带宽和显存压力明显。
2. 忘记颜色空间和格式，导致颜色偏差。
3. 用全分辨率处理不需要高精度的遮罩。

## 面试可能怎么问

### Render Target 和普通 Texture 的区别是什么？

回答要点：Render Target 可以作为 GPU 渲染输出目标，普通 Texture 更多作为采样输入；同一资源在不同阶段也可能切换用途。

## 实践建议

创建一个半分辨率 Render Target 做模糊，再与原图合成，观察性能和画质差异。

## 相关条目

- [[Framebuffer]]
- [[Render Pass]]
- [[后处理]]
- [[G-Buffer]]

## 参考来源

- 待补充

