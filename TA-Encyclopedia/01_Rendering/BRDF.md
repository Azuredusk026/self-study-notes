---
title: "BRDF"
aliases:
  - Bidirectional Reflectance Distribution Function
category: "Rendering"
tags: [技术美术, Rendering, PBR, Lighting]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# BRDF

## 一句话定义

BRDF 描述光从某个入射方向照到表面后，向某个观察方向反射多少能量。

## 为什么需要它

PBR 材质需要可预测地表达漫反射、高光、粗糙度、金属度和菲涅尔。BRDF 是这些计算的数学核心。TA 不一定每天推公式，但需要知道材质参数为什么会影响高光形状、能量守恒和不同光照环境下的观感。

## 核心原理

- 输入：入射光方向、观察方向、法线、粗糙度、金属度、基础颜色等。
- 处理过程：计算漫反射项和镜面反射项，常见微表面模型包含 D、G、F 三部分。
- 输出：某方向上的反射比例。
- 所在层级：Shader 光照模型。

## 技术美术中的典型用途

- 建立 PBR 材质标准。
- 排查高光过亮、塑料感、金属错误。
- 调整角色皮肤、布料、金属和非金属材质表现。
- 解释不同引擎材质观感差异。

## Unity 中的相关场景

Unity Lit Shader 内部使用基于物理的 BRDF。TA 通常通过 Base Color、Metallic、Smoothness/Roughness、Normal 和环境光影响最终结果。

## Unreal Engine 中的相关场景

Unreal 默认材质模型使用 PBR 工作流，Base Color、Metallic、Roughness、Specular 等输入最终进入 BRDF 光照计算。

## 常见误区

1. 认为 BRDF 只是高光公式：它描述更完整的方向性反射。
2. 把 Roughness 当成简单模糊：它会改变微表面法线分布和高光形态。
3. 金属材质仍使用普通漫反射思路。

## 面试可能怎么问

### PBR 中 BRDF 的作用是什么？

回答要点：BRDF 定义材质如何根据光线方向、观察方向和表面属性反射光，是 PBR 光照计算的核心。

## 实践建议

在同一 HDR 环境下对比 Roughness 从 0 到 1 的材质球，观察高光宽度和反射清晰度变化。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[PBR]] | 更偏材质和光照模型；本条目更关注具体渲染环节或画面效果。 |
| [[Shader基础]] | Shader 是实现手段；本条目通常还涉及管线状态、缓冲读写和引擎配置。 |

## 相关条目

- [[PBR]]
- [[Roughness]]
- [[Metallic]]
- [[Fresnel]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
