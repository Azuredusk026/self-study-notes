---
title: "Prompt Engineering"
aliases:
  - 提示词工程
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Prompt]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Prompt Engineering

## 定义与解释

Prompt Engineering 是为生成模型设计、组织、测试和记录文本提示的过程，用来控制主体、风格、构图、材质、质量和约束。

## 核心原理

Prompt 的核心是把生成意图转成模型能响应的条件文本。有效 Prompt 需要明确主体、属性、风格、镜头、材质、排除项和权重，并通过固定 Seed、Sampler 和模型版本进行对比测试。

TA 需要把 Prompt 当作可版本化的生产参数，而不是临时咒语。用于项目时应建立 Prompt 模板、变量位、命名规则和审核记录，方便复现和团队共享。

## 用途

- 在 AIGC 资产流程中定位与 Prompt Engineering 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Caption]] | Prompt 是生成指令；Caption 是图像或数据描述。 |
| [[ControlNet]] | Prompt 控制语义和风格，ControlNet 控制结构。 |

## 常见误区

1. 把 Prompt 当不可解释玄学，不记录变量。
2. 比较 Prompt 时同时改变模型、Seed 和 Sampler。
3. 使用未经审核的风格或角色描述生成正式资产。

## 相关条目

- [[Negative Prompt]]：负向提示是 Prompt 策略的一部分。
- [[CFG Scale]]：CFG 控制提示条件强度。
- [[CLIP]]：文本提示通常通过 CLIP 类编码器进入模型。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
