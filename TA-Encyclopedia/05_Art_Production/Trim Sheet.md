---
title: "Trim Sheet"
aliases:
  - 条带贴图
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Texture]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Trim Sheet

## 一句话定义

Trim Sheet 是把多种可复用边条、面板和细节集中到一张贴图中，供多个模型共享的贴图方法。

## 为什么需要它

场景资产如果每个都独立贴图，内存和制作成本会很高。Trim Sheet 适合建筑、硬表面、科幻面板和模块化场景，能提升复用率和风格一致性。

## 核心原理

模型 UV 被摆放到贴图中不同条带区域，通过重复、拉伸或模块化设计复用贴图细节。关键是统一纹素密度、边缘方向和材质风格。

## 技术美术中的典型用途

- 模块化场景生产。
- 降低贴图数量和内存。
- 提高美术资产风格一致性。
- 与 Decal、Vertex Color 和 Mask Map 组合。

## Unity 中的相关场景

Unity 项目中 Trim Sheet 可减少材质和贴图数量，有利于批处理和内存控制。

## Unreal Engine 中的相关场景

Unreal 模块化场景和建筑资产常使用 Trim Sheet，配合 Material Instance 调整颜色、粗糙度和细节。

## 常见误区

1. UV 随意拉伸导致纹素密度不一致。
2. Trim Sheet 设计只服务单个模型，失去复用价值。
3. 没有留出边缘 padding，Mipmap 后串色。

## 面试可能怎么问

### Trim Sheet 适合什么资产？

回答要点：适合模块化和硬表面资产，尤其是大量重复边条、面板、墙体和建筑结构。

## 实践建议

设计一张科幻墙体 Trim Sheet，用 5 个模块模型共享同一张贴图。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[建模规范]] | 建模规范偏输入资产质量；本条目可能关注某个具体制作或优化环节。 |
| [[贴图规范]] | 贴图规范偏纹理侧约束；本条目可能覆盖几何、绑定、动画或特效。 |

## 相关条目

- [[Texel Density]]
- [[UV]]
- [[贴图规范]]
- [[Texture Atlas]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
