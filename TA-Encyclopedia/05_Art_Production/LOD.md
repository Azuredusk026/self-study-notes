---
title: "LOD"
aliases:
  - Level of Detail
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Optimization]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# LOD

## 定义与解释

LOD 是根据距离、屏幕占比或性能需求切换不同细节级别资产的优化方法。它可以作用于模型、材质、骨骼、贴图和特效复杂度。

## 核心原理

LOD 的机制是为同一资产准备多套成本不同的表现，并在运行时按屏幕尺寸或距离切换。LOD0 保留最高质量，后续级别逐步减少三角形、材质槽、骨骼、贴图尺寸或 Shader 复杂度。

好的 LOD 不是只减面。切换阈值、法线一致性、UV、材质槽、阴影 LOD、碰撞和动画骨骼都要匹配。TA 需要通过场景距离、目标平台和性能分析决定每级预算，避免明显 Pop 或资源浪费。

## 用途

- 在资产制作和引擎导入中定位与 LOD 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Retopology]] | Retopology 关注拓扑重建；LOD 关注多级运行时表现。 |
| [[Draw Call]] | LOD 可能降低材质和绘制成本，但不必然减少 Draw Call。 |

## 常见误区

1. LOD 只减面，不减材质和贴图成本。
2. 切换距离设置不合理产生明显跳变。
3. LOD 版本法线、UV 或材质不一致导致闪烁。

## 相关条目

- [[Low Poly]]：低级 LOD 通常使用更简化的低模。
- [[Texel Density]]：远距离 LOD 可降低贴图密度需求。
- [[Frustum Culling]]：LOD 常与剔除策略共同优化场景。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
