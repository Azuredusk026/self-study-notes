---
title: "Shadow_Mapping"
aliases: []
category: "01_Rendering"
confidence: medium
tags: [rendering, shadow]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# Shadow Mapping

## 定义与解释

Shadow Mapping 是实时渲染中常用的阴影技术，先从光源视角记录深度，再从相机视角比较当前点是否被遮挡。

## 常见问题

- Shadow Acne
- Peter Panning
- 采样锯齿
- 级联阴影接缝

## 核心原理

Shadow Mapping 的核心分两步：光源 Pass 渲染深度图，主渲染 Pass 把片元位置变换到光源空间并与阴影图深度比较。如果当前点比阴影图记录更远，就说明它被更靠近光源的物体挡住。

阴影质量受分辨率、光源投影范围、Bias、过滤、级联划分和深度精度影响。常见问题包括 Shadow Acne、Peter Panning、锯齿、闪烁和级联边界。TA 需要根据场景尺度和镜头距离设置阴影参数，而不是只拉高分辨率。

## 用途

- 在渲染调试中定位与 Shadow_Mapping 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[SSAO]] | Shadow Mapping 表达直接光遮挡；SSAO 表达屏幕空间环境遮蔽。 |
| [[Light Probe]] | Light Probe 提供间接光信息；Shadow Mapping 提供直接光阴影。 |

## 常见误区

1. 只提高阴影分辨率，不调整投影范围和 Bias。
2. Bias 过小产生自阴影噪点，过大导致阴影漂浮。
3. 忽略动态物体、半透明和裁剪材质在 Shadow Pass 中的特殊处理。

## 相关条目

- [[Depth Buffer]]：Shadow Map 本质是从光源视角生成的深度缓冲。
- [[Render Pass]]：阴影通常需要独立 Shadow Pass。
- [[Z-Test]]：阴影比较与深度测试思想相关。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
