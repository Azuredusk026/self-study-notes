---
title: "Alpha Blend"
aliases:
  - 透明混合
category: "Rendering"
tags: [技术美术, Rendering, Transparency]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Alpha Blend

## 一句话定义

Alpha Blend 是根据源颜色、目标颜色和透明度把当前片元与已有画面混合的过程。

## 为什么需要它

玻璃、水、烟雾、UI、粒子和许多 VFX 都需要半透明。TA 需要理解混合公式、排序、深度写入和 Overdraw，否则容易出现穿插、发黑、叠加异常或性能过高。

## 核心原理

- 输入：源颜色、目标颜色、Alpha、Blend Factor。
- 处理过程：按混合状态组合颜色，例如 SrcAlpha / OneMinusSrcAlpha。
- 输出：写回颜色缓冲的混合结果。
- 所在层级：片元输出后的固定功能混合阶段。

## 技术美术中的典型用途

- 粒子、烟雾、火焰和魔法特效。
- UI 半透明和叠加。
- 玻璃、水面、能量罩。
- Additive、Multiply、Premultiplied Alpha 等模式选择。

## Unity 中的相关场景

ShaderLab 中通过 `Blend`、`ZWrite`、`Queue` 控制透明材质。URP/HDRP 的 Transparent 队列通常需要排序和额外 Pass。

## Unreal Engine 中的相关场景

Unreal 材质 Blend Mode 包括 Translucent、Additive、Masked 等。Translucency Sorting 和 Separate Translucency 会影响效果和成本。

## 常见误区

1. 认为透明只改 Alpha 就够：还要处理排序、深度和混合模式。
2. 忽略 Premultiplied Alpha 和 Straight Alpha 的贴图差异。
3. 透明物体期待像不透明物体一样稳定写入深度。

## 面试可能怎么问

### Alpha Blend 为什么会有排序问题？

回答要点：混合依赖已有目标颜色，绘制顺序会影响结果；透明物体通常需要从远到近排序，但复杂交叉几何很难完全正确。

## 实践建议

用两块交叉半透明面片测试不同排序和 ZWrite 设置，记录画面差异。

## 相关条目

- [[Alpha Test]]
- [[Overdraw]]
- [[Z-Test]]
- [[Forward_Rendering]]

## 参考来源

- 待补充

