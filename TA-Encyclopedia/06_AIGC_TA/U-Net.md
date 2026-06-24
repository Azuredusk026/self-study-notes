---
title: "U-Net"
aliases: []
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Model]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# U-Net

## 一句话定义

U-Net 是扩散模型中常见的去噪网络结构，用于根据条件预测并移除噪声。

## 为什么需要它

在 AIGC TA 视角里，U-Net 不一定需要推导网络结构，但要知道它是生成质量、风格能力、LoRA 注入和条件控制的重要位置。

## 核心原理

U-Net 通过编码-解码结构处理不同尺度特征，并结合文本、时间步和控制条件预测噪声或干净样本方向。

> 待核验：不同模型家族可能不再使用传统 U-Net 或结构差异明显，具体要看模型文档。

## 技术美术中的典型用途

- 理解 LoRA、ControlNet 等为什么能影响生成。
- 解释模型能力来自权重和训练数据，而不是单个 Prompt。
- 记录工作流中模型和附加权重版本。

## Unity 中的相关场景

Unity 侧通常不直接使用 U-Net，但生成结果会进入图标、贴图和概念参考流程。

## Unreal Engine 中的相关场景

Unreal 项目中同样主要使用生成结果，不直接部署 U-Net，除非做本地工具链或插件。

## 常见误区

1. 把 U-Net 当成可单独替换的普通节点。
2. 认为 LoRA 只改变 Prompt，不影响网络权重行为。
3. 不记录 checkpoint 和附加权重版本。

## 面试可能怎么问

### U-Net 在扩散模型中大致做什么？

回答要点：它在每个采样步根据噪声状态和条件预测去噪方向，是生成过程的核心网络之一。

## 实践建议

整理一张工作流图，标出文本编码、U-Net 去噪、VAE 解码和 ControlNet 条件输入的位置。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Stable_Diffusion]] | Stable Diffusion 是常见生成模型生态；本条目可能关注其中某个节点、流程或落地规范。 |
| [[AIGC管线落地]] | 管线落地强调团队流程；单项工具条目强调具体输入、参数和限制。 |

## 相关条目

- [[Diffusion Model]]
- [[LoRA]]
- [[ControlNet]]
- [[VAE]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
