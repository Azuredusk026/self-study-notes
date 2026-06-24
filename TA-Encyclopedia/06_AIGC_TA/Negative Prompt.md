---
title: "Negative Prompt"
aliases:
  - 负向提示词
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Prompt]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Negative Prompt

## 定义与解释

Negative Prompt 是生成时指定不希望出现的内容、风格或缺陷的文本条件。它用于降低某些错误倾向，但不能保证完全禁止。

## 核心原理

Negative Prompt 通过无条件/反向条件影响去噪方向，使模型远离某些语义或视觉特征。它与 CFG、Sampler、模型训练偏差和正向 Prompt 共同作用。

TA 应把 Negative Prompt 当作质量控制辅助，而不是堆词清单。过长负面词可能互相冲突或压制正常细节。工作流中应记录常用负面模板，并根据资产类型调整。

## 用途

- 在 AIGC 资产流程中定位与 Negative Prompt 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Prompt Engineering]] | Prompt Engineering 包含正向和负向提示策略。 |
| [[AIGC 资产审核规范]] | Negative Prompt 降低缺陷概率，审核规范决定结果能否使用。 |

## 常见误区

1. 堆大量负面词替代结果审核。
2. 不同模型使用同一负面模板不验证。
3. 负面词和正向目标冲突导致结果变差。

## 相关条目

- [[Prompt Engineering]]：Negative Prompt 是提示词策略的一部分。
- [[CFG Scale]]：CFG 会影响正负条件强度。
- [[Stable_Diffusion]]：Negative Prompt 是常见生成参数。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
