---
title: "PBR"
aliases: []
category: "01_Rendering"
confidence: medium
tags: [rendering, pbr, material]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# PBR

## 定义与解释

PBR（Physically Based Rendering）是一套以物理规律为约束的材质和光照工作流，用统一参数描述表面如何反射光。它的目标是让材质在不同灯光和环境中保持相对一致可信。

## 核心概念

- Albedo/Base Color
- Metallic
- Roughness/Smoothness
- Normal
- AO
- BRDF
- IBL

## 常见问题

- 贴图颜色空间错误
- 金属度和粗糙度通道打包错误
- 法线方向或切线空间不一致

## 核心原理

PBR 的核心是能量守恒、材质参数语义统一和 BRDF 驱动的光照响应。Base Color、Metallic、Roughness、Normal、AO、Emission 等参数不是独立调色项，而是共同决定漫反射、镜面反射和环境光响应。

工程上，PBR 依赖正确的颜色空间、贴图通道打包、法线空间、IBL、曝光和 Tone Mapping。Unity、Unreal 和 DCC 软件可能使用 Roughness/Smoothness 命名差异或通道约定差异，TA 需要建立项目级材质规范和校验流程。

## 用途

- 在渲染调试中定位与 PBR 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[BRDF]] | BRDF 是反射函数；PBR 是围绕物理材质和光照的一套工作流。 |
| [[NPR]] | PBR 追求物理一致性；NPR 追求风格表达。 |

## 常见误区

1. 把 PBR 当作固定贴图套餐，不理解参数语义。
2. Base Color、Metallic、Roughness 使用错误颜色空间或通道。
3. 只在单一灯光下调材质，换环境后表现崩坏。

## 相关条目

- [[BRDF]]：PBR 光照通常由 BRDF 组织。
- [[Roughness]]：PBR 关键材质参数。
- [[Metallic]]：PBR 金属度工作流核心参数。
- [[IBL]]：PBR 常依赖 IBL 提供环境光。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
