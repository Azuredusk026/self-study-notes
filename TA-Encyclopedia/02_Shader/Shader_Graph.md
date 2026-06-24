---
title: "Shader_Graph"
aliases: []
category: "02_Shader"
confidence: medium
tags: [shader, node-graph]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# Shader Graph

## 定义与解释

Shader Graph 是 Unity 等引擎提供的节点化 Shader 创作工具。它让用户通过节点网络生成 Shader，而不是直接手写完整 HLSL。

## 核心原理

Shader Graph 的核心是把节点网络编译为目标渲染管线可用的 Shader。每个节点会生成对应代码或函数调用，黑板参数会映射为材质属性，Sub Graph 则提供复用逻辑。

它降低了创作门槛，但仍受 SRP、Pass、Keyword、采样次数、精度和平台限制约束。TA 需要设计节点规范、Sub Graph 复用方式和参数命名，避免项目中出现大量难维护的节点图。

## 用途

- 在材质或 Shader 调试中定位与 Shader_Graph 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Graph]] | Material Graph 是通用概念；Shader Graph 是 Unity 生态具体工具。 |
| [[HLSL]] | HLSL 是代码路径；Shader Graph 是节点生成路径。 |

## 常见误区

1. 认为节点化就不需要理解 Shader。
2. Sub Graph 无规范导致重复逻辑和隐藏成本。
3. Graph 参数命名随意，导致材质面板难以维护。

## 相关条目

- [[Material Graph]]：Shader Graph 是具体节点材质工具。
- [[HLSL]]：Shader Graph 可包含或生成 HLSL 逻辑。
- [[Keyword]]：Graph 中的开关可能生成 Keyword。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
