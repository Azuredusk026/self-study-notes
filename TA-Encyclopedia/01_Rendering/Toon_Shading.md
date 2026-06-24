---
title: "Toon_Shading"
aliases: []
category: "01_Rendering"
confidence: medium
tags: [rendering, toon-shading, npr]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# Toon Shading

## 定义与解释

Toon Shading 是用阶梯化光照、色带、描边和风格化阴影模拟卡通或赛璐璐观感的渲染方法。它属于 NPR 的常见方向。

## 核心原理

Toon Shading 通常不使用连续 Lambert 或 PBR 光照，而是把 NdotL、半角高光、阴影或 Ramp 贴图量化成有限层级。描边可以通过法线外扩、反向 Hull、深度/法线边缘检测或 Stencil 组合实现。

核心不是单个 Shader 技巧，而是风格规则统一。角色、场景、阴影、后处理和灯光都需要遵循同一套层级、色带和边线规范。TA 需要控制美术参数暴露方式，避免每个材质单独调出不同风格。

## 用途

- 在渲染调试中定位与 Toon_Shading 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[PBR]] | PBR 强调物理一致性；Toon Shading 强调风格化层级。 |
| [[NPR]] | NPR 是大类；Toon Shading 是其中一种常见方案。 |

## 常见误区

1. 只做光照二值化就认为完成卡通渲染。
2. 角色和场景使用不同 Ramp 规则导致风格割裂。
3. 描边方案不考虑距离、FOV、模型厚度和平台性能。

## 相关条目

- [[NPR]]：Toon Shading 是 NPR 的具体表现方向。
- [[Lambert]]：Toon 常对漫反射项进行阶梯化。
- [[Stencil Buffer]]：部分描边方案会使用模板控制。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
