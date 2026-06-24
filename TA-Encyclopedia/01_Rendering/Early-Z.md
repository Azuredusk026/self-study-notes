---
title: "Early-Z"
aliases:
  - Early Depth Test
category: "Rendering"
tags: [技术美术, Rendering, Optimization]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Early-Z

## 一句话定义

Early-Z 是在片元着色前尽早执行深度测试，从而跳过被遮挡片元的优化机制。

## 为什么需要它

Fragment Shader 可能包含多次纹理采样、复杂光照和分支。若一个片元最终被前面的物体遮挡，提前丢弃它可以节省大量 GPU 成本。TA 在优化复杂材质和高 Overdraw 场景时需要理解 Early-Z 的触发条件。

## 核心原理

- 输入：片元深度、Depth Buffer、深度状态。
- 处理过程：在 Fragment Shader 前做深度比较，失败则不执行片元着色。
- 输出：减少实际执行的片元数。
- 所在层级：GPU 深度优化。

## 技术美术中的典型用途

- 深度预通道优化复杂材质。
- 检查透明、Alpha Test、discard 是否破坏 Early-Z。
- 分析植被、粒子、毛发和卡片特效的片元成本。

## Unity 中的相关场景

Unity 中 Opaque 队列通常更容易利用 Early-Z。使用 `clip()`、Alpha Clipping、透明队列和关闭 ZWrite 时，需要评估 Early-Z 收益。

## Unreal Engine 中的相关场景

Unreal 的 Early Z-pass 设置会影响 Masked 材质、复杂场景和 Nanite/非 Nanite 物体的深度预处理策略。

## 常见误区

1. 认为 Early-Z 总是生效：透明、深度写入、discard 等会影响。
2. 为所有场景强行加 Depth Prepass：额外几何提交也有成本。
3. 只看 Draw Call，不看片元复杂度和覆盖面积。

## 面试可能怎么问

### Early-Z 为什么能优化性能？

回答要点：它让被遮挡片元在执行 Fragment Shader 前被丢弃，减少纹理采样和光照计算。

## 实践建议

用一个高采样复杂材质放在墙后，比较有无深度预通道或遮挡情况下的 GPU 时间。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[PBR]] | 更偏材质和光照模型；本条目更关注具体渲染环节或画面效果。 |
| [[Shader基础]] | Shader 是实现手段；本条目通常还涉及管线状态、缓冲读写和引擎配置。 |

## 相关条目

- [[Depth Buffer]]
- [[Z-Test]]
- [[Overdraw]]
- [[Alpha Test]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
