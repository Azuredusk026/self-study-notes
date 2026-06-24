---
title: "HybridCLR"
aliases: []
category: "04_Engine"
confidence: medium
tags: [unity, hot-update, hybridclr]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# HybridCLR

## 定义与解释

HybridCLR 是 Unity 生态中用于 C# 热更新和 AOT/解释执行补充的方案之一，常用于运行时更新逻辑代码。

## 核心原理

HybridCLR 的核心是让部分 C# 程序集在运行时加载，并补充 IL2CPP AOT 环境下泛型、元数据和热更新代码执行能力。它涉及程序集拆分、元数据补充、打包、版本管理和平台构建流程。

TA 通常不直接编写热更底层，但需要理解它对资源包、工具、构建和版本流程的影响。涉及具体版本、平台限制和 API 行为时必须核验，不能把热更能力写成不受约束的通用结论。

## 用途

- 在引擎项目中定位与 HybridCLR 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[YooAsset]] | YooAsset 管资源更新；HybridCLR 管代码热更新。 |
| [[AssetBundle]] | AssetBundle 管资源包；HybridCLR 涉及程序集和元数据加载。 |

## 常见误区

1. 把代码热更和资源热更混为一谈。
2. 未核验平台和版本限制就设计流程。
3. 热更程序集、资源版本和服务器配置没有绑定。

## 相关条目

- [[Unity]]：HybridCLR 运行在 Unity 项目生态中。
- [[YooAsset]]：热更代码和热更资源常在版本流程上配合。
- [[CI_CD for Game Assets]]：热更构建需要自动化检查和产物管理。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
