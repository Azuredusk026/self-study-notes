---
title: "Alpha Test"
aliases:
  - Alpha Clip
  - 透明裁剪
category: "Rendering"
tags: [技术美术, Rendering, Transparency]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---



# Alpha Test

## 定义与解释

Alpha Test 是根据 Alpha 或遮罩阈值直接丢弃片元的透明裁剪方式。它适合树叶、铁丝网、破洞布料等边界明确的材质，不适合表达玻璃、烟雾这类连续半透明。

## 核心原理

Alpha Test 的机制是片元着色阶段执行裁剪判断，低于阈值的片元不会继续写入颜色和深度。由于剩余片元仍可写深度，它更接近不透明渲染路径，排序问题通常比 Alpha Blend 少，但边缘会呈现硬切断。

在实时项目中，Alpha Test 的质量主要受遮罩分辨率、阈值、抗锯齿策略、Mip 边界和阴影 Pass 一致性影响。移动端或植被密集场景还要关注被裁掉的片元是否已经产生了昂贵采样和 Overdraw 成本。

## 用途

- 在渲染调试中定位与 Alpha Test 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Alpha Blend]] | Alpha Test 不保留半透明层次；Alpha Blend 会与背景颜色混合。 |
| [[Depth Buffer]] | Alpha Test 可写入深度，Depth Buffer 决定后续遮挡。 |

## 常见误区

1. 以为 Alpha Test 没有性能成本，忽略被裁掉片元之前的采样和着色。
2. 遮罩阈值在主 Pass、阴影 Pass、Depth Pass 中不一致。
3. 忽略 Mipmap 后遮罩边缘变粗、变细或闪烁。

## 相关条目

- [[Alpha Blend]]：连续半透明使用混合而不是二值裁剪。
- [[Z-Test]]：被保留的片元通常可以正常写入深度。
- [[Overdraw]]：大量遮罩面片仍可能造成片元浪费。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
