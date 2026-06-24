---
title: "Blend Shape"
aliases:
  - Shape Key
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Animation]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Blend Shape

## 定义与解释

Blend Shape 是通过混合多个目标网格形状来实现表情、口型、肌肉或局部变形的技术。它在不同软件和引擎中也常被称为 Morph Target。

## 核心原理

Blend Shape 的核心是每个目标形状存储相对基础网格的顶点位移，运行时按权重把一个或多个位移叠加到基础网格上。它要求目标网格和基础网格有一致的顶点数量、顺序和拓扑。

Blend Shape 适合精细面部和局部形变，但会增加内存、带宽和变形计算成本。TA 需要控制目标数量、命名、压缩、LOD 继承和与骨骼动画的叠加顺序。

## 用途

- 在资产制作和引擎导入中定位与 Blend Shape 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Skinning]] | Skinning 用骨骼权重驱动顶点；Blend Shape 用目标形状权重驱动顶点。 |
| [[Morph Target]] | 两者在很多引擎中指同一类目标形变机制。 |

## 常见误区

1. 修改基础网格拓扑后目标形状全部失效。
2. 表情目标过多导致内存和计算成本过高。
3. LOD 没同步表情目标，远距离出现形变断层。

## 相关条目

- [[Morph Target]]：Morph Target 与 Blend Shape 是近义实现概念。
- [[Rigging]]：面部 Rig 常结合 Blend Shape。
- [[Skinning]]：Blend Shape 可与骨骼蒙皮叠加。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
