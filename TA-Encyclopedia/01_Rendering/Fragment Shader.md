---
title: "Fragment Shader"
aliases:
  - Pixel Shader
  - 片元着色器
category: "Rendering"
tags: [技术美术, Rendering, Shader]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Fragment Shader

## 定义与解释

Fragment Shader 是 GPU 中为片元计算颜色、材质属性或其他输出的 Shader 阶段。它位于光栅化之后，直接影响最终像素表现和大量片元级性能成本。

## 核心原理

Fragment Shader 接收光栅化插值得到的数据，例如 UV、法线、颜色、屏幕坐标等，然后执行采样、光照、遮罩、分支和输出。它的结果可能写入颜色缓冲、G-Buffer，或被裁剪丢弃。

片元阶段的成本通常随屏幕覆盖面积和 Overdraw 放大。高分辨率贴图采样、复杂分支、循环、法线重建、透明叠加都会让 Fragment Shader 成为瓶颈。TA 在材质规范中需要关注采样次数、精度、关键字变体和移动端限制。

## 用途

- 在渲染调试中定位与 Fragment Shader 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Vertex Shader]] | Vertex Shader 按顶点执行；Fragment Shader 按片元执行。 |
| [[Shader基础]] | Shader基础是总体概念；Fragment Shader 是具体阶段。 |

## 常见误区

1. 只看模型面数，不看屏幕覆盖和片元复杂度。
2. 在移动端过度使用高精度和多纹理采样。
3. 以为分支一定省性能，忽略 GPU 分支执行方式。

## 相关条目

- [[Vertex Shader]]：顶点阶段提供插值前的数据。
- [[Rasterization]]：光栅化产生片元并插值属性。
- [[Overdraw]]：片元重复覆盖会放大片元着色成本。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
