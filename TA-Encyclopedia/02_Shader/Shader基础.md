---
title: "Shader基础"
aliases: []
category: "02_Shader"
confidence: medium
tags: [shader, basics]
status: draft
created: 2026-06-24
updated: "2026-06-24"
---

# Shader基础

## 一句话定义
Shader 是运行在 GPU 上的程序，用于控制顶点处理、像素着色和计算任务。

## 为什么需要它

TA 需要理解 `Shader基础`，因为它会影响资源制作、引擎配置、画面表现、调试路径或团队协作边界。把它写成明确条目，可以减少口头经验传递，并让问题排查有稳定入口。

## 基础主题

- 顶点着色器
- 片元/像素着色器
- Uniform/常量缓冲
- 纹理采样
- 坐标空间

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

`Shader基础` 解决的核心问题是什么？

回答要点：先说明它在Shader 开发中处理哪类输入和输出，再结合一个项目场景说明为什么需要它。

### 问题 2

在 Unity 和 Unreal 中落地 `Shader基础` 时，TA 需要分别关注什么？

回答要点：比较两边的工具入口、资源规则、调试方式和平台限制，不要只背 API 名称。

### 问题 3

如果 `Shader基础` 相关效果或资产在项目中出问题，你会怎么排查？

回答要点：从资源输入、引擎配置、运行时状态、性能指标和最小复现场景逐层缩小范围。

## 实践建议

- 为 `Shader基础` 保留一个最小测试场景或示例资产，便于回归检查。
- 把关键参数、命名规则和导入设置写入团队规范，避免只存在个人经验里。
- 涉及具体版本、API 或第三方工具行为时，先标记 `待核验`，再登记到 [[91_Sources/source_registry|Source Registry]]。

## 相关条目

- [[02_Shader/README|02_Shader README]]
- [[技术美术百科总目录]]
- [[术语索引]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
