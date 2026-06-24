---
title: "VAE"
aliases:
  - Variational Autoencoder
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Model]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# VAE

## 定义与解释

VAE 是 Stable Diffusion 类流程中常用的编码/解码模块，用于在像素图像和潜空间表示之间转换。

## 核心原理

VAE 的核心是压缩和重建。编码器把图像压缩成 Latent，解码器把 Latent 还原为像素图。扩散去噪通常发生在 Latent Space 中，最终图像质量和色彩会受 VAE 影响。

TA 需要记录使用的 VAE 版本，因为更换 VAE 可能改变颜色、对比度、细节和暗部表现。Img2Img、Inpainting 和高清修复都可能受到编码/解码差异影响。

## 用途

- 在 AIGC 资产流程中定位与 VAE 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[U-Net]] | U-Net 去噪，VAE 编码和解码图像。 |
| [[Sampler]] | Sampler 控制去噪路径，VAE 不负责采样步进。 |

## 常见误区

1. 更换 VAE 后不记录版本。
2. 把 VAE 色彩差异误判为 Prompt 问题。
3. 多次编码解码导致细节损失却未检查。

## 相关条目

- [[Latent Space]]：VAE 负责进入和离开潜空间。
- [[Stable_Diffusion]]：Stable Diffusion 流程常包含 VAE。
- [[Img2Img]]：Img2Img 需要先编码参考图。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
