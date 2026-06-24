---
title: "Morph Target"
aliases:
  - 变形目标
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Unreal, Animation]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Morph Target

## 一句话定义

Morph Target 是 Unreal 中通过目标形态顶点偏移驱动模型变形的技术，概念上接近 Blend Shape。

## 为什么需要它

Unreal 角色表情、口型、修型和局部变形常用 Morph Target。TA 需要保证 DCC 导出、命名、顶点顺序和运行时驱动一致。

## 核心原理

Morph Target 存储目标形态相对基础网格的顶点差值，运行时通过权重混合。要求基础网格和目标形态拓扑一致。

## 技术美术中的典型用途

- 面部表情。
- 口型同步。
- 肌肉和关节修型。
- 角色自定义滑条。

## Unity 中的相关场景

Unity 中通常称为 BlendShape，概念类似。

## Unreal Engine 中的相关场景

Skeletal Mesh 导入 Morph Target 后，可由动画曲线、蓝图、Control Rig 或材质逻辑配合驱动。

## 常见误区

1. DCC 中改了顶点顺序导致导入失败。
2. Morph 数量过多但没有性能预算。
3. 命名混乱，动画曲线无法稳定匹配。

## 面试可能怎么问

### Morph Target 导入失败常见原因是什么？

回答要点：拓扑或顶点顺序不一致、导出设置错误、命名不规范或引擎导入选项未启用。

## 实践建议

从 Maya/Blender 导出一个带口型 Morph Target 的角色到 Unreal，验证曲线驱动。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[建模规范]] | 建模规范偏输入资产质量；本条目可能关注某个具体制作或优化环节。 |
| [[贴图规范]] | 贴图规范偏纹理侧约束；本条目可能覆盖几何、绑定、动画或特效。 |

## 相关条目

- [[Blend Shape]]
- [[Rigging]]
- [[Unreal_Engine|Unreal Engine]]
- [[动画技术]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
