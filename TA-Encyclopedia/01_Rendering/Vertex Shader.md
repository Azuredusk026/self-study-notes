---
title: "Vertex Shader"
aliases:
  - 顶点着色器
category: "Rendering"
tags: [技术美术, Rendering, Shader]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Vertex Shader

## 定义与解释

Vertex Shader 是 GPU 中按顶点执行的 Shader 阶段，负责顶点位置变换和向后续阶段输出可插值属性。它连接模型数据和裁剪空间，是渲染管线早期的重要阶段。

## 核心原理

Vertex Shader 通常把对象空间顶点变换到裁剪空间，并输出 UV、法线、切线、颜色、自定义数据等。随后光栅化会根据三角形覆盖区域插值这些属性，供 Fragment Shader 使用。

顶点阶段适合做顶点动画、风吹草动、GPU Skinning 的部分逻辑或实例化数据处理，但它按顶点而非按像素执行，细节受网格密度限制。TA 需要理解空间变换、法线变换和插值误差，避免把片元级效果错误放到顶点阶段。

## 用途

- 在渲染调试中定位与 Vertex Shader 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Fragment Shader]] | Vertex Shader 按顶点执行；Fragment Shader 按片元执行。 |
| [[Object Space]] | Object Space 是输入空间之一；Vertex Shader 负责把它转换到后续空间。 |

## 常见误区

1. 以为顶点阶段可以表达任意像素细节。
2. 法线变换没有使用正确矩阵，导致光照错误。
3. 顶点动画改变位置但没有同步包围盒，导致剔除异常。

## 相关条目

- [[Fragment Shader]]：片元阶段使用顶点阶段输出的插值数据。
- [[Rasterization]]：光栅化插值 Vertex Shader 输出。
- [[矩阵变换]]：顶点空间变换依赖矩阵。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
