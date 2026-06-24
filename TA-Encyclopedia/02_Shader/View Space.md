---
title: "View Space"
aliases:
  - Camera Space
  - 视图空间
category: "Shader"
tags: [技术美术, Shader, Space]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# View Space

## 定义与解释

View Space 是以相机为原点和方向参考的坐标空间。它常用于光照、深度、法线、屏幕效果和与相机相关的计算。

## 核心原理

物体从 World Space 经过 View Matrix 转换到 View Space，此时相机位于空间原点。视图空间能方便表达到相机的方向、深度和相对位置，再进一步通过投影矩阵进入 Clip Space。

不同引擎对相机前向轴、深度正负和矩阵布局有约定差异。TA 在写深度重建、边缘检测、View Direction、法线变换和雾效时，需要确认使用的是 View Space、World Space 还是 Screen Space 数据。

## 用途

- 在材质或 Shader 调试中定位与 View Space 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[World Space]] | World Space 是场景坐标；View Space 是相机相对坐标。 |
| [[Clip Space]] | Clip Space 加入投影和齐次裁剪；View Space 仍是三维相机空间。 |

## 常见误区

1. 把 View Space 深度当作非线性深度纹理值。
2. 相机前向轴约定弄错导致方向反了。
3. 混用 View Space 法线和 World Space 光照方向。

## 相关条目

- [[World Space]]：View Space 由 World Space 经相机矩阵得到。
- [[Clip Space]]：View Space 经投影矩阵进入 Clip Space。
- [[Screen Space]]：屏幕空间效果常由 View Space 重建位置。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
