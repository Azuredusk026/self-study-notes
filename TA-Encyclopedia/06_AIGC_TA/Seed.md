---
title: "Seed"
aliases:
  - 随机种子
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Workflow]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Seed

## 一句话定义

Seed 是生成过程中初始化随机噪声的种子，用于控制结果的可复现性。

## 为什么需要它

AIGC 工作流如果不记录 Seed，很难复现一张接近的图，也难以做参数对比。TA 在批量生成、审核和工具化流程中必须记录 Seed、模型、Prompt、Sampler 和尺寸。

## 核心原理

在相同模型、参数和实现条件下，相同 Seed 通常会得到相同或接近的初始噪声路径。实际复现还依赖模型版本、采样器、精度和工具实现。

> 待核验：跨工具、跨版本、跨硬件是否完全复现需要按具体环境测试。

## 技术美术中的典型用途

- 固定构图后迭代 Prompt。
- 生成同一角色或图标的多版本。
- 做参数 A/B 测试。
- 记录审核通过资产的生成配置。

## Unity 中的相关场景

做图标、贴图参考或 UI 资产时，Seed 应写入生成记录，方便后续重新导出更高分辨率或改版。

## Unreal Engine 中的相关场景

用于场景概念和 VFX 参考时，Seed 记录能帮助团队在同一构图上继续迭代。

## 常见误区

1. 只保存图片，不保存 Seed 和工作流。
2. 以为相同 Seed 在任何工具中都完全一致。
3. 批量生成时随机 Seed 不落盘，无法回查。

## 面试可能怎么问

### 为什么 AIGC 资产生成要记录 Seed？

回答要点：Seed 是复现和迭代的重要条件，配合模型、Prompt、Sampler、尺寸和工作流记录，才能追踪结果来源。

## 实践建议

为每张候选图建立 JSON 或表格记录：模型、Seed、Prompt、Negative Prompt、Sampler、CFG、尺寸和审核状态。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Stable_Diffusion]] | Stable Diffusion 是常见生成模型生态；本条目可能关注其中某个节点、流程或落地规范。 |
| [[AIGC管线落地]] | 管线落地强调团队流程；单项工具条目强调具体输入、参数和限制。 |

## 相关条目

- [[Prompt Engineering]]
- [[CFG Scale]]
- [[Sampler]]
- [[ComfyUI]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
