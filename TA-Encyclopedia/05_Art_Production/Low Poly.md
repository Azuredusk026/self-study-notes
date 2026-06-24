---
title: "Low Poly"
aliases:
  - 低模
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Modeling]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Low Poly

## 定义与解释

Low Poly 是面数和复杂度受运行时预算约束的低模资产，通常承接高模烘焙细节并进入引擎使用。

## 核心原理

Low Poly 的核心是在轮廓、变形、UV 和材质需求之间分配有限三角形。它需要保留影响剪影、动画变形和光照的重要结构，把细小表面细节交给 Normal Map、贴图或材质表达。

低模质量取决于拓扑走向、硬边、UV 切分、法线、材质槽和 LOD 计划。TA 需要定义不同资产类型的面数、材质数量和贴图预算，而不是只要求越低越好。

## 用途

- 在资产制作和引擎导入中定位与 Low Poly 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[High Poly]] | High Poly 追求细节；Low Poly 追求实时可用。 |
| [[LOD]] | Low Poly 可以是最终运行模型，也可以是某一级 LOD。 |

## 常见误区

1. 盲目减面导致剪影和动画变形崩坏。
2. 材质槽过多抵消低面数收益。
3. 低模 UV 和硬边规划不当导致烘焙接缝。

## 相关条目

- [[High Poly]]：High Poly 提供细节来源。
- [[Baking]]：低模接收高模烘焙贴图。
- [[Retopology]]：重拓扑常用于生成可用 Low Poly。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
