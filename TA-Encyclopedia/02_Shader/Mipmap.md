---
title: "Mipmap"
aliases: []
category: "02_Shader"
tags:
  - 技术美术
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---

# Mipmap

## 一句话定义

Mipmap 是后续需要扩充的技术美术相关主题。本页当前用于补全知识库双链，避免核心条目引用到不存在的页面。

## 为什么需要它

该主题已经在第一轮核心条目中被引用，说明它与渲染、Shader、引擎、资产生产或算法基础存在直接关系。

## 核心原理

- 输入：顶点属性、纹理、常量缓冲、材质参数、关键字和渲染状态。
- 处理过程：在顶点、片元、计算或材质图阶段执行采样、空间变换、分支、插值和混合。
- 输出：颜色、法线、深度、遮罩、材质属性或供后续 Pass 使用的中间结果。
- 所在层级：GPU / Shader / Material System。

## 技术美术中的典型用途

- 编写和维护可复用 Shader/Material Graph。
- 控制变体数量、采样次数和移动端精度。
- 为美术暴露稳定、可理解的材质参数。

## Unity 中的相关场景

常见于 ShaderLab/HLSL、Shader Graph、MaterialPropertyBlock、Keyword、SRP Batcher 和 URP/HDRP 自定义材质。

## Unreal Engine 中的相关场景

常见于 Material Editor、Material Function、Custom HLSL、Static Switch、Material Instance 和平台材质质量分级。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Graph]] | Material Graph 偏节点化编辑；本条目可能涉及更底层的代码、编译和采样细节。 |
| [[Texture Sampling]] | Texture Sampling 是常见操作；本条目可能覆盖更完整的 Shader 结构或控制策略。 |

## 常见误区

1. 只记概念名，不确认它在项目中的输入、输出和所在管线阶段。
2. 把引擎默认效果当成固定标准，忽略渲染管线、平台和项目配置差异。
3. 没有保留可复现的测试场景，导致问题只能靠截图或主观描述沟通。

## 面试可能怎么问

### 问题 1

`Mipmap` 解决的核心问题是什么？

回答要点：先说明它在Shader 开发中处理哪类输入和输出，再结合一个项目场景说明为什么需要它。

### 问题 2

在 Unity 和 Unreal 中落地 `Mipmap` 时，TA 需要分别关注什么？

回答要点：比较两边的工具入口、资源规则、调试方式和平台限制，不要只背 API 名称。

### 问题 3

如果 `Mipmap` 相关效果或资产在项目中出问题，你会怎么排查？

回答要点：从资源输入、引擎配置、运行时状态、性能指标和最小复现场景逐层缩小范围。

## 实践建议

- 为 `Mipmap` 保留一个最小测试场景或示例资产，便于回归检查。
- 把关键参数、命名规则和导入设置写入团队规范，避免只存在个人经验里。
- 涉及具体版本、API 或第三方工具行为时，先标记 `待核验`，再登记到 [[91_Sources/source_registry|Source Registry]]。

## 相关条目

- [[技术美术百科总目录]]
- [[待扩充条目]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
