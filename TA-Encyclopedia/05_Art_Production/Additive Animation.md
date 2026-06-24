---
title: "Additive Animation"
aliases:
  - 叠加动画
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Animation]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Additive Animation

## 定义与解释

Additive Animation 是把一段动画作为增量叠加到基础姿势或基础动画上的动画技术。它常用于呼吸、受击、瞄准偏移、表情、上半身叠加和细节动作。

## 核心原理

Additive Animation 的关键是动画数据不直接表示最终姿势，而是表示相对参考姿势的差值。运行时先播放基础动画，再把增量按权重叠加到指定骨骼或通道上。

它依赖稳定的参考姿势、骨骼层级和混合空间。参考姿势不一致会导致漂移或姿态爆炸；叠加范围没有 Mask 会污染不该动的骨骼。TA 需要和动画师约定导出姿势、层级遮罩、权重范围和引擎中的 Additive 类型。

## 用途

- 在资产制作和引擎导入中定位与 Additive Animation 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Root Motion]] | Root Motion 处理整体位移；Additive Animation 处理姿势增量。 |
| [[Blend Shape]] | Blend Shape 叠加几何形变；Additive Animation 叠加骨骼姿势。 |

## 常见误区

1. 参考姿势不一致导致叠加结果偏移。
2. 没有骨骼 Mask，局部动作污染全身。
3. 把 Root 位移也作为普通姿势增量叠加。

## 相关条目

- [[动画技术]]：Additive Animation 是动画混合技术之一。
- [[Rigging]]：稳定骨架和参考姿势是叠加动画基础。
- [[Root Motion]]：Root 位移通常不应被随意叠加。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
