---
title: "Skinning"
aliases:
  - 蒙皮
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Rigging]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Skinning

## 定义与解释

Skinning 是把网格顶点绑定到骨骼，并根据骨骼变换和权重驱动顶点变形的技术。

## 核心原理

Skinning 的核心是每个顶点拥有若干骨骼权重，运行时根据骨骼矩阵混合计算新位置和法线。常见线性混合蒙皮简单高效，但在关节弯曲处可能产生体积塌陷。

TA 需要关注权重数量、骨骼数量、规范化、关节边流、扭转骨、辅助骨和平台限制。权重质量不是只看 DCC 中变形顺滑，还要看引擎导入、压缩、LOD 和动画叠加后的表现。

## 用途

- 在资产制作和引擎导入中定位与 Skinning 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Rigging]] | Rigging 建立骨架和控制器；Skinning 建立网格到骨骼的权重关系。 |
| [[Blend Shape]] | Skinning 由骨骼驱动；Blend Shape 由目标形状驱动。 |

## 常见误区

1. 权重没有归一化或影响骨骼过多。
2. 关节拓扑不支持变形，权重再好也会塌陷。
3. LOD 删除骨骼后没有检查蒙皮结果。

## 相关条目

- [[Rigging]]：Skinning 依赖 Rig 骨架。
- [[角色绑定]]：角色绑定规范包含蒙皮要求。
- [[LOD]]：角色 LOD 需要处理骨骼和权重简化。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
