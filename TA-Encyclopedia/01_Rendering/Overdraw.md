---
title: "Overdraw"
aliases:
  - 过度绘制
category: "Rendering"
tags: [技术美术, Rendering, Optimization]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Overdraw

## 定义与解释

Overdraw 是同一屏幕像素被多个片元重复绘制或着色的现象。它会增加片元着色、带宽和混合成本，在透明、粒子、植被和复杂遮挡场景中特别常见。

## 核心原理

Overdraw 的本质是屏幕空间覆盖重复。即使最后只看到最前面的颜色，后面的片元也可能已经执行了着色、采样或混合。Early-Z 可以减少不透明物体的无效片元，但透明和裁剪材质往往更难优化。

TA 需要结合 Overdraw 视图、材质复杂度、绘制顺序和屏幕占比判断成本。一个低面数粒子如果覆盖全屏并多层叠加，可能比高面数小物体更贵。

## 用途

- 在渲染调试中定位与 Overdraw 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Draw Call]] | Draw Call 是提交次数成本；Overdraw 是屏幕片元重复成本。 |
| [[Z-Test]] | Z-Test 决定片元是否通过；Overdraw 描述重复覆盖现象。 |

## 常见误区

1. 只按三角形数量估算渲染成本。
2. 忽略大面积透明粒子和 UI 叠加的片元成本。
3. 认为关闭看不见的模型就解决了所有 Overdraw，忽略透明层级。

## 相关条目

- [[Early-Z]]：Early-Z 可减少部分不透明 Overdraw 成本。
- [[Alpha Blend]]：透明混合常造成高 Overdraw。
- [[Fragment Shader]]：Overdraw 会放大片元着色成本。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
