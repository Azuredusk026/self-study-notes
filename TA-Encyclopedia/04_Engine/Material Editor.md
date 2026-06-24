---
title: "Material Editor"
aliases:
  - Unreal Material Editor
category: "04_Engine"
tags: [技术美术, Unreal, Material]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Material Editor

## 定义与解释

Material Editor 是 Unreal 中用于节点化编辑材质的工具，负责组织纹理采样、参数、函数、数学计算和材质输出。

## 核心原理

Material Editor 的核心是节点图到 Shader 的编译映射。节点连接形成材质数据流，参数暴露给 Material Instance，Static Switch 等选项可能生成不同变体。

TA 需要用它建立主材质、材质函数和参数规范，而不是让每个资产复制一份复杂节点图。采样次数、静态开关、材质域、Blend Mode、Shading Model 和平台质量等级都会影响结果和性能。

## 用途

- 在引擎项目中定位与 Material Editor 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Graph]] | Material Graph 是通用节点材质概念；Material Editor 是 Unreal 具体工具。 |
| [[Blueprint]] | Blueprint 管对象逻辑；Material Editor 管材质着色逻辑。 |

## 常见误区

1. 每个资产都复制完整材质图。
2. 参数命名和分组混乱，实例难以使用。
3. Static Switch 过多导致 Shader 编译和变体压力。

## 相关条目

- [[Material Instance]]：实例复用 Material Editor 中的父材质逻辑。
- [[Post Process Material]]：后处理材质也在材质系统中编辑。
- [[PBR]]：材质输出常服务 PBR 参数。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
