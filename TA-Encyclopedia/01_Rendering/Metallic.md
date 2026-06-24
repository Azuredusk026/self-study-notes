---
title: "Metallic"
aliases: []
category: "01_Rendering"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Metallic

## 定义与解释

Metallic 是 PBR 工作流中描述表面是否具有金属反射特性的参数。它通常在金属和非金属之间切换材质能量分配，而不是简单控制亮度。

## 核心原理

Metallic 的机制是改变 Base Color 的语义和反射能量分配。非金属的 Base Color 主要代表漫反射颜色，镜面 F0 通常较低且接近无色；金属的 Base Color 更多参与有色镜面反射，漫反射部分接近消失。

实际资产制作中，Metallic 通常应接近 0 或 1，过多灰值需要有明确材质依据，例如脏污、氧化、混合材质或压缩过渡。TA 需要检查通道打包、色彩空间、遮罩边缘和 Roughness 的配合。

## 用途

- 在渲染调试中定位与 Metallic 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Roughness]] | Metallic 改变材质类别和能量分配；Roughness 改变微表面高光扩散。 |
| [[PBR]] | PBR 定义 Base Color、Metallic、Roughness 等参数的整体语义。 |

## 常见误区

1. 把 Metallic 当作让材质变亮的滑杆。
2. 金属贴图使用 sRGB 导致阈值不准。
3. 在单一材质上大量使用中间灰金属度而没有物理或美术依据。

## 相关条目

- [[PBR]]：Metallic 是 PBR 材质关键参数。
- [[Roughness]]：Roughness 与 Metallic 共同决定高光形态。
- [[Fresnel]]：金属的 Fresnel 颜色和非金属不同。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
