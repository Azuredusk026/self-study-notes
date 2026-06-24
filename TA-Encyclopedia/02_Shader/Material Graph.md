---
title: "Material Graph"
aliases:
  - 材质图
category: "02_Shader"
tags: [技术美术, Shader, Material]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Material Graph

## 一句话定义

Material Graph 是用节点方式组织材质计算逻辑的图形化 Shader 表达方式。

## 为什么需要它

很多项目让美术和 TA 通过节点搭建材质，而不是直接手写 Shader。Material Graph 能提高可视化和复用性，但也容易隐藏性能成本。

## 核心原理

节点图最终会被转换或编译为 Shader 代码。每个采样、数学节点、分支和静态开关都可能影响指令数、采样数和变体数量。

## 技术美术中的典型用途

- PBR、Toon、VFX 材质。
- 材质函数库。
- 参数暴露和实例化。
- 性能调试和节点重构。

## Unity 中的相关场景

Unity 中对应工具是 Shader Graph。

## Unreal Engine 中的相关场景

Unreal 的 Material Editor 就是典型 Material Graph 工作流。

## 常见误区

1. 节点图越直观就越便宜。
2. 复杂逻辑没有封装成函数或子图。
3. 不检查最终 Shader 变体和采样次数。

## 面试可能怎么问

### Material Graph 和手写 Shader 怎么取舍？

回答要点：节点图更适合可视化、快速迭代和美术协作；手写 Shader 更适合底层控制、复杂优化和特殊管线需求。

## 实践建议

把一个复杂材质拆成 Base、Mask、Detail、VFX 四个函数或子图，减少重复连线。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Graph]] | Material Graph 偏节点化编辑；本条目可能涉及更底层的代码、编译和采样细节。 |
| [[Texture Sampling]] | Texture Sampling 是常见操作；本条目可能覆盖更完整的 Shader 结构或控制策略。 |

## 相关条目

- [[Material Editor]]
- [[Shader_Graph|Shader Graph]]
- [[Shader Variant]]
- [[Texture Sampling]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
