---
title: "Unity"
aliases: []
category: "04_Engine"
confidence: medium
tags: [engine, unity]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# Unity

## 定义与解释

Unity 是跨平台实时 3D 引擎，TA 工作常围绕资源导入、渲染管线、编辑器工具、性能分析、打包和平台适配展开。

## 核心原理

Unity 的核心是把资产数据库、场景、Prefab、组件、脚本、渲染管线、构建系统和运行时资源管理组织成一个编辑器驱动的工作流。外部资产进入 Unity 后，会被 Importer 转换为引擎资源，再由场景和运行时系统使用。

TA 需要理解 Unity 的编辑器态和运行态边界：导入设置、材质、Shader、Addressables、Profiler、Frame Debugger、SRP 和构建平台会共同决定最终表现。很多问题不是单个资产错，而是资源设置、管线配置和平台限制共同作用。

## 用途

- 在引擎项目中定位与 Unity 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Unreal_Engine]] | 两者都是实时引擎，但资源系统、材质系统和工具生态不同。 |
| [[SRP]] | SRP 是 Unity 渲染管线框架，不等同于 Unity 整体。 |

## 常见误区

1. 只看编辑器效果，不验证目标平台构建。
2. 把资源导入设置和运行时问题割裂处理。
3. 升级 Unity 或 SRP 版本前不评估管线和工具兼容。

## 相关条目

- [[URP]]：Unity 常用的轻量 SRP 管线。
- [[HDRP]]：Unity 高端渲染管线。
- [[Addressables]]：Unity 资源管理框架。
- [[Unity_TA管线]]：Unity 项目需要 TA 管线规则支撑。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
