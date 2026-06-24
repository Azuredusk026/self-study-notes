---
title: "World Space"
aliases:
  - 世界空间
category: "Shader"
tags: [技术美术, Shader, Space]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# World Space

## 定义与解释

World Space 是整个场景共享的全局坐标空间。它用于描述物体位置、灯光方向、世界法线、体积效果和跨对象一致的材质逻辑。

## 核心原理

模型顶点从 Object Space 通过模型矩阵转换到 World Space。世界空间让不同对象可以在同一坐标系中比较位置、方向和距离，再根据需要转换到 View、Clip 或 Screen Space。

World Space 适合做世界坐标渐变、三平面投射、全局风场、体积雾和基于高度的效果。风险是大世界坐标精度、浮点抖动、原点重定位、非均匀缩放和实例化矩阵处理。TA 需要确认效果是否应该跟随物体还是固定在世界中。

## 用途

- 在材质或 Shader 调试中定位与 World Space 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Object Space]] | Object Space 跟随模型；World Space 统一整个场景。 |
| [[Screen Space]] | Screen Space 跟随相机投影；World Space 独立于屏幕像素。 |

## 常见误区

1. 用 World Space 做本应跟随模型的局部效果。
2. 大世界坐标下使用低精度导致抖动。
3. 非均匀缩放下直接变换法线导致光照错误。

## 相关条目

- [[Object Space]]：Object Space 经模型矩阵变为 World Space。
- [[View Space]]：World Space 经相机矩阵变为 View Space。
- [[Tangent Space]]：法线常从 Tangent Space 转到 World Space。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
