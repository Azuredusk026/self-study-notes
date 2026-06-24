---
title: "Prompt Engineering"
aliases:
  - 提示词工程
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Prompt]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Prompt Engineering

## 一句话定义

Prompt Engineering 是通过结构化描述任务、风格、内容、限制和输出要求来控制生成结果的方法。

## 为什么需要它

在 AIGC TA 工作里，Prompt 不是一句“好看一点”。它要服务生产目标：角色设定、道具风格、材质类型、镜头、颜色、分辨率、禁用元素、批量一致性和后续导入规范。

## 核心原理

Prompt 把人的意图转成模型可利用的条件信号。工程上更关注可复用模板、变量槽位、负向约束、Seed 记录和结果评估，而不是单次碰运气。

## 技术美术中的典型用途

- 角色立绘、图标、道具和场景概念生成。
- 批量生成统一风格参考图。
- 与 [[Negative Prompt]]、[[CFG Scale]]、[[Seed]] 配合做可控迭代。
- 作为 [[Agent工作流]] 中的自动化生成参数。

## Unity 中的相关场景

Unity 项目中可为图标、贴图参考、UI 草图建立 Prompt 模板，并要求输出尺寸、透明背景、命名和导入规则。

## Unreal Engine 中的相关场景

Unreal 项目中可用于环境概念、材质参考、VFX 方向图和宣传资产草案，但最终落地仍需符合引擎材质和资产规范。

## 常见误区

1. 把 Prompt 当玄学词堆，不记录版本、Seed 和模型。
2. 只描述风格，不描述生产限制。
3. 不维护负向词和失败案例库。

## 面试可能怎么问

### Prompt 在 AIGC 管线里怎样工程化？

回答要点：模板化、参数化、记录模型和 Seed、建立质量标准、沉淀失败案例，并与后续审核和导入流程连接。

## 实践建议

为“游戏技能图标”设计 Prompt 模板，包含职业、元素、形状、颜色、背景、禁用项和输出尺寸。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Stable_Diffusion]] | Stable Diffusion 是常见生成模型生态；本条目可能关注其中某个节点、流程或落地规范。 |
| [[AIGC管线落地]] | 管线落地强调团队流程；单项工具条目强调具体输入、参数和限制。 |

## 相关条目

- [[Negative Prompt]]
- [[CFG Scale]]
- [[Seed]]
- [[ComfyUI]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
