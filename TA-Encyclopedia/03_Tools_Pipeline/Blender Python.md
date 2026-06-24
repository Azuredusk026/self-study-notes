---
title: "Blender Python"
aliases: []
category: "03_Tools_Pipeline"
tags: [技术美术, Blender, Python, Pipeline]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Blender Python

## 定义与解释

Blender Python 是 Blender 提供的脚本和插件接口，用于自动化资产检查、批量处理、导出、命名整理和自定义 UI。

## 核心原理

Blender Python 的核心是通过 `bpy` 访问 Blender 内部数据块，例如 Object、Mesh、Material、Collection、Armature 和 Operator。TA 可以读取场景状态、修改属性、执行导出、生成报告或封装工具面板。

脚本设计要区分一次性批处理、交互式插件和团队管线工具。可靠工具需要处理选择状态、上下文依赖、撤销、安全写入、路径规范、版本兼容和错误报告，而不是只录制一段操作宏。

## 用途

- 把 Blender Python 纳入资产生产、检查、导出、导入或版本管理流程，减少人工操作和沟通成本。
- 把团队规范转成可执行规则、工具入口或自动化报告，让问题尽早暴露。
- 连接 DCC、引擎、版本库和 CI/CD，让美术资产从制作到落地有可追踪的状态。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Maya Python]] | 两者都是 DCC 脚本接口，但对象模型和命令系统不同。 |
| [[Unity Editor Tool]] | Blender Python 处理制作侧；Unity Editor Tool 处理引擎侧。 |

## 常见误区

1. 脚本依赖当前选择和 UI 上下文，批处理时失败。
2. 不输出明确错误文件和对象路径，导致美术无法修复。
3. 没有固定 Blender 版本和插件依赖。

## 相关条目

- [[Blender]]：Blender Python 运行在 Blender 环境内。
- [[自动化导出工具]]：导出工具可由 Blender Python 实现。
- [[资源检查工具]]：Blender 场景检查可作为资源检查的一环。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
