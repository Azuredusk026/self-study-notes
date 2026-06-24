---
title: "Precision"
aliases:
  - Shader 精度
category: "Shader"
tags: [技术美术, Shader, Optimization]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Precision

## 定义与解释

Precision 是 Shader 中数值精度和数据格式的选择问题。它影响画面稳定性、性能、寄存器压力和移动端兼容性。

## 核心原理

Shader 计算可能使用 half、float、fixed 或平台对应的低/中/高精度类型。较低精度能降低带宽和寄存器压力，但会带来量化误差、溢出、Banding 或法线归一化问题。

精度选择要看数据语义：颜色、遮罩、UV、法线、世界位置、深度和时间累积需要不同范围和误差容忍度。移动端 GPU 对精度更敏感，桌面端有时会把类型提升或优化，不能只凭单个平台判断。

## 用途

- 在材质或 Shader 调试中定位与 Precision 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Mipmap]] | Mipmap 管采样级别；Precision 管数值表示。 |
| [[Texture Sampling]] | 采样得到的数据还要经过合适精度参与计算。 |

## 常见误区

1. 所有变量都用 float，忽略移动端成本。
2. 世界坐标或深度使用过低精度导致抖动。
3. 只看最终截图，不检查不同平台和 HDR/后处理链路。

## 相关条目

- [[HLSL]]：HLSL 中 half/float 等类型体现精度选择。
- [[GLSL]]：GLSL ES 有 lowp/mediump/highp 精度限定。
- [[Depth Buffer]]：深度精度直接影响 Z-Fighting 和屏幕效果。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
