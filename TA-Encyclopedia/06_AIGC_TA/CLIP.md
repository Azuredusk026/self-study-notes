---
title: "CLIP"
aliases: []
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Model]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# CLIP

## 定义与解释

CLIP 是连接文本和图像语义表示的模型家族，在 AIGC 中常用于文本编码、图文匹配、检索和风格/内容对齐。

## 核心原理

在 Stable Diffusion 类流程中，CLIP 文本编码器会把 Prompt 转成条件向量，供 U-Net 在去噪过程中使用。它并不直接生成图像，而是提供文本语义约束。

CLIP 对词语、顺序、权重和训练语料的理解有边界。TA 需要知道 Prompt 不会按人类语法完全执行，复杂资产描述应拆分验证，并结合参考图、ControlNet、IP-Adapter 或后期精修控制结果。

## 用途

- 在 AIGC 资产流程中定位与 CLIP 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[U-Net]] | CLIP 编码文本条件；U-Net 执行去噪生成。 |
| [[Caption]] | Caption 是文本数据；CLIP 可把文本映射到语义表示。 |

## 常见误区

1. 认为 Prompt 会被模型逐字严格执行。
2. 用过长复杂描述却不拆分验证。
3. 忽略不同模型使用的文本编码器和训练语料差异。

## 相关条目

- [[Prompt Engineering]]：Prompt 通过 CLIP 等文本编码器影响生成。
- [[Stable_Diffusion]]：Stable Diffusion 流程常包含 CLIP 文本编码。
- [[IP-Adapter]]：IP-Adapter 提供图像条件补充文本条件。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
