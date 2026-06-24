---
title: "Diffusion Model"
aliases:
  - 扩散模型
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Diffusion]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Diffusion Model

## 定义与解释

Diffusion Model 是通过逐步加噪和逐步去噪学习数据分布的生成模型。图像生成中常见流程是从噪声逐步还原出符合条件的图像。

## 核心原理

扩散模型的核心是去噪过程。训练时模型学习在不同噪声强度下预测噪声或干净样本；生成时从随机噪声出发，在 Sampler 控制下多步迭代去噪，并受文本、图像或控制条件影响。

TA 不需要把它当黑盒按钮。理解噪声、步数、Sampler、Seed、Latent Space 和条件控制之间的关系，有助于解释为什么同一 Prompt 会因为参数变化出现构图、细节和风格差异。

## 用途

- 在 AIGC 资产流程中定位与 Diffusion Model 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[U-Net]] | U-Net 常作为去噪网络结构；Diffusion Model 是整体生成框架。 |
| [[VAE]] | VAE 负责像素和潜空间转换；扩散模型负责潜空间或图像空间去噪。 |

## 常见误区

1. 把步数越多等同于质量越高。
2. 不固定 Seed 却比较 Prompt 效果。
3. 忽略模型、Sampler 和 VAE 组合差异。

## 相关条目

- [[Stable_Diffusion]]：Stable Diffusion 是扩散模型生态中的常见实现。
- [[Sampler]]：Sampler 控制生成时的去噪路径。
- [[Latent Space]]：许多图像扩散模型在潜空间中去噪。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
