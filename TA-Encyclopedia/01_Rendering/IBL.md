---
title: "IBL"
aliases:
  - Image Based Lighting
  - 图像基光照
category: "Rendering"
tags: [技术美术, Rendering, PBR, Lighting]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# IBL

## 定义与解释

IBL（Image-Based Lighting）是使用环境贴图或预计算环境数据为材质提供间接光照的技术。它让 PBR 材质在没有大量显式灯光的情况下仍能获得环境反射和漫反射氛围。

## 核心原理

IBL 通常把环境贴图分成漫反射部分和镜面反射部分。漫反射会使用低频卷积结果，镜面反射会根据 Roughness 采样不同模糊级别的预滤波环境贴图，并结合 BRDF LUT 得到近似积分。

IBL 的质量受 HDR 环境、色彩空间、反射探针位置、粗糙度 Mip、曝光和 Tone Mapping 影响。TA 需要检查环境来源是否可信、探针是否覆盖场景、动态物体和室内外过渡是否出现反射不匹配。

## 用途

- 在渲染调试中定位与 IBL 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Light Probe]] | Light Probe 更偏局部间接光采样；IBL 更强调环境贴图驱动的光照。 |
| [[Reflection Probe]] | Reflection Probe 是采集或提供 IBL 反射数据的常见引擎对象。 |

## 常见误区

1. 使用 LDR 或曝光错误的环境贴图导致材质灰暗或过曝。
2. 室内外共用同一反射环境，造成反射不可信。
3. 把 IBL 当作简单贴图反射，忽略 BRDF 和 Roughness 影响。

## 相关条目

- [[PBR]]：IBL 是 PBR 间接光的重要来源。
- [[Reflection Probe]]：Reflection Probe 常提供局部 IBL 数据。
- [[Roughness]]：粗糙度决定镜面 IBL 的模糊级别。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
