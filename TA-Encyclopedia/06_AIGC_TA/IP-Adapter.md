---
title: "IP-Adapter"
aliases: []
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Reference]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# IP-Adapter

## 定义与解释

IP-Adapter 是在扩散生成中引入图像参考条件的适配器方案，用于把参考图的语义、风格或角色特征传递给生成过程。

## 核心原理

IP-Adapter 的核心是把参考图编码为图像条件，并在去噪过程中影响生成结果。它通常比单纯 Prompt 更适合保持角色、物体、风格或构图的视觉相似性。

TA 需要区分它与 ControlNet 的职责：IP-Adapter 偏图像语义和风格参考，ControlNet 偏结构约束。使用时要记录参考图来源、权重、模型版本和是否允许进入正式资产流程。

## 用途

- 在 AIGC 资产流程中定位与 IP-Adapter 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[ControlNet]] | IP-Adapter 偏参考图语义/风格，ControlNet 偏姿态/边缘/深度结构。 |
| [[Prompt Engineering]] | Prompt 是文本条件，IP-Adapter 是图像条件。 |

## 常见误区

1. 用未经授权参考图保持角色相似性。
2. 权重过高导致结果过拟合参考图。
3. 不记录参考图和适配器版本。

## 相关条目

- [[ControlNet]]：ControlNet 偏结构控制。
- [[Img2Img]]：Img2Img 也使用参考图但机制不同。
- [[ComfyUI]]：IP-Adapter 常通过节点接入工作流。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
