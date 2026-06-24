---
title: "ControlNet"
aliases: []
category: "06_AIGC_TA"
confidence: medium
tags: [aigc, controlnet]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# ControlNet

## 定义与解释

ControlNet 是给扩散模型增加结构控制条件的技术，常用姿态、深度、边缘、线稿、法线或分割图约束生成结果。

## 核心原理

ControlNet 的机制是在去噪过程中注入额外条件分支，让模型在遵循文本的同时参考结构图。不同预处理器会把参考图转换成边缘、深度、OpenPose、Canny 等控制信号。

它适合控制构图和形体，但不会自动保证材质、版权或资产可用性。TA 需要记录预处理器、权重、控制起止步数和参考图来源，并检查控制过强导致的僵硬或过拟合。

## 用途

- 在 AIGC 资产流程中定位与 ControlNet 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[IP-Adapter]] | ControlNet 偏结构控制；IP-Adapter 偏图像语义和风格参考。 |
| [[Prompt Engineering]] | Prompt 提供文本意图，ControlNet 提供结构约束。 |

## 常见误区

1. 把低质量控制图当作精确设计稿。
2. 控制权重过高导致结果僵硬。
3. 不记录预处理器和参考图来源。

## 相关条目

- [[Stable_Diffusion]]：ControlNet 扩展 Stable Diffusion 的条件控制。
- [[Img2Img]]：两者都可利用参考图，但控制方式不同。
- [[ComfyUI]]：ComfyUI 常用节点接入 ControlNet。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
