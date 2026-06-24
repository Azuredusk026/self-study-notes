---
title: "Editor Utility Widget"
aliases:
  - EUW
category: "04_Engine"
tags: [技术美术, Unreal, Tool]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Editor Utility Widget

## 一句话定义

Editor Utility Widget 是 Unreal 中用 UMG 和蓝图创建编辑器工具界面的方式。

## 为什么需要它

TA 需要把批量重命名、资源检查、材质替换、关卡整理、导入设置修正等流程做成美术可用工具。EUW 能快速做出编辑器内工具面板。

## 核心原理

EUW 运行在编辑器环境，可通过蓝图调用编辑器功能、访问选中资产或关卡对象，并提供可交互 UI。

> 待核验：EUW 可调用的 API 和权限随 Unreal 版本变化，复杂自动化需查官方文档。

## 技术美术中的典型用途

- 批量重命名和整理资产。
- 批量修改材质实例参数。
- 关卡对象检查。
- 一键生成报告或执行规范修复。

## Unity 中的相关场景

Unity 中对应方向是 [[Unity Editor Tool]]、EditorWindow 和自定义 Inspector。

## Unreal Engine 中的相关场景

EUW 常与 Content Browser、Selected Actors、Data Validation 和 Python 工具配合。

## 常见误区

1. 工具没有预览和确认，直接批量修改。
2. 没有错误报告和日志。
3. 蓝图工具越写越大，缺少模块化。

## 面试可能怎么问

### Unreal TA 如何给美术做编辑器工具？

回答要点：可用 Editor Utility Widget 或 Python，把批处理和检查流程做成可交互工具，并输出报告和可回滚操作。

## 实践建议

做一个批量材质实例参数修改工具，支持选择资产、预览变更和导出日志。

## 相关条目

- [[Blueprint]]
- [[Unreal Python]]
- [[资源检查工具]]
- [[Unreal_TA管线]]

## 参考来源

- 待补充

