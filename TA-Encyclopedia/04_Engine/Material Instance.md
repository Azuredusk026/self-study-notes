---
title: "Material Instance"
aliases:
  - 材质实例
category: "04_Engine"
tags: [技术美术, Unreal, Material]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Material Instance

## 一句话定义

Material Instance 是 Unreal 中基于父材质创建的参数化材质实例，用于复用 Shader 逻辑并调整参数。

## 为什么需要它

项目中大量材质共享相同逻辑，只是颜色、贴图、粗糙度、开关不同。材质实例能减少重复材质图，方便美术调参，也利于 TA 统一规范。

## 核心原理

父材质定义节点逻辑和可暴露参数；实例只覆盖参数值。静态参数可能影响编译变体，动态参数主要影响运行时 uniform。

## 技术美术中的典型用途

- 角色换色、皮肤和装备材质。
- 场景资产共享主材质。
- VFX 参数模板。
- 与蓝图或 Niagara 动态控制参数。

## Unity 中的相关场景

Unity 中类似思路是共享 Shader/Material，并通过 MaterialPropertyBlock 或材质实例控制参数。

## Unreal Engine 中的相关场景

常用 Material Instance Constant 做资产参数，Material Instance Dynamic 在运行时由蓝图或 C++ 修改。

## 常见误区

1. 每个资产都复制一份完整材质图。
2. 参数分组和命名混乱，美术难以使用。
3. 静态开关过多导致变体膨胀。

## 面试可能怎么问

### Material Instance 的优势是什么？

回答要点：复用父材质逻辑，减少重复维护，方便调参和统一规范，同时可通过实例覆盖贴图和数值参数。

## 实践建议

为一组道具建立主材质和多个实例，参数分组为 Base、Mask、Detail、VFX。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Unity]] | Unity 是引擎平台；本条目可能是其中某个系统或工作流。 |
| [[Unreal_Engine]] | Unreal 是引擎平台；本条目可能与其对应系统形成实现差异。 |

## 相关条目

- [[Material Editor]]
- [[MaterialPropertyBlock]]
- [[PBR]]
- [[Unreal_Engine|Unreal Engine]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
