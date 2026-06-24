---
title: "Lambert"
aliases: []
category: "01_Rendering"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Lambert

## 定义与解释

Lambert 是一种理想漫反射模型，假设表面向各方向均匀散射入射光。它常用于解释 NdotL 漫反射、基础光照和非金属材质的低频光照部分。

## 核心原理

Lambert 漫反射的核心是亮度与表面法线和光照方向夹角的余弦成正比。表面朝向光源时更亮，掠射或背光时更暗，公式简单稳定。

它不描述镜面反射、粗糙度变化、能量复杂分布或次表面散射。在现代 PBR 中，Lambert 或其变体常只是漫反射项的一部分。TA 需要知道它适合作为基础模型，而不是完整材质模型。

## 用途

- 在渲染调试中定位与 Lambert 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[BRDF]] | BRDF 是通用反射函数；Lambert 是其中非常简单的漫反射模型。 |
| [[Fresnel]] | Fresnel 描述角度相关镜面反射；Lambert 只描述理想漫反射。 |

## 常见误区

1. 把 Lambert 当作完整真实材质模型。
2. 忘记 NdotL 需要在正确空间中计算并归一化。
3. 在风格化项目中照搬 Lambert，导致明暗设计不可控。

## 相关条目

- [[BRDF]]：Lambert 可以看作一种简单漫反射 BRDF。
- [[PBR]]：PBR 中的漫反射部分可能使用 Lambert 或改进模型。
- [[Toon_Shading]]：Toon 常对 NdotL 做阶梯化处理。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
