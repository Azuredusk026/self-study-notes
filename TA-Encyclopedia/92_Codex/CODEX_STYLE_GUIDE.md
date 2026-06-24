---
title: "CODEX_STYLE_GUIDE"
aliases: []
category: "92_Codex"
confidence: medium
tags: [codex, style-guide]
status: active
created: 2026-06-24
updated: 2026-06-24
---
# CODEX_STYLE_GUIDE

## 语言风格

本知识库面向中文技术美术工程师。写作应当清晰、直接、工程化。

推荐写法：

- “G-Buffer 用来在 Deferred Rendering 中保存几何阶段输出的数据。”
- “它保存的法线、深度、材质参数会直接影响后处理、描边和光照结果。”
- “写用途时要说明它在 Shader、材质、资产规范、引擎工具或性能排查中的具体作用。”

避免写法：

- “它很有用。”
- “它在很多项目中都会出现。”
- “它能提升效果。”

## 术语规则

英文术语可以直接使用：

- Shader
- Render Pass
- Subpass
- G-Buffer
- PBR
- NPR
- Toon Shading
- LoRA
- ControlNet
- Agent
- AssetBundle
- Addressables
- Blueprint
- Material Graph

第一次出现时可以写成：

- `G-Buffer（Geometry Buffer）`
- `PBR（Physically Based Rendering）`
- `NPR（Non-Photorealistic Rendering）`

## 条目深度

每个核心条目至少包含：

1. 定义与解释
2. 核心原理
3. 用途
4. 与其他概念的区别
5. 常见误区
6. 相关条目
7. 参考来源

“定义与解释”不能只写一句话，应说明概念边界、上下文和容易混淆的点。“核心原理”应尽量详细，但必须按条目自身机制组织，不要套用固定的输入/处理/输出模板。Shader 条目可以写执行阶段和采样逻辑，渲染条目可以写管线顺序和缓冲关系，工具链条目可以写规则流转和自动化边界，数学条目可以写推导关系和数值约束。

## 内容可信度

使用 frontmatter 的 `confidence` 字段：

- `high`：基础概念、确定性强、无需版本依赖。
- `medium`：一般技术解释，可能有实现差异。
- `low`：工具版本、最新 API、具体厂商实现、未核验内容。

## Obsidian 链接规则

优先使用双链：

- `[[PBR]]`
- `[[Shader基础]]`
- `[[Deferred_Rendering]]`

不要滥用双链。只有真正相关的概念才链接。

相关条目必须体现真实关系，不使用总目录、术语索引、README 或空链接充数。推荐写成 `- [[PBR]]：共享材质参数语义，常和 Roughness、Metallic 一起解释。`

## 文件命名规则

- 核心英文术语可以使用英文文件名，例如 `PBR.md`、`G-Buffer.md`。
- 中文主题可以使用中文文件名，例如 `贴图规范.md`。
- 不要为同一主题建立多个重复文件。
