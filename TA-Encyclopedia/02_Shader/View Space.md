---
title: "View Space"
aliases:
  - Camera Space
  - 视图空间
category: "Shader"
tags: [技术美术, Shader, Space]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# View Space

## 一句话定义

View Space 是以相机为基准的坐标空间。

## 为什么需要它

很多屏幕相关效果需要知道物体相对相机的位置和方向，例如视线方向、深度重建、法线可视化、边缘检测、雾效和后处理。View Space 让这些计算以相机为中心表达。

## 核心原理

- 输入：World Space 位置或方向。
- 处理过程：乘以 View Matrix 转到相机坐标系。
- 输出：相机空间位置、方向或深度。
- 所在层级：Vertex/Fragment Shader 和后处理。

## 技术美术中的典型用途

- 屏幕空间法线和深度效果。
- Rim Light 与视线方向。
- 后处理深度重建。
- 相机相关的 VFX 变形和淡出。

## Unity 中的相关场景

Unity 中常用 View Matrix 或内置转换函数。URP 后处理和深度重建常涉及 View Space。

## Unreal Engine 中的相关场景

Unreal 材质和后处理提供 Camera Vector、Pixel Depth、Scene Depth 等相机相关数据。

## 常见误区

1. 把 View Space Z 直接当线性世界距离。
2. 相机翻转或平台差异导致深度方向理解错误。
3. 混用世界法线和视图法线做屏幕空间计算。

## 面试可能怎么问

### View Space 在后处理中有什么用？

回答要点：它可以根据深度和屏幕坐标重建相机空间位置，用于 SSAO、雾效、景深等屏幕空间效果。

## 实践建议

写一个 View Space Normal 可视化 Shader，观察相机旋转时颜色如何变化。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Graph]] | Material Graph 偏节点化编辑；本条目可能涉及更底层的代码、编译和采样细节。 |
| [[Texture Sampling]] | Texture Sampling 是常见操作；本条目可能覆盖更完整的 Shader 结构或控制策略。 |

## 相关条目

- [[World Space]]
- [[Clip Space]]
- [[Depth Buffer]]
- [[后处理]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
