---
title: "Frustum Culling"
aliases:
  - 视锥剔除
category: "Math_CS"
tags: [技术美术, Math, Rendering, Optimization]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Frustum Culling

## 定义与解释

Frustum Culling 是用相机视锥剔除不可见对象的可见性优化方法。它通过测试对象包围体是否在视锥内，减少不必要渲染提交。

## 核心原理

视锥通常由相机的近远裁面和上下左右平面组成。对象的 AABB、OBB 或包围球与这些平面测试，如果完全在某个平面外，就可以判定不可见并跳过渲染。

Frustum Culling 是粗粒度可见性判断，不处理遮挡在其他物体后面的情况。TA 需要关注包围盒是否正确、动画或顶点位移是否扩展 Bounds、多相机和阴影相机是否使用不同剔除规则。

## 用途

- 在图形、动画、碰撞、寻路、编辑器工具或调试可视化中解释与 Frustum Culling 相关的结果。
- 把数学概念转成可验证的代码、Gizmos、Shader 计算或资源检查规则。
- 帮助 TA 与程序沟通空间关系、复杂度、数值稳定性和运行时限制。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Overdraw]] | Frustum Culling 减少视锥外对象，Overdraw 处理视锥内重复覆盖。 |
| [[LOD]] | LOD 降低可见对象成本，Frustum Culling 跳过不可见对象。 |

## 常见误区

1. Bounds 太小导致对象突然消失。
2. 以为视锥剔除能处理遮挡剔除。
3. 顶点动画或特效超出包围盒未更新。

## 相关条目

- [[AABB_OBB]]：视锥剔除常测试包围盒。
- [[空间划分]]：空间结构可加速剔除候选。
- [[LOD]]：剔除和 LOD 共同影响可见资产成本。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
