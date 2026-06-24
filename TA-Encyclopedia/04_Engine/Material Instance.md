---
title: "Material Instance"
aliases:
  - 材质实例
category: "04_Engine"
tags: [技术美术, Unreal, Material]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Material Instance

## 定义与解释

Material Instance 是 Unreal 中基于父材质创建的参数化材质实例，用于复用 Shader 逻辑并覆盖贴图、颜色、数值和开关参数。

## 核心原理

父材质定义节点逻辑和可暴露参数，Material Instance 只保存参数覆盖。运行时或编辑器使用实例时，仍复用父材质的核心编译逻辑；Static 参数可能影响编译排列，普通标量/向量/纹理参数主要改变运行时常量或资源绑定。

它的价值在于规范和复用：TA 可以设计主材质和参数分组，让美术只调整安全范围内的参数。若静态开关过多或父材质过于庞大，实例体系也会变得难以维护。

## 用途

- 在引擎项目中定位与 Material Instance 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Editor]] | Material Editor 定义父材质逻辑；Material Instance 覆盖参数。 |
| [[MaterialPropertyBlock]] | MaterialPropertyBlock 是 Unity 的 per-renderer 参数覆盖机制。 |

## 常见误区

1. 每个资产复制父材质而不是使用实例。
2. 实例参数没有分组和命名规范。
3. 静态开关过多导致编译排列膨胀。

## 相关条目

- [[Material Editor]]：父材质逻辑在 Material Editor 中搭建。
- [[MaterialPropertyBlock]]：Unity 中类似需求常用 MaterialPropertyBlock 或材质实例处理。
- [[PBR]]：实例常覆盖 PBR 贴图和参数。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
