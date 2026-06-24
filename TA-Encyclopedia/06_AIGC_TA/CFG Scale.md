---
title: "CFG Scale"
aliases:
  - Classifier-Free Guidance Scale
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Sampling]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# CFG Scale

## 定义与解释

CFG Scale 是扩散生成中控制文本条件约束强度的参数。它影响模型在遵循 Prompt 和保留自然采样之间的平衡。

## 核心原理

CFG 的核心是 Classifier-Free Guidance：模型会比较有条件和无条件预测，并按权重强化条件方向。Scale 越高，Prompt 约束越强，但也可能带来过饱和、结构僵硬、细节破碎或不自然纹理。

CFG 不是质量滑杆。合适范围取决于模型、Sampler、步数、Prompt、LoRA 和图像尺寸。TA 做可复现工作流时应记录 CFG，并用对比图评估它对风格、构图和材质的影响。

## 用途

- 在 AIGC 资产流程中定位与 CFG Scale 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Seed]] | Seed 控制随机初始状态；CFG 控制文本条件强度。 |
| [[Negative Prompt]] | Negative Prompt 提供反向条件，CFG 决定条件整体权重。 |

## 常见误区

1. 把 CFG 拉高当作提升质量。
2. 比较结果时不固定 Seed 和 Sampler。
3. 不同模型套用同一 CFG 范围。

## 相关条目

- [[Prompt Engineering]]：CFG 决定 Prompt 约束强度。
- [[Sampler]]：CFG 与采样器和步数共同影响结果。
- [[Stable_Diffusion]]：CFG 是 Stable Diffusion 常见生成参数。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
