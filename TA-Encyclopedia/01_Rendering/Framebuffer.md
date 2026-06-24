---
title: "Framebuffer"
aliases:
  - 帧缓冲
category: "Rendering"
tags: [技术美术, Rendering, Buffer]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Framebuffer

## 一句话定义

Framebuffer 是一组用于接收渲染输出的颜色、深度和模板附件集合。

## 为什么需要它

GPU 渲染需要明确写到哪里。Framebuffer 把颜色 Render Target、Depth Buffer、Stencil Buffer 组织在一起，让一次渲染阶段可以同时输出颜色并进行深度模板测试。

## 核心原理

- 输入：Render Pass 对附件的配置。
- 处理过程：片元通过深度/模板/混合等测试后写入附件。
- 输出：颜色、深度、模板等缓冲结果。
- 所在层级：图形 API 和引擎渲染资源管理。

## 技术美术中的典型用途

- 理解为什么后处理需要读取上一帧或当前相机颜色。
- 分析 G-Buffer 多 Render Target 写入。
- 排查深度纹理、模板遮罩和颜色格式问题。

## Unity 中的相关场景

Unity 对 Framebuffer 做了较多封装，TA 常通过 RenderTexture、Camera Target、URP Renderer 资源间接接触。

## Unreal Engine 中的相关场景

Unreal 的 Scene Color、Scene Depth、GBuffer 等都是渲染管线中重要的帧缓冲附件或派生资源。

## 常见误区

1. 把 Framebuffer 当成单张颜色图：它通常包含多个附件。
2. 忽略 Depth/Stencil 附件，导致遮挡或模板效果异常。
3. 在移动端创建过多高精度附件。

## 面试可能怎么问

### Framebuffer 和 Render Target 的关系是什么？

回答要点：Render Target 是具体附件或输出纹理，Framebuffer 是这些附件的组合。

## 实践建议

在 RenderDoc 中查看一次 Draw Call 绑定的颜色、深度和模板附件，理解当前 Pass 的输出目标。

## 相关条目

- [[Render Target]]
- [[Depth Buffer]]
- [[Stencil Buffer]]
- [[G-Buffer]]

## 参考来源

- 待补充

