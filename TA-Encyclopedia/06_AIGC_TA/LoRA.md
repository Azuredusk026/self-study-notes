---
title: "LoRA"
aliases: []
category: "06_AIGC_TA"
confidence: medium
tags: [aigc, lora]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# LoRA

## 定义与解释

LoRA 是一种轻量微调方法，可在不完整重训大模型的情况下学习特定角色、风格、服装、物体或画法特征。

## 核心原理

LoRA 的核心是在模型部分权重旁添加低秩增量矩阵，训练时只学习这些小规模参数。生成时加载 LoRA 并设置权重，就能影响模型输出。

TA 使用 LoRA 时需要控制训练数据、Caption、触发词、训练步数、学习率和权重强度。LoRA 不是素材版权豁免，也不是万能风格按钮；过拟合会导致姿态僵硬、构图重复或污染基础模型风格。

## 用途

- 在 AIGC 资产流程中定位与 LoRA 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[IP-Adapter]] | LoRA 学习成参数文件，IP-Adapter 使用参考图条件。 |
| [[ControlNet]] | LoRA 改变风格/概念倾向，ControlNet 控制结构。 |

## 常见误区

1. 用来源不明数据训练正式项目 LoRA。
2. 训练集太少或 Caption 混乱导致过拟合。
3. 生成时 LoRA 权重过高破坏画面。

## 相关条目

- [[LoRA 训练流程]]：训练流程决定 LoRA 质量。
- [[Caption]]：Caption 会影响 LoRA 学到的概念。
- [[Stable_Diffusion]]：LoRA 常加载到 Stable Diffusion 工作流中。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
