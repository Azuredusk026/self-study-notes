---
title: "Rasterization"
aliases:
  - 光栅化
category: "Rendering"
tags: [技术美术, Rendering, GPU]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Rasterization

## 定义与解释

Rasterization 是把几何图元转换成屏幕片元的过程，是传统实时渲染管线中连接顶点处理和片元着色的关键阶段。

## 核心原理

光栅化会根据投影后的三角形覆盖范围生成片元，并对顶点属性进行插值，例如 UV、颜色、法线或自定义数据。随后片元进入 Fragment Shader、深度/模板测试和混合等阶段。

它的细节会影响边缘规则、插值精度、透视校正、MSAA 和屏幕空间效果。TA 需要理解为什么同一个模型在不同分辨率、抗锯齿或投影设置下边缘、UV 和深度表现会变化。

## 用途

- 在渲染调试中定位与 Rasterization 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[渲染管线]] | Rasterization 是管线中的一个阶段；渲染管线包含更完整的提交、着色和输出流程。 |
| [[Raycast]] | Raycast 是射线查询；Rasterization 是屏幕覆盖转换。 |

## 常见误区

1. 以为光栅化直接产生最终像素颜色。
2. 忽略透视校正插值对 UV 和深度的影响。
3. 把模型锯齿问题全部归因于贴图或后处理。

## 相关条目

- [[Vertex Shader]]：顶点阶段输出供光栅化插值的数据。
- [[Fragment Shader]]：光栅化产生片元后进入片元着色。
- [[Z-Test]]：片元生成后通常会进行深度测试。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
