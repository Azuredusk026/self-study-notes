---
title: "CFG Scale"
aliases:
  - Classifier-Free Guidance Scale
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Sampling]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# CFG Scale

## 一句话定义

CFG Scale 是控制生成过程对文本条件跟随强度的参数。

## 为什么需要它

CFG 太低时结果可能不听 Prompt；太高时可能出现过锐、过饱和、结构异常或风格僵硬。TA 在搭建批量生成流程时，需要把它当成可记录、可对比、可复现的参数。

## 核心原理

CFG 通过调整条件预测和无条件预测之间的差异，影响模型朝 Prompt 描述靠近的程度。不同模型和采样器的适用范围不完全一致。

> 待核验：具体推荐范围必须按模型、采样器和工作流验证，不应写成固定结论。

## 技术美术中的典型用途

- 控制图标是否严格跟随元素和形状描述。
- 调整角色图对服装、颜色、构图的服从程度。
- 在批量生成中保持参数可复现。

## Unity 中的相关场景

Unity 资产导入前，CFG 影响生成图是否符合图标、贴图、UI 或道具规范，间接影响后处理和人工修图成本。

## Unreal Engine 中的相关场景

用于 VFX、环境概念或材质参考时，CFG 会影响概念图是否贴合项目描述和镜头需求。

## 常见误区

1. 把 CFG 当成“质量”参数。
2. 不同模型直接套同一个 CFG。
3. 只调 CFG，不调 Prompt、Seed、Sampler 和参考控制。

## 面试可能怎么问

### CFG Scale 调大一定更好吗？

回答要点：不一定。它提高对 Prompt 的跟随强度，但过高可能带来伪影、过饱和或结构异常。

## 实践建议

固定 Prompt、Seed、Sampler，只改变 CFG，生成一组对比图并记录质量变化。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Stable_Diffusion]] | Stable Diffusion 是常见生成模型生态；本条目可能关注其中某个节点、流程或落地规范。 |
| [[AIGC管线落地]] | 管线落地强调团队流程；单项工具条目强调具体输入、参数和限制。 |

## 相关条目

- [[Prompt Engineering]]
- [[Seed]]
- [[Sampler]]
- [[Stable_Diffusion|Stable Diffusion]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
