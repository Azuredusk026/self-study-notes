---
title: "Raycast"
aliases:
  - 射线检测
category: "Math_CS"
tags: [技术美术, Math, Physics, Tools]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Raycast

## 定义与解释

Raycast 是沿射线在场景中查询碰撞、命中点、法线或对象的操作。它常用于点击拾取、射击检测、地面检测、工具摆放和调试可视化。

## 核心原理

Raycast 的机制是把 Ray 与场景中的碰撞体或几何加速结构相交测试，并返回最近或所有命中结果。引擎通常会结合碰撞层、触发器、距离、查询模式和物理场景设置过滤结果。

TA 使用 Raycast 做编辑器工具时，要确认坐标空间、Layer Mask、碰撞体是否存在、查询距离和命中法线。渲染网格可见不代表物理查询可命中，因为碰撞体和渲染网格可能不同。

## 用途

- 在图形、动画、碰撞、寻路、编辑器工具或调试可视化中解释与 Raycast 相关的结果。
- 把数学概念转成可验证的代码、Gizmos、Shader 计算或资源检查规则。
- 帮助 TA 与程序沟通空间关系、复杂度、数值稳定性和运行时限制。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Ray]] | Ray 是查询几何，Raycast 是执行查询并返回结果。 |
| [[BVH]] | BVH 可加速大量 Raycast 查询。 |

## 常见误区

1. 以为看得见的网格一定能被 Raycast 命中。
2. Layer Mask 或 Trigger 设置错误导致漏检。
3. 没有处理多命中和最近命中的区别。

## 相关条目

- [[Ray]]：Raycast 基于射线定义查询方向。
- [[AABB_OBB]]：包围体可加速射线粗判。
- [[几何算法]]：射线相交测试属于几何算法。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
