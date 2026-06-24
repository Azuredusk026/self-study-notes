---
title: "Latent Space"
aliases:
  - 潜空间
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Model]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Latent Space

## 一句话定义

Latent Space 是模型内部用于表示图像语义和结构的压缩特征空间。

## 为什么需要它

在潜空间中生成比直接处理像素更高效。很多 AIGC 操作，如 latent upscale、img2img、inpaint 和噪声控制，都与潜空间表示有关。

## 核心原理

图像通过 VAE 编码成潜变量，扩散模型在潜变量上去噪，最后再解码回图像。潜空间不直接等于像素，但保留了足够的语义和结构信息。

## 技术美术中的典型用途

- 理解 Img2Img 的 denoise strength。
- 理解潜空间放大和图像重绘。
- 分析为什么同一 Seed 和参数能复现相近构图。

## Unity 中的相关场景

Unity 资产生成工作流中，潜空间相关参数影响输出图结构稳定性，间接影响后续导入和修图成本。

## Unreal Engine 中的相关场景

用于场景概念和 VFX 参考时，潜空间控制影响构图、色块和整体风格稳定性。

## 常见误区

1. 以为潜空间可以像 PSD 图层一样直接编辑。
2. 不理解 denoise strength 改变的是原图保留程度。
3. 把 latent upscale 和普通图像超分完全等同。

## 面试可能怎么问

### Latent Space 对图像生成有什么意义？

回答要点：它让模型在压缩表示中生成和编辑图像，降低计算成本，同时保留语义和结构信息。

## 实践建议

对同一张输入图测试不同 denoise strength，观察潜空间重绘对结构保留的影响。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Stable_Diffusion]] | Stable Diffusion 是常见生成模型生态；本条目可能关注其中某个节点、流程或落地规范。 |
| [[AIGC管线落地]] | 管线落地强调团队流程；单项工具条目强调具体输入、参数和限制。 |

## 相关条目

- [[VAE]]
- [[Img2Img]]
- [[Inpainting]]
- [[Seed]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
