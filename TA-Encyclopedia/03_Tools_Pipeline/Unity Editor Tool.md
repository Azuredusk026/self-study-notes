---
title: "Unity Editor Tool"
aliases:
  - Unity 编辑器工具
category: "03_Tools_Pipeline"
tags: [技术美术, Unity, Tool, Pipeline]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Unity Editor Tool

## 定义与解释

Unity Editor Tool 是运行在 Unity 编辑器中的自定义工具，用于资产检查、批处理、导入规则、关卡辅助、报告生成和流程自动化。

## 核心原理

Unity 编辑器工具通常通过 EditorWindow、MenuItem、AssetPostprocessor、ScriptedImporter、PrefabUtility、Addressables API 等接口操作项目资产和编辑器状态。它的核心是把重复编辑器操作变成可执行流程。

工具设计要区分交互式工具、导入钩子和 CI 命令行工具。可靠工具应避免隐式选择状态，支持批量路径、进度、日志、撤销、安全写入和错误定位，并考虑 Unity 版本和包依赖。

## 用途

- 把 Unity Editor Tool 纳入资产生产、检查、导出、导入或版本管理流程，减少人工操作和沟通成本。
- 把团队规范转成可执行规则、工具入口或自动化报告，让问题尽早暴露。
- 连接 DCC、引擎、版本库和 CI/CD，让美术资产从制作到落地有可追踪的状态。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Maya Python]] | Maya Python 处理 DCC 源文件；Unity Editor Tool 处理引擎内资产。 |
| [[自动化导出工具]] | 导出工具多在 DCC 侧；Unity Editor Tool 多在导入和项目整理侧。 |

## 常见误区

1. 工具依赖当前选中对象，批处理和 CI 不可用。
2. 自动修改资产前没有预览和日志。
3. 没有区分错误、警告和建议，影响团队接受度。

## 相关条目

- [[Unity_TA管线]]：Unity Editor Tool 是 Unity TA 管线的执行入口。
- [[资源检查工具]]：Unity 中的检查工具可用 Editor Tool 实现。
- [[Addressables]]：资源打包和依赖检查常与 Addressables 相关。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
