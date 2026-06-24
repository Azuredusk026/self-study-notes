---
title: "VAE"
aliases:
  - Variational Autoencoder
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Model]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# VAE

## 一句话定义

VAE 是把图像压缩到潜空间并从潜空间解码回图像的模型组件。

## 为什么需要它

许多图像生成模型不直接在原始像素空间里去噪，而是在更紧凑的 Latent Space 中工作。TA 需要知道 VAE 会影响颜色、细节、对比度和最终解码质量。

## 核心原理

编码器把图像压缩为潜变量，解码器把潜变量还原为图像。扩散过程常在潜空间中进行，最后再通过 VAE 解码成可见图像。

> 待核验：不同模型使用的 VAE 结构和替换策略不同，具体兼容性需要按模型文档确认。

## 技术美术中的典型用途

- 排查生成图偏灰、偏色或细节异常。
- 理解 Latent Upscale、潜空间编辑和图像解码。
- 管理模型、VAE、工作流版本的一致性。

## Unity 中的相关场景

VAE 影响输出图质量，最终会影响进入 Unity 的 UI、贴图参考或图标清晰度。

## Unreal Engine 中的相关场景

在 Unreal 相关概念图和材质参考生成中，VAE 解码质量会影响后续人工重制和参考可信度。

## 常见误区

1. 把 VAE 当作普通后处理滤镜。
2. 混用不兼容 VAE 导致颜色或细节异常。
3. 只保存最终图，不记录使用的 VAE。

## 面试可能怎么问

### VAE 在 Stable Diffusion 类工作流中的作用是什么？

回答要点：它负责图像与潜空间之间的编码和解码，影响生成过程的表示空间和最终图像还原质量。

## 实践建议

固定 Prompt、Seed 和模型，对比不同 VAE 的颜色和细节差异，并把结果写入工作流记录。

## 相关条目

- [[Latent Space]]
- [[Diffusion Model]]
- [[Stable_Diffusion|Stable Diffusion]]

## 参考来源

- 待补充

