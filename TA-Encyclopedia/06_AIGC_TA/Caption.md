---
title: "Caption"
aliases:
  - 图像描述
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Dataset]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Caption

## 一句话定义

Caption 是训练或整理数据集时为图像编写的文字描述，用于告诉模型图像中有哪些内容和风格。

## 为什么需要它

LoRA 或风格数据集训练时，Caption 质量会直接影响模型学到什么。TA 需要制定 Caption 规范，避免模型把背景、水印、错误姿势或无关元素学成目标特征。

## 核心原理

Caption 把图像内容、角色、服装、风格、镜头、动作等信息转成文本标签或句子。训练时模型根据图文对应关系学习条件与视觉特征的关联。

> 待核验：不同训练框架对 Caption 格式、触发词和 tag 权重的处理不同。

## 技术美术中的典型用途

- LoRA 数据集整理。
- 角色、风格、图标数据标注。
- 建立可复用的数据规范。
- 与 [[Tagging]] 配合自动生成和人工修正。

## Unity 中的相关场景

如果为 Unity 项目训练图标或角色风格 LoRA，Caption 需要描述项目可控特征，而不是随意堆关键词。

## Unreal Engine 中的相关场景

Unreal 项目中的环境风格或 VFX 参考训练，也需要 Caption 区分场景元素、光照、构图和风格。

## 常见误区

1. Caption 只写风格，不写关键内容。
2. 把不想学习的背景和噪点也写入标签。
3. 自动标注后不人工清洗。

## 面试可能怎么问

### LoRA 数据集为什么要重视 Caption？

回答要点：Caption 决定模型如何把文本条件和图像特征对应起来，错误 Caption 会让模型学到错误关联。

## 实践建议

整理 20 张角色图，分别写“角色身份、服装、姿态、风格、需要忽略的背景”字段，再统一成训练 Caption。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Stable_Diffusion]] | Stable Diffusion 是常见生成模型生态；本条目可能关注其中某个节点、流程或落地规范。 |
| [[AIGC管线落地]] | 管线落地强调团队流程；单项工具条目强调具体输入、参数和限制。 |

## 相关条目

- [[Tagging]]
- [[LoRA 训练流程]]
- [[LoRA]]
- [[AIGC 资产审核规范]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
