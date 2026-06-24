---
title: "Blueprint"
aliases:
  - 蓝图
category: "04_Engine"
tags: [技术美术, Unreal, Tool]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Blueprint

## 定义与解释

Blueprint 是 Unreal 的可视化脚本系统，用节点图组织 Gameplay、编辑器逻辑、工具流程和资源行为。

## 核心原理

Blueprint 的机制是把节点图编译成 Unreal 可执行的脚本逻辑，并与 Actor、Component、事件、变量和函数系统结合。它既可以驱动运行时对象，也可以配合编辑器工具处理内容生产。

TA 需要区分 Blueprint 适合表达的工具和表现逻辑，以及应交给 C++ 或材质/Niagara 的部分。节点图过度复杂会带来维护困难、运行时开销和引用耦合，参数命名和资产模板也需要规范。

## 用途

- 在引擎项目中定位与 Blueprint 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Editor]] | Material Editor 描述材质计算；Blueprint 描述对象和逻辑流程。 |
| [[Unreal Python]] | Blueprint 适合交互式工具和逻辑；Unreal Python 更适合批处理和自动化。 |

## 常见误区

1. 把所有逻辑都堆在 Blueprint 中，缺少模块边界。
2. 忽略 Tick、动态绑定和大量节点带来的运行时成本。
3. 工具 Blueprint 没有权限、路径和错误处理约束。

## 相关条目

- [[Unreal_Engine]]：Blueprint 是 Unreal 核心工具系统。
- [[Editor Utility Widget]]：编辑器工具可用 Blueprint 体系构建。
- [[Niagara]]：Blueprint 常与 Niagara 参数和事件联动。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
