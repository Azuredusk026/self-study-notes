---
title: "BVH"
aliases:
  - Bounding Volume Hierarchy
  - 包围体层次结构
category: "Math_CS"
tags: [技术美术, Math, SpatialPartition]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# BVH

## 定义与解释

BVH（Bounding Volume Hierarchy）是用层级包围体组织几何对象的数据结构，用于加速射线、碰撞、可见性和空间查询。

## 核心原理

BVH 的机制是把大量对象递归分组，每个节点保存能包住子节点或几何的包围体。查询时先测试上层包围体，若不相交就跳过整个子树，从而减少逐个对象测试。

BVH 的效率取决于构建策略、包围体质量、树深度和对象更新频率。静态场景可以构建更高质量树，动态对象则需要考虑重建或 refit 成本。TA 在可视化和工具中可用 BVH 理解为什么空间查询不是线性扫全场景。

## 用途

- 在图形、动画、碰撞、寻路、编辑器工具或调试可视化中解释与 BVH 相关的结果。
- 把数学概念转成可验证的代码、Gizmos、Shader 计算或资源检查规则。
- 帮助 TA 与程序沟通空间关系、复杂度、数值稳定性和运行时限制。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[空间划分]] | 空间划分是大类，BVH 是层级包围体方案。 |
| [[Graph]] | BVH 是空间层级，Graph 是通用节点边关系。 |

## 常见误区

1. 动态物体频繁变化却使用昂贵重建策略。
2. 包围体过松导致剪枝效率低。
3. 把 BVH 查询结果当作最终精确碰撞，不做窄阶段检测。

## 相关条目

- [[AABB_OBB]]：BVH 节点常使用 AABB 作为包围体。
- [[Raycast]]：Raycast 可通过 BVH 加速。
- [[空间划分]]：BVH 是空间加速结构之一。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
