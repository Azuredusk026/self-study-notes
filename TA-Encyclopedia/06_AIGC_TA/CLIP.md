---
title: "CLIP"
aliases: []
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Model]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# CLIP

## 一句话定义

CLIP 是把文本和图像映射到相近语义空间的模型，常用于让生成模型理解 Prompt 与图像内容的关系。

## 为什么需要它

AIGC 工作流中，文本不是直接变成图像，而是先被编码成模型可使用的条件。TA 需要理解 CLIP 的位置，才能解释为什么 Prompt 写法、关键词权重、参考图和模型版本会影响生成结果。

## 核心原理

CLIP 通常包含文本编码器和图像编码器，把文本描述和图像特征映射到同一语义空间。扩散模型常利用文本编码结果作为生成条件。

> 待核验：不同模型体系中的文本编码器并不完全相同，具体实现要按模型版本查证。

## 技术美术中的典型用途

- 解释 Prompt 为什么能影响生成图像。
- 分析关键词不生效、语义冲突或风格漂移。
- 与 [[Prompt Engineering]]、[[Negative Prompt]] 和 [[IP-Adapter]] 配合理解控制方式。

## Unity 中的相关场景

Unity 资产生成流程中，CLIP 不是直接落地到引擎的资产，但它影响图标、贴图参考和概念图生成的一致性。

## Unreal Engine 中的相关场景

Unreal 项目中使用 AIGC 做环境概念或 VFX 参考时，CLIP 相关的文本理解能力会影响批量结果的稳定性。

## 常见误区

1. 以为模型完全按自然语言理解 Prompt。
2. 把 CLIP 当成版权或质量审核工具。
3. 不同模型之间直接套同一套 Prompt 预期。

## 面试可能怎么问

### CLIP 在文生图里起什么作用？

回答要点：它把文本条件编码成模型可用的语义表示，让扩散模型在去噪过程中朝文本描述方向生成。

## 实践建议

用同一模型测试同义词、风格词、材质词和构图词的影响，记录哪些词稳定、哪些词容易冲突。

## 相关条目

- [[Diffusion Model]]
- [[Prompt Engineering]]
- [[Stable_Diffusion|Stable Diffusion]]

## 参考来源

- 待补充

