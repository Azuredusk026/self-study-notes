---
title: "Frustum Culling"
aliases:
  - 视锥剔除
category: "Math_CS"
tags: [技术美术, Math, Rendering, Optimization]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Frustum Culling

## 一句话定义

Frustum Culling 是剔除相机视锥外对象，避免提交不可见渲染对象的优化方法。

## 为什么需要它

场景中大量物体并不总在相机视野内。视锥剔除可以减少 Draw Call、渲染状态切换和 GPU 工作。TA 在场景优化、LOD、实例化和可见性调试时需要理解它。

## 核心原理

- 输入：相机视锥平面、对象包围体。
- 处理过程：检测 AABB、OBB 或球是否在六个视锥平面外。
- 输出：可见、不可见或相交。
- 所在层级：引擎可见性系统和渲染提交前。

## 技术美术中的典型用途

- 优化大场景和开放世界。
- 检查模型 Bounds 是否正确。
- 粒子、骨骼动画、Shader 顶点偏移的包围盒问题。
- 与 Occlusion Culling、LOD 配合。

## Unity 中的相关场景

Unity Renderer Bounds 会影响相机剔除。顶点动画超出 Bounds 时可能被错误裁掉，需要扩展包围盒。

## Unreal Engine 中的相关场景

Unreal 使用 Primitive Bounds 做可见性判断。Niagara、World Position Offset、Instanced Mesh 都可能需要关注 Bounds。

## 常见误区

1. 认为模型看不见一定不会被渲染：可能在视锥内但被遮挡，需要 Occlusion Culling。
2. Bounds 太小导致动画或特效突然消失。
3. Bounds 太大导致剔除失效。

## 面试可能怎么问

### 视锥剔除和遮挡剔除有什么区别？

回答要点：视锥剔除判断是否在相机视野范围内；遮挡剔除判断是否被其他物体挡住。

## 实践建议

制作一个顶点动画草丛，故意缩小 Bounds，观察相机边缘处被错误剔除的问题。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[线性代数]] | 线性代数提供基础语言；本条目可能是其中一个概念或算法应用。 |
| [[几何算法]] | 几何算法偏空间关系判断；本条目可能偏数据结构、搜索或变换。 |

## 相关条目

- [[AABB_OBB]]
- [[空间划分]]
- [[BVH]]
- [[Render Pass]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
