---
title: "U-Net"
aliases: []
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Model]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# U-Net

## 定义与解释

U-Net 是扩散图像模型中常见的去噪网络结构，负责在不同噪声阶段预测图像或潜变量的修正方向。

## 核心原理

U-Net 的结构通常包含下采样、瓶颈和上采样路径，并通过跳跃连接保留多尺度信息。在 Stable Diffusion 中，U-Net 接收潜变量、时间步和条件向量，逐步预测噪声或去噪结果。

TA 不需要深入实现每层网络，但需要知道 U-Net 是生成质量、风格响应和条件控制的核心位置。LoRA、ControlNet 等扩展常作用于或围绕 U-Net，因此模型版本和附加权重会明显改变结果。

## 用途

- 在 AIGC 资产流程中定位与 U-Net 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[CLIP]] | CLIP 编码文本条件，U-Net 执行去噪预测。 |
| [[VAE]] | VAE 转换像素和潜空间，U-Net 在潜空间中去噪。 |

## 常见误区

1. 把 U-Net 当成完整生成流程。
2. 更换模型或 LoRA 后不理解为什么画风变化。
3. 忽略 U-Net 与文本、控制条件的耦合。

## 相关条目

- [[Diffusion Model]]：U-Net 常作为扩散模型去噪网络。
- [[Stable_Diffusion]]：Stable Diffusion 流程包含 U-Net 去噪。
- [[LoRA]]：LoRA 常作用于 U-Net 等模块。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
