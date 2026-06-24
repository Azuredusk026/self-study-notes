---
title: "Seed"
aliases:
  - 随机种子
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Workflow]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Seed

## 定义与解释

Seed 是生成流程中的随机种子，用于确定初始噪声或随机过程起点。固定 Seed 有助于对比 Prompt、模型和参数变化。

## 核心原理

Seed 的核心是控制随机性入口。同一模型、Sampler、步数、尺寸、Prompt、CFG 和工作流版本下，固定 Seed 通常能复现相近结果；任何关键条件变化都可能让结果偏离。

TA 应把 Seed 作为生成记录的一部分，而不是唯一复现条件。批量生成时可以用 Seed 范围探索变体，再把候选图的完整参数保存进审核表。

## 用途

- 在 AIGC 资产流程中定位与 Seed 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Sampler]] | Seed 控制随机起点，Sampler 控制迭代策略。 |
| [[Prompt Engineering]] | Prompt 控制语义目标，Seed 控制随机变体。 |

## 常见误区

1. 只保存 Seed 不保存其他参数。
2. 不同模型或尺寸下期待同一 Seed 复现同图。
3. 批量随机生成后不记录候选图参数。

## 相关条目

- [[Sampler]]：Seed 与采样器共同决定生成路径。
- [[CFG Scale]]：固定 Seed 后可观察 CFG 影响。
- [[ComfyUI]]：节点工作流中应记录 Seed。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
