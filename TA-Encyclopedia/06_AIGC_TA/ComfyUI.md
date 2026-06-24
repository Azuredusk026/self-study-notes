---
title: "ComfyUI"
aliases: []
category: "06_AIGC_TA"
confidence: medium
tags: [aigc, comfyui, workflow]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# ComfyUI

## 定义与解释

ComfyUI 是用节点图组织 Stable Diffusion 等 AIGC 工作流的工具，适合构建可复用、可追踪、可参数化的生成流程。

## 核心原理

ComfyUI 的核心是显式节点图。模型加载、文本编码、采样、VAE 解码、ControlNet、IP-Adapter、LoRA、放大和保存都由节点连接表达，工作流本身可以保存和复用。

TA 使用 ComfyUI 时应把节点图当作管线资产管理：固定模型版本、输入输出路径、命名规则、参数组、审核字段和示例结果。节点图越复杂，越需要注释、分组和版本控制。

## 用途

- 在 AIGC 资产流程中定位与 ComfyUI 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Agent工作流]] | ComfyUI 组织图像生成节点；Agent 工作流组织任务和工具调用。 |
| [[Prompt Engineering]] | Prompt 是文本策略；ComfyUI 是执行工作流。 |

## 常见误区

1. 只保存生成图，不保存工作流和模型版本。
2. 节点图缺少注释，团队无法复用。
3. 临时路径和本地模型依赖写死。

## 相关条目

- [[Stable_Diffusion]]：ComfyUI 常承载 Stable Diffusion 工作流。
- [[ControlNet]]：ControlNet 可作为节点接入约束。
- [[AIGC管线落地]]：节点图需要纳入团队管线。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
