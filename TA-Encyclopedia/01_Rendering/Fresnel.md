---
title: "Fresnel"
aliases: []
category: "01_Rendering"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Fresnel

## 定义与解释

Fresnel 描述表面反射强度随观察角度变化的现象：视线越接近掠射角，反射通常越强。它是 PBR 高光、边缘光、水面、玻璃和风格化材质中的重要机制。

## 核心原理

Fresnel 的核心是反射率不是固定值，而由视线方向和表面法线夹角决定。PBR 中常用 Schlick 近似计算 Fresnel 项，并与 Roughness、Metallic、法线和 BRDF 共同影响高光。

在美术应用中，Fresnel 经常被简化成边缘亮度控制，但物理材质中的 Fresnel 还承担能量分配。TA 需要区分风格化 Fresnel、PBR Fresnel 和引擎材质节点中的近似实现，避免边缘光滥用破坏材质一致性。

## 用途

- 在渲染调试中定位与 Fresnel 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Roughness]] | Roughness 控制高光扩散；Fresnel 控制角度相关反射强度。 |
| [[Lambert]] | Lambert 漫反射不表达镜面 Fresnel 变化。 |

## 常见误区

1. 把 Fresnel 只当作边缘光特效。
2. 在 PBR 材质中随意改 F0，破坏材质可信度。
3. 忽略法线贴图会改变 Fresnel 的局部角度响应。

## 相关条目

- [[BRDF]]：Fresnel 是常见 BRDF 镜面项。
- [[PBR]]：PBR 使用 Fresnel 控制角度相关反射。
- [[Metallic]]：金属和非金属的 Fresnel 颜色语义不同。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
