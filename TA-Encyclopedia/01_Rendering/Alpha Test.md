---
title: "Alpha Test"
aliases:
  - Alpha Clip
  - 透明裁剪
category: "Rendering"
tags: [技术美术, Rendering, Transparency]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Alpha Test

## 一句话定义

Alpha Test 根据透明度阈值直接保留或丢弃片元，不做半透明混合。

## 为什么需要它

树叶、草、铁丝网、破洞布料等需要轮廓透明，但不一定需要半透明。Alpha Test 可以保留深度写入和相对稳定的遮挡关系，但可能带来锯齿和 Early-Z 限制。

## 核心原理

- 输入：Alpha 值和裁剪阈值。
- 处理过程：Alpha 小于阈值时 discard/clip 片元。
- 输出：保留的片元按不透明方式写颜色和深度。
- 所在层级：Fragment Shader 或固定裁剪逻辑。

## 技术美术中的典型用途

- 植被卡片。
- 破洞、镂空、栅栏。
- Masked 材质和裁剪溶解。
- 需要深度遮挡但不需要半透明的美术资产。

## Unity 中的相关场景

Unity Shader 中常用 `clip(alpha - cutoff)`。URP/HDRP Lit 材质提供 Alpha Clipping 设置。

## Unreal Engine 中的相关场景

Unreal 中 Masked Blend Mode 使用 Opacity Mask，常用于植被和镂空材质。

## 常见误区

1. 以为 Alpha Test 一定比 Alpha Blend 快：大量裁剪和复杂 Shader 仍有成本。
2. 阈值过硬导致边缘闪烁。
3. 忽略 Mipmap 后 Alpha 边缘变化。

## 面试可能怎么问

### Alpha Test 和 Alpha Blend 的区别是什么？

回答要点：Alpha Test 是二值裁剪，通常可写深度；Alpha Blend 是半透明混合，结果依赖绘制顺序。

## 实践建议

制作一张树叶贴图，比较 Alpha Clip、Alpha Blend 和几何叶片的性能与边缘质量。

## 相关条目

- [[Alpha Blend]]
- [[Early-Z]]
- [[Overdraw]]
- [[Texture Sampling]]

## 参考来源

- 待补充

