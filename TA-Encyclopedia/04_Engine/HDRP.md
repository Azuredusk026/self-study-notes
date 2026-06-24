---
title: "HDRP"
aliases:
  - High Definition Render Pipeline
category: "04_Engine"
tags: [技术美术, Unity, Rendering]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# HDRP

## 一句话定义

HDRP 是 Unity 面向高保真实时渲染的 Scriptable Render Pipeline，主要服务 PC、主机和高端硬件项目。

## 为什么需要它

HDRP 提供更完整的光照、后处理、体积、材质和高质量渲染能力。TA 需要理解它的价值和成本：更高画质通常意味着更复杂的材质、更重的渲染路径和更严格的性能预算。

## 核心原理

HDRP 基于 SRP 架构，提供面向高端项目的 Lit 材质、Decal、Volume、Probe、后处理和调试视图。它适合追求画质的项目，但不适合所有平台。

> 待核验：HDRP 的具体功能、路径和 API 会随 Unity 版本变化，项目落地前需要查阅对应版本官方文档。

## 技术美术中的典型用途

- 高保真角色、场景和影视化实时渲染。
- 材质 LookDev 和灯光调试。
- 体积雾、屏幕空间效果和高级后处理。
- 与 URP 做项目技术路线对比。

## Unity 中的相关场景

HDRP 项目通常需要更严格的灯光、反射、材质、Volume 和平台配置管理。TA 还需要关注 Shader Variant、构建体积和目标机性能。

## Unreal Engine 中的相关场景

Unreal 默认面向高保真场景的能力更集中在其 Deferred、Lumen、Nanite、材质和后处理体系中，可与 HDRP 做技术路线对比。

## 常见误区

1. 以为 HDRP 一定比 URP 更适合所有项目。
2. 只看编辑器画质，不看目标平台性能。
3. 忽略材质和后处理复杂度对迭代成本的影响。

## 面试可能怎么问

### URP 和 HDRP 如何选择？

回答要点：看目标平台、画质目标、团队技术能力、性能预算和项目周期。URP 更偏跨平台和轻量，HDRP 更偏高保真和高端硬件。

## 实践建议

用同一套资产分别在 URP 和 HDRP 中搭建材质球场景，对比光照、后处理、性能和工作流差异。

## 相关条目

- [[URP]]
- [[SRP]]
- [[PBR]]
- [[IBL]]

## 参考来源

- 待补充

