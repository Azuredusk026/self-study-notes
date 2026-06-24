---
title: "Render Pass"
aliases:
  - 渲染通道
category: "Rendering"
tags: [技术美术, Rendering, Pipeline]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Render Pass

## 一句话定义

Render Pass 是一次有明确输入、输出和渲染目标的绘制阶段。

## 为什么需要它

复杂画面不是一次绘制完成的。阴影、深度预通道、G-Buffer、透明、后处理、UI 都可能拆成不同 Render Pass。TA 在自定义渲染管线、后处理、Render Feature、材质调试和性能分析中需要看懂每个 Pass 的目的。

## 核心原理

- 输入：场景对象、材质、纹理、深度、上一阶段输出。
- 处理过程：设置 Render Target、Depth/Stencil 状态、Shader Pass、Draw Call。
- 输出：颜色缓冲、深度缓冲、G-Buffer、Shadow Map 或中间纹理。
- 所在层级：引擎渲染调度和图形 API 抽象。

## 技术美术中的典型用途

- 添加描边、Bloom、角色遮挡高亮等自定义效果。
- 分析 Frame Debugger 中每一步渲染成本。
- 管理 RenderTexture 和中间缓冲生命周期。
- 判断一个效果应该插入在 Opaque、Transparent 还是 PostProcess 阶段。

## Unity 中的相关场景

URP 中常见 ScriptableRenderPass、Renderer Feature、DepthOnly Pass、ShadowCaster Pass。ShaderLab 的 Pass 也表示材质在某个渲染阶段使用的程序和状态。

## Unreal Engine 中的相关场景

Unreal 的 Base Pass、Shadow Pass、Post Processing、Custom Depth 都可视为渲染阶段。材质域和渲染管线决定一个材质参与哪些 Pass。

## 常见误区

1. 把 Shader Pass 和图形 API Render Pass 完全等同：它们层级不同。
2. 只看最终画面，不看中间缓冲，导致问题定位困难。
3. 添加全屏 Pass 时忽略带宽和移动端成本。

## 面试可能怎么问

### 为什么后处理通常需要额外 Render Pass？

回答要点：后处理需要读取已经渲染好的颜色、深度或法线缓冲，再输出到新的目标或最终屏幕。

## 实践建议

用 Unity URP 写一个 Renderer Feature，将场景颜色复制到临时 RenderTexture 后做一次 Sobel 描边。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[PBR]] | 更偏材质和光照模型；本条目更关注具体渲染环节或画面效果。 |
| [[Shader基础]] | Shader 是实现手段；本条目通常还涉及管线状态、缓冲读写和引擎配置。 |

## 相关条目

- [[后处理]]
- [[G-Buffer]]
- [[Render Target]]
- [[Vulkan]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
