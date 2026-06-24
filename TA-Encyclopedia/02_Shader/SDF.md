---
title: "SDF"
aliases:
  - Signed Distance Field
  - 有符号距离场
category: "Shader"
tags: [技术美术, Shader, Math, VFX]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# SDF

## 定义与解释

SDF（Signed Distance Field）是存储到最近边界有符号距离的数据表示。它常用于字体、描边、软边遮罩、体积近似、2D/3D 特效和程序化形状。

## 核心原理

SDF 的核心是距离值：边界处为零，一侧为正，另一侧为负。Shader 可以通过阈值、smoothstep、梯度和距离运算生成清晰边缘、可调粗细、软过渡或布尔组合。

SDF 的质量取决于距离场分辨率、生成范围、归一化方式和采样过滤。字体和图标 SDF 适合在缩放下保持边缘质量，但复杂形状、尖角和过小范围会产生失真。TA 需要确认 SDF 的单位语义和 Mip 策略。

## 用途

- 在材质或 Shader 调试中定位与 SDF 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Mipmap]] | Mipmap 会混合距离值，SDF 需要谨慎生成和采样。 |
| [[Alpha Test]] | Alpha Test 是二值裁剪；SDF 可提供平滑距离边界。 |

## 常见误区

1. 把 SDF 当普通灰度遮罩使用，不理解距离语义。
2. SDF 范围太小导致描边或软边无法扩展。
3. Mip 或压缩破坏距离值导致边缘抖动。

## 相关条目

- [[Dissolve]]：Dissolve 可使用 SDF 控制消散边界。
- [[Texture Sampling]]：SDF 通常作为纹理采样并解释为距离。
- [[Screen Space]]：屏幕空间 SDF 可用于描边和 UI 效果。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
