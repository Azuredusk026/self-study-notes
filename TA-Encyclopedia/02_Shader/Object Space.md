---
title: "Object Space"
aliases:
  - Local Space
  - 模型空间
category: "Shader"
tags: [技术美术, Shader, Space]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Object Space

## 定义与解释

Object Space 是以模型自身原点、轴向和缩放为参考的局部坐标空间。它用于描述顶点原始位置、局部方向和随物体一起移动的效果。

## 核心原理

Object Space 的坐标会随模型导入和对象变换进入世界空间。顶点数据通常先在 Object Space 中定义，再由模型矩阵转换到 World Space。

在 Shader 中，Object Space 适合做局部渐变、模型内坐标遮罩、顶点动画和不受世界位置影响的效果。问题在于非均匀缩放、合批、实例化和导入轴向会改变预期，TA 需要确认坐标来源和矩阵转换。

## 用途

- 在材质或 Shader 调试中定位与 Object Space 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[World Space]] | Object Space 跟随单个模型；World Space 是场景统一坐标。 |
| [[Tangent Space]] | Tangent Space 依附表面切线基底；Object Space 依附模型整体。 |

## 常见误区

1. 用 Object Space 做世界方向效果，导致物体旋转后效果跟着转。
2. 忽略非均匀缩放对法线和距离的影响。
3. 不同 DCC 导入轴向不一致导致局部效果错位。

## 相关条目

- [[World Space]]：Object Space 经过模型矩阵变成 World Space。
- [[Tangent Space]]：Tangent Space 依附表面局部基底。
- [[Vertex Shader]]：顶点阶段常处理 Object Space 到 Clip Space 的变换。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
