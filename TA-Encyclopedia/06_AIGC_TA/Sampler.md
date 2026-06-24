---
title: "Sampler"
aliases:
  - 采样器
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Sampling]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Sampler

## 定义与解释

Sampler 是扩散模型生成时控制去噪路径和步进策略的算法。它会影响速度、细节、稳定性和同一 Seed 下的结果形态。

## 核心原理

Sampler 决定每一步如何从噪声预测更新到下一状态。不同采样器在收敛速度、随机性、细节保留和高 CFG 稳定性上不同，步数也会改变结果。

TA 做可复现工作流时必须记录 Sampler、步数、Scheduler、Seed、CFG 和模型版本。采样器不是越新越好，而要根据资产类型、速度需求和稳定性选择。

## 用途

- 在 AIGC 资产流程中定位与 Sampler 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Seed]] | Seed 给随机起点，Sampler 决定去噪路径。 |
| [[CFG Scale]] | CFG 控制条件强度，Sampler 控制迭代方式。 |

## 常见误区

1. 只记录 Seed 不记录 Sampler。
2. 步数越高越好。
3. 换采样器后还声称与旧图可复现。

## 相关条目

- [[Diffusion Model]]：Sampler 推进扩散去噪过程。
- [[Seed]]：Seed 与 Sampler 共同决定随机路径。
- [[CFG Scale]]：Sampler 对 CFG 的响应会影响结果。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
