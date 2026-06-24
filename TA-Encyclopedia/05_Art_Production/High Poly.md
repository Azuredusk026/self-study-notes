---
title: "High Poly"
aliases:
  - 高模
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Modeling]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# High Poly

## 定义与解释

High Poly 是高细节模型，通常用于雕刻、展示、烘焙和概念验证，而不是直接进入实时游戏运行时。

## 核心原理

High Poly 的价值在于提供形体、倒角、凹凸、材质细节和高频表面信息。制作完成后，这些细节通常通过 Baking 转移到 Low Poly 的法线、AO、曲率或其他贴图中。

高模可以非常复杂，但需要服务后续低模和烘焙流程。TA 需要约束命名、分件、硬边逻辑、细节尺度和与低模的对应关系，否则高模再精细也难以稳定转化为游戏资产。

## 用途

- 在资产制作和引擎导入中定位与 High Poly 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Low Poly]] | High Poly 追求细节来源；Low Poly 追求运行时可用。 |
| [[Baking]] | High Poly 是源数据；Baking 是转移细节的过程。 |

## 常见误区

1. 把高模直接当游戏模型使用。
2. 高低模分件和命名不匹配导致烘焙错误。
3. 细节尺度过小，贴图分辨率无法承载。

## 相关条目

- [[Low Poly]]：低模承接高模细节并进入运行时。
- [[Baking]]：高模细节通过烘焙转移到贴图。
- [[Retopology]]：重拓扑把高模形体转为可用低模结构。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
