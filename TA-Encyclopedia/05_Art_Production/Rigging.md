---
title: "Rigging"
aliases:
  - 绑定
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Rigging]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Rigging

## 一句话定义

Rigging 是为角色或机械模型建立骨骼、控制器和约束系统，使其能够被动画驱动的过程。

## 为什么需要它

没有可靠 Rig，动画难以制作，导入引擎后也容易出现骨骼层级、Root Motion、重定向和变形问题。TA 需要在美术、动画和程序之间保证 Rig 可用、可导出、可维护。

## 核心原理

Rig 包括骨骼层级、控制器、约束、IK/FK、蒙皮和导出骨架。游戏项目通常要求控制 Rig 和导出骨架分离，避免把无关控制器带入引擎。

## 技术美术中的典型用途

- 角色绑定规范。
- 动画导出骨架检查。
- IK/FK 控制器设计。
- 引擎重定向和 Root Motion 支持。

## Unity 中的相关场景

Unity Humanoid/Generic Rig、Avatar、Animation Rigging 和 Retargeting 都依赖合理骨架和命名。

## Unreal Engine 中的相关场景

Unreal Skeletal Mesh、Skeleton、Control Rig、IK Rig 和 Retargeter 都与 Rigging 质量相关。

## 常见误区

1. 控制器和导出骨架混在一起。
2. 骨骼命名和轴向不统一。
3. 只在 DCC 中可用，导入引擎后才暴露问题。

## 面试可能怎么问

### 游戏角色 Rig 和影视 Rig 有什么差异？

回答要点：游戏 Rig 更强调运行时骨架、导出限制、性能、重定向和引擎兼容；影视 Rig 可以更复杂，但不一定适合实时引擎。

## 实践建议

做一个简单双足角色 Rig，导出到 Unity/Unreal，验证动画播放、Root 和骨骼层级。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[建模规范]] | 建模规范偏输入资产质量；本条目可能关注某个具体制作或优化环节。 |
| [[贴图规范]] | 贴图规范偏纹理侧约束；本条目可能覆盖几何、绑定、动画或特效。 |

## 相关条目

- [[角色绑定]]
- [[Skinning]]
- [[Root Motion]]
- [[Retopology]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
