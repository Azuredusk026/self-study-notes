---
title: "Screen Space"
aliases: []
category: "02_Shader"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Screen Space

## 定义与解释

Screen Space 是以屏幕像素或归一化屏幕坐标为参考的空间。它常用于后处理、屏幕 UV、深度重建、描边、SSAO 和全屏特效。

## 核心原理

Screen Space 通常来自 Clip Space 透视除法和视口映射。Shader 中可用屏幕坐标采样 Scene Color、Depth、Normal 或其他屏幕纹理，并在像素邻域内做计算。

屏幕空间效果的限制是只知道当前视角可见的信息。屏幕外、被遮挡或透明未写入的对象无法可靠参与计算。TA 还要注意分辨率缩放、动态分辨率、TAA jitter、Y 翻转和 UV 原点差异。

## 用途

- 在材质或 Shader 调试中定位与 Screen Space 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[World Space]] | World Space 是场景坐标；Screen Space 是当前相机投影后的二维坐标。 |
| [[View Space]] | View Space 仍有三维相机空间信息；Screen Space 更贴近像素采样。 |

## 常见误区

1. 以为屏幕空间效果知道完整场景。
2. 动态分辨率或 TAA 下直接按像素偏移导致错位。
3. 忽略不同平台屏幕 UV 原点和 Y 方向。

## 相关条目

- [[Clip Space]]：Clip Space 转换后得到屏幕空间。
- [[后处理]]：后处理大量依赖 Screen Space。
- [[Depth Buffer]]：屏幕空间效果常读取深度。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
