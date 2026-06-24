---
title: "YooAsset"
aliases: []
category: "04_Engine"
confidence: medium
tags: [unity, yooasset, resource-management]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# YooAsset

## 定义与解释

YooAsset 是 Unity 生态中的资源管理和热更新框架，用于组织资源包、清单、下载、缓存和运行时加载。

## 核心原理

YooAsset 的核心是围绕 Package、Manifest、Bundle、版本和加载句柄管理资源生命周期。构建阶段生成资源包和清单，运行时根据版本信息下载、缓存、加载和卸载资源。

TA 需要关注资源分组、版本策略、依赖冗余、首包/热更边界、远程服务器、缓存清理和构建报告。它和 Addressables 一样需要管线规则支撑，不能只在代码层接入。

## 用途

- 在引擎项目中定位与 YooAsset 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Addressables]] | 两者都做资源管理，但 API、构建流程和生态不同。 |
| [[HybridCLR]] | YooAsset 管资源热更；HybridCLR 管代码热更。 |

## 常见误区

1. 没有明确首包和热更资源边界。
2. 只看加载 API，不分析依赖重复和下载体积。
3. 资源版本和代码版本没有绑定。

## 相关条目

- [[Addressables]]：Unity 官方地址化资源管理框架。
- [[AssetBundle]]：资源包底层概念与 YooAsset 流程相关。
- [[HybridCLR]]：资源热更常与代码热更流程配合。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
