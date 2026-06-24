---
title: "Bloom"
aliases:
  - 泛光
category: "Rendering"
tags: [技术美术, Rendering, PostProcessing]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Bloom

## 一句话定义

Bloom 是把画面中高亮区域扩散到周围，模拟镜头或眼睛眩光感的后处理效果。

## 为什么需要它

游戏中发光材质、霓虹灯、魔法特效、太阳和高亮 UI 需要更强的亮度感。Bloom 常配合 HDR 和 Tone Mapping 使用，让超过阈值的亮部产生柔和外扩。

## 核心原理

- 输入：HDR 场景颜色或提取后的高亮图。
- 处理过程：亮度筛选、多级降采样、模糊、上采样合成。
- 输出：叠加回场景颜色的泛光结果。
- 所在层级：后处理 Render Pass。

## 技术美术中的典型用途

- 强化发光材质和 VFX。
- 调整场景曝光和视觉层级。
- 控制移动端后处理成本。
- 排查画面发灰、过曝或边缘闪烁。

## Unity 中的相关场景

URP/HDRP Volume 中有 Bloom 设置。TA 需要关注 Threshold、Intensity、Scatter、Dirt Texture 和 HDR 是否启用。

## Unreal Engine 中的相关场景

Unreal Post Process Volume 中可调 Bloom。发光材质通常通过 Emissive 强度配合 Bloom 产生视觉发光。

## 常见误区

1. 用 Bloom 代替真实光照：Bloom 只影响画面扩散，不照亮周围物体。
2. 阈值过低导致整个画面发灰。
3. 移动端使用过多高分辨率模糊 Pass。

## 面试可能怎么问

### Bloom 的基本实现流程是什么？

回答要点：从场景颜色提取高亮区域，降采样并模糊，再逐级上采样合成回原图。

## 实践建议

做一个 HDR 发光材质，调整 Emission、Bloom Threshold 和 Tone Mapping，观察亮度链路。

## 相关条目

- [[后处理]]
- [[Render Pass]]
- [[Tone Mapping]]
- [[Render Target]]

## 参考来源

- 待补充

