---
title: "BRDF"
aliases:
  - Bidirectional Reflectance Distribution Function
category: "Rendering"
tags: [技术美术, Rendering, PBR, Lighting]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---



# BRDF

## 定义与解释

BRDF（Bidirectional Reflectance Distribution Function）描述光从某个方向照到表面后，沿另一个方向反射出去的分布规律。它是 PBR 光照模型中连接材质参数、入射光和观察方向的核心函数。

## 核心原理

BRDF 的核心是能量如何在漫反射和镜面反射之间分配。实时 PBR 常用微表面模型：表面被看作大量微小镜面，法线分布、几何遮蔽和 Fresnel 共同决定高光形状和强度。

在工程实现中，BRDF 不只是一个公式，还涉及法线空间、粗糙度映射、金属度工作流、IBL 积分近似和 LUT。不同引擎的参数命名和压缩方式可能不同，但必须保持能量守恒、颜色空间和贴图语义一致。

## 用途

- 在渲染调试中定位与 BRDF 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Lambert]] | Lambert 是简单漫反射模型；BRDF 可以包含更完整的漫反射和镜面反射项。 |
| [[IBL]] | IBL 提供环境光来源；BRDF 决定材质如何响应这些光。 |

## 常见误区

1. 把 BRDF 等同于某一个固定公式，忽略引擎实现和近似差异。
2. 只调 Base Color，不检查 Roughness、Metallic、Fresnel 对能量分配的影响。
3. 忽略颜色空间错误导致的光照不守恒。

## 相关条目

- [[PBR]]：PBR 使用 BRDF 组织材质和光照交互。
- [[Fresnel]]：Fresnel 通常是 BRDF 镜面项的重要部分。
- [[Roughness]]：粗糙度控制微表面分布和高光宽度。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
