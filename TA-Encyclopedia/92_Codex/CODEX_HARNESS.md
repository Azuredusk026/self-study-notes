---
title: "CODEX_HARNESS"
aliases: []
category: "92_Codex"
confidence: medium
tags: [codex, workflow]
status: active
created: 2026-06-24
updated: 2026-06-24
---

# CODEX_HARNESS

Codex 协作入口，用于规范自动化整理、检查和扩充笔记的方式。

## 默认任务

- 新增条目时使用 `90_Templates/条目模板.md`。
- 更新资料时同步维护 `91_Sources/source_registry.md`。
- 大批量修改后运行 `scripts/check_frontmatter.py` 和 `scripts/check_links.py`。

## 约束

- 不删除已有笔记，除非明确要求。
- 不把未经验证的资料写成确定结论。
- 中文为主，术语可保留英文。
