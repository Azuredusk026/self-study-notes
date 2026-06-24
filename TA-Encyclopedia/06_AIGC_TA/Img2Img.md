---
title: "Img2Img"
aliases:
  - Image to Image
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Workflow]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Img2Img

## 定义与解释

Img2Img 是以已有图像作为初始参考，再通过扩散去噪生成新图的流程。它用于变体生成、风格迁移、草图细化和资产迭代。

## 核心原理

Img2Img 的核心是先把参考图编码到潜空间并加入一定噪声，再按 Prompt 和参数重新去噪。Denoise Strength 决定保留原图结构和重新生成之间的比例。

TA 使用 Img2Img 时要明确参考图的用途：构图、色彩、风格还是细节。强度过低变化有限，过高会丢失设计意图。正式资产流程还要记录原图来源和处理链路。

## 用途

- 在 AIGC 资产流程中定位与 Img2Img 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[ControlNet]] | Img2Img 从整图状态出发；ControlNet 注入结构条件。 |
| [[Seed]] | Seed 仍影响 Img2Img 的随机细节。 |

## 常见误区

1. Denoise Strength 不记录，结果无法复现。
2. 参考图版权和来源不清。
3. 把低清草图直接当最终资产来源。

## 相关条目

- [[Inpainting]]：Inpainting 是局部区域的 Img2Img 变体。
- [[Stable_Diffusion]]：Img2Img 是常见 Stable Diffusion 工作流。
- [[ControlNet]]：ControlNet 可补充结构控制。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
