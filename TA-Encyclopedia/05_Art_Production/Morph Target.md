---
title: "Morph Target"
aliases:
  - 变形目标
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Unreal, Animation]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Morph Target

## 定义与解释

Morph Target 是通过目标形状权重驱动网格顶点位移的变形机制，常用于面部表情、口型、肌肉和局部形变。

## 核心原理

Morph Target 要求基础网格和目标网格拥有一致顶点数量和顺序。运行时根据权重混合多个目标位移，再与骨骼蒙皮等变形阶段组合。

它和 Blend Shape 在很多工具和引擎中是同类概念。TA 需要关注目标数量、压缩、LOD、导出命名、运行时权重控制和与骨骼动画的叠加顺序，避免表情资产在引擎中丢失或成本过高。

## 用途

- 在资产制作和引擎导入中定位与 Morph Target 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Blend Shape]] | 两者多为同类机制在不同软件或引擎中的命名。 |
| [[Skinning]] | Skinning 用骨骼变形；Morph Target 用目标形状变形。 |

## 常见误区

1. 目标网格顶点顺序被修改导致形变损坏。
2. 目标数量过多导致内存和运行时成本上升。
3. 导出设置没启用 Morph Target。

## 相关条目

- [[Blend Shape]]：Blend Shape 与 Morph Target 是近义概念。
- [[Skinning]]：Morph Target 常与骨骼蒙皮叠加。
- [[Rigging]]：面部 Rig 常驱动 Morph Target。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
