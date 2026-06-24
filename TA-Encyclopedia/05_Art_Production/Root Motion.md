---
title: "Root Motion"
aliases:
  - 根运动
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Animation]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Root Motion

## 定义与解释

Root Motion 是从动画根骨骼或根节点提取角色整体位移和旋转，并用于驱动角色移动的机制。

## 核心原理

Root Motion 的关键是把运动来源从代码速度转移到动画数据。动画中的 Root 轨迹被引擎解析后，应用到角色胶囊体、Actor 或 Transform 上，使脚步和位移更贴合。

它依赖清晰 Root 骨骼、动画 Bake、循环边界和引擎导入设置。TA 需要和动画、程序约定哪些动画使用 Root Motion，哪些使用代码驱动，并处理转向、混合、网络同步和碰撞关系。

## 用途

- 在资产制作和引擎导入中定位与 Root Motion 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Additive Animation]] | Additive 叠加姿势差值；Root Motion 提取整体位移。 |
| [[Skinning]] | Skinning 处理网格变形；Root Motion 处理角色整体移动。 |

## 常见误区

1. Root 骨骼和骨盆骨骼职责混乱。
2. 循环动画首尾 Root 不连续导致滑步或跳变。
3. 没有和程序移动系统约定权责。

## 相关条目

- [[Rigging]]：Root 骨骼结构来自 Rigging 规范。
- [[动画技术]]：Root Motion 是动画驱动移动的一种技术。
- [[Additive Animation]]：Additive 动画通常不应污染 Root 位移。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
