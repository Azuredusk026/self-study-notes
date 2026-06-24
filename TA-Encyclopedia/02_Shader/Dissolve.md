---
title: "Dissolve"
aliases: []
category: "02_Shader"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Dissolve

## 定义与解释

Dissolve 是用遮罩、噪声或阈值逐步裁剪或混合表面的 Shader 效果。它常用于消散、燃烧、传送、破碎显隐和技能特效。

## 核心原理

Dissolve 的核心是把某种标量场与阈值比较：低于或高于阈值的区域被裁剪、透明化或改变颜色。噪声贴图、顶点色、世界坐标、SDF 或程序噪声都可以作为控制场。

效果质量取决于遮罩空间、边缘宽度、抗锯齿、深度写入和阴影 Pass 是否一致。若使用 clip/discard，会影响 Early-Z 和阴影；若使用 Alpha Blend，则会带来透明排序和 Overdraw 问题。TA 需要把主 Pass、阴影、深度和特效边缘统一设计。

## 用途

- 在材质或 Shader 调试中定位与 Dissolve 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Alpha Test]] | Alpha Test 是裁剪机制；Dissolve 是基于遮罩阈值的效果设计。 |
| [[Texture Sampling]] | Dissolve 常采样噪声或遮罩，但不等同于采样本身。 |

## 常见误区

1. 只做主 Pass 消散，忘记阴影和深度 Pass。
2. 边缘过窄导致锯齿或闪烁。
3. 在大量粒子或全屏物体上使用高成本噪声采样。

## 相关条目

- [[Alpha Test]]：Dissolve 常用裁剪实现硬边消散。
- [[Alpha Blend]]：柔和消散可能使用透明混合。
- [[SDF]]：SDF 可作为更稳定的距离控制场。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
