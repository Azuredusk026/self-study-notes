---
title: "Caption"
aliases:
  - 图像描述
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Dataset]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Caption

## 定义与解释

Caption 是对图像内容、风格、对象、构图或标签的文本描述，常用于数据集整理、训练 LoRA、检索和生成结果记录。

## 核心原理

Caption 的机制是把视觉内容转成模型可学习或可检索的文本信号。训练数据中的 Caption 会影响模型把哪些词和哪些视觉特征关联起来；过粗、过乱或错误的描述会让训练结果偏移。

TA 需要区分自然语言 Caption、Tag 列表和审核备注。用于训练时，Caption 要保持粒度一致、命名统一、去除无关噪声，并记录风格、主体、视角、材质等与目标有关的信息。

## 用途

- 在 AIGC 资产流程中定位与 Caption 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Tagging]] | Tagging 偏标签集合；Caption 偏完整文本描述。 |
| [[Prompt Engineering]] | Prompt 是生成指令；Caption 是数据或结果描述。 |

## 常见误区

1. Caption 粒度混乱，导致训练概念边界不稳定。
2. 把审核意见写进训练 Caption。
3. 不统一角色名、风格名和材质词。

## 相关条目

- [[Tagging]]：Tagging 常生成结构化标签，Caption 更接近描述文本。
- [[LoRA 训练流程]]：Caption 质量会影响 LoRA 训练效果。
- [[CLIP]]：文本与图像匹配常依赖 CLIP 类模型。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
