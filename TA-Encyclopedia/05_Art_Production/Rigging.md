---
title: "Rigging"
aliases:
  - 绑定
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Rigging]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Rigging

## 定义与解释

Rigging 是为角色或机械模型建立骨骼、控制器、约束和导出骨架，使模型可以被动画稳定驱动的过程。

## 核心原理

Rigging 的核心是区分动画控制系统和游戏运行时骨架。控制器、约束、IK/FK、辅助骨骼用于动画制作；导出骨架则需要简洁、稳定、可重定向并符合引擎限制。

TA 需要在 DCC 和引擎之间建立骨骼命名、轴向、层级、Root、控制器清理、动画 Bake 和导出规则。一个 Rig 在 DCC 中好用，不代表进入 Unity 或 Unreal 后就可用。

## 用途

- 在资产制作和引擎导入中定位与 Rigging 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Skinning]] | Rigging 建立骨架和控制；Skinning 负责顶点如何随骨骼变形。 |
| [[角色绑定]] | 角色绑定更偏项目角色规范；Rigging 是通用绑定流程。 |

## 常见误区

1. 控制器和导出骨架混在一起。
2. 骨骼命名和轴向不统一。
3. 只在 DCC 中验证，导入引擎后才暴露问题。

## 相关条目

- [[角色绑定]]：角色绑定是 Rigging 在角色资产上的具体规范。
- [[Skinning]]：Skinning 把网格顶点绑定到骨骼。
- [[Root Motion]]：Rig 结构决定 Root Motion 能否稳定导出。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
