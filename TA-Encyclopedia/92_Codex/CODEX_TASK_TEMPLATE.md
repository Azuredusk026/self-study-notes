---
title: "CODEX_TASK_TEMPLATE"
aliases: []
category: "92_Codex"
confidence: medium
tags: [codex, template]
status: active
created: 2026-06-24
updated: 2026-06-24
---
# Codex Task Template

## 任务目标

请在本 Obsidian + Markdown + Git 仓库中完成以下知识库维护任务：

主题：

范围：

目标读者：中文技术美术工程师、TA 实习生、游戏图形学学习者。

## 必须阅读

开始修改前必须阅读：

- `AGENTS.md`
- `92_Codex/CODEX_STYLE_GUIDE.md`
- `90_Templates/条目模板.md`
- 对应目录下的 `README.md`
- 已有相关条目

## 输出要求

你需要完成：

1. 新增或扩充对应 Markdown 条目。
2. 使用 Obsidian 双链连接相关概念。
3. 更新对应目录 README。
4. 更新 `00_Index/技术美术百科总目录.md`。
5. 更新 `00_Index/术语索引.md`。
6. 如果涉及来源，更新 `91_Sources/source_registry.md`。
7. 运行检查脚本：
   - `python scripts/check_frontmatter.py`
   - `python scripts/check_links.py`
   - `python scripts/check_terms.py`
   - `python scripts/build_index.py`

## 写作要求

- 使用中文说明，英文术语正常保留。
- 内容要面向工程实践，不要写成泛科普。
- 每个核心概念必须说明“为什么需要它”和“TA 如何用它”。
- 面试题部分必须能直接用于技术美术面试准备。
- 不确定内容标记为 `待核验`。
- 不要删除用户已有内容。

## 验收标准

完成后请输出：

1. 修改文件列表。
2. 每个文件的修改摘要。
3. 新增了哪些 Obsidian 双链。
4. 是否运行检查脚本。
5. 是否存在待核验内容。
6. 建议下一步扩充主题。