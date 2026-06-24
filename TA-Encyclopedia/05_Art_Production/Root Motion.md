---
title: "Root Motion"
aliases:
  - 根运动
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Animation]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Root Motion

## 一句话定义

Root Motion 是从动画根骨骼中提取角色位移和旋转，用于驱动角色实际移动的方式。

## 为什么需要它

攻击位移、翻滚、跳跃、攀爬和过场动画常需要动画位移与游戏逻辑一致。Root Motion 能减少脚滑，但会增加动画、程序和网络同步协作成本。

## 核心原理

动画中 Root 骨骼记录位移和旋转，引擎播放时将这些运动提取并应用到角色 Actor 或 GameObject 上。

## 技术美术中的典型用途

- 检查 Root 骨骼方向和位移。
- 处理脚滑和动作位移。
- 动画导出规范。
- 与战斗、导航和网络同步协作。

## Unity 中的相关场景

Unity Animator 可启用 Apply Root Motion。Humanoid 动画还涉及 Bake Into Pose、Root Transform Position/Rotation 等设置。

## Unreal Engine 中的相关场景

Unreal 支持 Root Motion 提取和 Montage 使用。项目需要决定由动画驱动移动还是 Character Movement 驱动。

## 常见误区

1. Root 骨骼不是稳定根节点。
2. 动画位移和程序位移重复叠加。
3. 多人游戏中未考虑同步和预测。

## 面试可能怎么问

### Root Motion 的优缺点是什么？

回答要点：优点是动作和位移更匹配、减少脚滑；缺点是控制和网络同步更复杂，需要动画和程序协作。

## 实践建议

导入一个翻滚动画，分别测试启用和关闭 Root Motion 的位移表现。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[建模规范]] | 建模规范偏输入资产质量；本条目可能关注某个具体制作或优化环节。 |
| [[贴图规范]] | 贴图规范偏纹理侧约束；本条目可能覆盖几何、绑定、动画或特效。 |

## 相关条目

- [[动画技术]]
- [[Rigging]]
- [[Skinning]]
- [[Unity]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
