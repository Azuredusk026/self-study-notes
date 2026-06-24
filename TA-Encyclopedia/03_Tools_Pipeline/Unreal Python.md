---
title: "Unreal Python"
aliases: []
category: "03_Tools_Pipeline"
tags: [技术美术, Unreal, Python, Pipeline]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Unreal Python

## 一句话定义

Unreal Python 是 Unreal Editor 中用于自动化内容处理、批量操作和管线工具开发的脚本接口。

## 为什么需要它

Unreal 项目内容量大，手动改材质实例、导入设置、目录、LOD 或命名容易出错。Python 可以把这些操作变成可复用脚本或工具。

## 核心原理

Unreal Python 运行在编辑器环境，通过 Unreal API 访问资产、关卡对象、导入任务、材质实例和编辑器功能。

> 待核验：Unreal Python API 覆盖范围和函数名称会随版本变化，需要查对应版本文档。

## 技术美术中的典型用途

- 批量导入和重导入资产。
- 修改材质实例参数。
- 扫描 Content 目录并生成报告。
- 批量设置 LOD、碰撞、贴图组。

## Unity 中的相关场景

Unity 对应方向通常是 C# Editor Tool 和 AssetPostprocessor。

## Unreal Engine 中的相关场景

常与 Editor Utility Widget、Data Validation 和命令行自动化配合，适合批处理和 CI 前检查。

## 常见误区

1. 在运行时逻辑里期待使用 Editor Python。
2. 批量修改资产不保存日志。
3. 没有先 dry-run，直接写入大量资产。

## 面试可能怎么问

### Unreal Python 适合做哪些 TA 工具？

回答要点：适合内容批处理、导入导出、材质实例修改、资产检查、报告生成和编辑器自动化。

## 实践建议

写一个脚本扫描所有 Texture，输出尺寸、压缩设置、LOD Group 和引用数量。

## 相关条目

- [[Editor Utility Widget]]
- [[Unreal_TA管线]]
- [[资源检查工具]]
- [[Texture Compression]]

## 参考来源

- 待补充

