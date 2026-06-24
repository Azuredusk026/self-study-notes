---
title: "Latent Space"
aliases:
  - 潜空间
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Model]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Latent Space

## 定义与解释

Latent Space 是模型内部使用的压缩表示空间，Stable Diffusion 等模型常在潜空间中执行去噪，再解码为图像。

## 核心原理

潜空间的机制是用 VAE 将像素图像编码成低维特征，再由扩散模型在这个空间中采样和去噪，最后解码回像素。这样可以降低计算成本，并让模型在更抽象的特征层面生成图像。

TA 理解 Latent Space 有助于解释为什么分辨率、VAE、放大、Img2Img 强度和局部重绘会影响结果。潜空间不是可直接编辑的普通贴图，它的数值语义由模型训练决定。

## 用途

- 在 AIGC 资产流程中定位与 Latent Space 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[VAE]] | VAE 是编码/解码器；Latent Space 是编码后的表示空间。 |
| [[Diffusion Model]] | 扩散模型定义去噪过程，Latent Space 是执行该过程的表示空间之一。 |

## 常见误区

1. 把 Latent 当作普通 RGB 图像理解。
2. 更换 VAE 后不检查色彩和细节差异。
3. 忽略分辨率和潜空间尺寸的对应关系。

## 相关条目

- [[VAE]]：VAE 负责像素空间和潜空间转换。
- [[Stable_Diffusion]]：Stable Diffusion 常在 Latent Space 中去噪。
- [[Sampler]]：Sampler 在潜空间中推进去噪过程。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
