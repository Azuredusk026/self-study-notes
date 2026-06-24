---
title: "Material Editor"
aliases:
  - Unreal Material Editor
category: "04_Engine"
tags: [技术美术, Unreal, Material]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Material Editor

## 一句话定义

Material Editor 是 Unreal 中用节点方式创建材质和 Shader 逻辑的编辑器。

## 为什么需要它

Unreal TA 大量工作发生在材质系统里：PBR 材质、角色 Shader、后处理材质、VFX 材质、Material Function 和参数暴露。Material Editor 是连接美术表现和引擎渲染的核心工具。

## 核心原理

材质节点最终会编译为平台 Shader。材质域、Blend Mode、Shading Model、Static Switch 和参数类型决定材质参与哪些渲染路径和生成多少变体。

## 技术美术中的典型用途

- 角色、场景和特效材质。
- Material Function 复用。
- Post Process Material。
- 材质性能分析和 Shader Complexity 调试。

## Unity 中的相关场景

Unity 中相近工具是 Shader Graph 和手写 HLSL/ShaderLab。两者都需要关注节点复杂度和变体数量。

## Unreal Engine 中的相关场景

TA 需要管理材质参数、实例、函数库、贴图通道、材质域和平台质量开关。

## 常见误区

1. 节点能连出来就认为性能可接受。
2. 所有功能都做成 Static Switch，导致 permutation 增长。
3. 不把通用逻辑沉淀成 Material Function。

## 面试可能怎么问

### Unreal Material Editor 中 Static Switch 有什么风险？

回答要点：Static Switch 会参与编译变体，过多组合可能增加编译时间、包体和运行时管理成本。

## 实践建议

做一个可复用角色材质函数库：基础 PBR、Rim、Dissolve、Hit Flash 和 Mask 通道解析。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Unity]] | Unity 是引擎平台；本条目可能是其中某个系统或工作流。 |
| [[Unreal_Engine]] | Unreal 是引擎平台；本条目可能与其对应系统形成实现差异。 |

## 相关条目

- [[Material Instance]]
- [[Material Graph]]
- [[Shader Variant]]
- [[Unreal_Engine|Unreal Engine]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
