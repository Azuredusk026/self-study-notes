---
title: "Stable_Diffusion"
aliases: []
category: "06_AIGC_TA"
confidence: medium
tags: [aigc, stable-diffusion]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# Stable Diffusion

## 定义与解释

Stable Diffusion 是常用于图像生成、风格探索和资产辅助生产的潜空间扩散模型生态。

## 核心原理

Stable Diffusion 的典型流程是：CLIP 将文本条件编码，U-Net 在 Latent Space 中按 Sampler 多步去噪，VAE 再把潜空间结果解码为图像。LoRA、ControlNet、IP-Adapter、Img2Img 和 Inpainting 都是在这个基础流程上增加条件或改写入口。

TA 需要把它视为可配置生成系统，而不是单一软件。模型版本、VAE、Sampler、Seed、CFG、分辨率、Prompt、参考图和节点工作流共同决定结果，正式资产还必须经过来源和质量审核。

## 用途

- 在 AIGC 资产流程中定位与 Stable_Diffusion 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[LoRA]] | LoRA 是附加微调权重，Stable Diffusion 是基础生成模型生态。 |
| [[ControlNet]] | ControlNet 给 Stable Diffusion 增加结构条件。 |

## 常见误区

1. 把模型名、界面工具和完整工作流混为一谈。
2. 只保存结果图，不保存参数和模型版本。
3. 生成结果未经审核直接进入正式资源库。

## 相关条目

- [[Diffusion Model]]：Stable Diffusion 属于扩散模型应用。
- [[Latent Space]]：它通常在潜空间中去噪。
- [[ComfyUI]]：ComfyUI 可组织 Stable Diffusion 工作流。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
