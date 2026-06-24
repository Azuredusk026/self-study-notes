---
title: "Overdraw"
aliases:
  - 过度绘制
category: "Rendering"
tags: [技术美术, Rendering, Optimization]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Overdraw

## 一句话定义

Overdraw 指同一屏幕像素被多个片元重复绘制或着色的现象。

## 为什么需要它

Overdraw 会让 Fragment Shader 重复执行，尤其在透明粒子、UI、植被、毛发、烟雾和大面积特效中常见。TA 优化移动端和特效性能时，Overdraw 往往比面数更关键。

## 核心原理

- 输入：屏幕上重叠的图元和片元。
- 处理过程：同一区域多次通过或尝试通过深度、混合和颜色写入。
- 输出：更高片元执行次数和带宽消耗。
- 所在层级：光栅化和片元着色成本。

## 技术美术中的典型用途

- 粒子特效预算。
- UI 层级和透明图集优化。
- 植被 Alpha Clip 与几何复杂度取舍。
- Scene View Overdraw 或 RenderDoc 热点分析。

## Unity 中的相关场景

Unity Scene View 可查看 Overdraw 模式。URP 移动端项目中，大量透明特效和 UI 叠层会明显影响 GPU。

## Unreal Engine 中的相关场景

Unreal 提供 Shader Complexity / Quad Overdraw 等视图帮助分析材质复杂度和过度绘制。

## 常见误区

1. 只压面数不看屏幕覆盖面积。
2. 认为透明贴图空白区域没有成本：卡片仍可能产生片元。
3. 用更复杂 Shader 处理本可通过网格或贴图预算解决的问题。

## 面试可能怎么问

### 如何优化粒子 Overdraw？

回答要点：减小屏幕覆盖面积、减少叠层、降低分辨率和采样、用软粒子谨慎处理交界、必要时用 Mesh VFX 替代大透明面片。

## 实践建议

做一个命中特效：比较一张大透明贴图和多个紧贴轮廓的小 Mesh 粒子的 Overdraw 差异。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[PBR]] | 更偏材质和光照模型；本条目更关注具体渲染环节或画面效果。 |
| [[Shader基础]] | Shader 是实现手段；本条目通常还涉及管线状态、缓冲读写和引擎配置。 |

## 相关条目

- [[Rasterization]]
- [[Fragment Shader]]
- [[Alpha Blend]]
- [[Early-Z]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
