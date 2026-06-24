---
title: "AGENTS"
aliases: []
category: "Root"
confidence: medium
tags: [codex, instructions]
status: active
created: 2026-06-24
updated: 2026-06-24
---
# AGENTS.md

本仓库是一个面向中文技术美术工程师的 Obsidian + Markdown 技术美术百科库。

## 总目标

构建一个系统化、可检索、可持续扩充的技术美术中文百科全书。术语可以正常使用英文，例如 Shader、PBR、G-Buffer、Render Pass、LoRA、ControlNet、AssetBundle、Subpass。

## Codex 工作原则

1. 不允许随意大规模重写已有笔记。
2. 修改前必须先阅读相关目录的 README、模板和已有同主题条目。
3. 每次任务只处理一个明确主题或一个明确目录。
4. 新增条目必须使用 `90_Templates/条目模板.md`。
5. 所有新增内容必须保持中文工程师可读，不写空泛科普文。
6. 技术概念必须尽量包含：
   - 定义
   - 为什么需要它
   - 工作原理
   - 在技术美术中的用途
   - 常见误区
   - Unity / Unreal / DCC / AIGC 中的相关场景
   - 面试可能怎么问
   - 相关条目链接
7. 不确定的事实必须标记为 `待核验`，不要编造。
8. 涉及具体版本、API、工具行为、论文结论时，需要在 `91_Sources/source_registry.md` 中记录来源。
9. 保持 Obsidian 双链格式，例如 `[[PBR]]`、`[[G-Buffer]]`。
10. 文件名使用中文或英文均可，但同一主题不要重复建多个近义文件。
11. 修改后必须更新相关索引：
    - `00_Index/技术美术百科总目录.md`
    - `00_Index/术语索引.md`
    - 对应目录下的 `README.md`
12. 每次提交前必须运行 scripts 中的检查脚本。若脚本失败，必须说明原因并修复。

## 禁止行为

- 禁止生成没有工程价值的泛泛定义。
- 禁止把一篇笔记写成论文。
- 禁止无来源地断言最新工具版本、最新 API 行为。
- 禁止删除用户已有内容，除非任务明确要求。
- 禁止把英文术语强行翻译成生硬中文。
- 禁止把多个大主题塞进一个文件。
- 禁止制造重复条目，例如同时存在 `PBR.md`、`Physically Based Rendering.md`、`基于物理的渲染.md`，除非其中两个是重定向索引。