---
title: "Additive Animation"
aliases:
  - 叠加动画
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Animation]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Additive Animation

## 一句话定义

Additive Animation 是把一个动画作为增量叠加到基础动画上的技术。

## 为什么需要它

角色呼吸、受击、瞄准偏移、上半身动作、表情和小幅姿态修正，不一定需要重做完整动画。叠加动画能提高复用率，但需要正确的参考姿势和骨骼范围。

## 核心原理

叠加动画记录相对参考姿势的差值，再叠加到当前基础姿势上。参考姿势、权重和骨骼 Mask 决定结果是否稳定。

## 技术美术中的典型用途

- 呼吸和待机细节。
- 上半身瞄准或攻击叠加。
- 受击抖动。
- 表情和姿态修正。

## Unity 中的相关场景

Unity Animator Layer 支持 Additive 混合，可配合 Avatar Mask 控制影响骨骼范围。

## Unreal Engine 中的相关场景

Unreal Animation Blueprint 中可使用 Additive 动画、Aim Offset、Layered Blend per Bone 等节点。

## 常见误区

1. 参考姿势不一致导致姿态偏移。
2. 叠加权重过高造成动作变形。
3. 没有使用骨骼 Mask，影响了不该影响的部位。

## 面试可能怎么问

### Additive Animation 适合解决什么问题？

回答要点：适合在基础动作上叠加小幅或局部变化，如呼吸、瞄准、受击和表情，提高动画复用率。

## 实践建议

做一个上半身呼吸叠加层，测试走路、跑步、站立三种基础动画上的表现。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[建模规范]] | 建模规范偏输入资产质量；本条目可能关注某个具体制作或优化环节。 |
| [[贴图规范]] | 贴图规范偏纹理侧约束；本条目可能覆盖几何、绑定、动画或特效。 |

## 相关条目

- [[Root Motion]]
- [[动画技术]]
- [[Rigging]]
- [[Blend Shape]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
