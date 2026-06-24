---
title: "Forward Rendering"
aliases:
  - 前向渲染
category: "Rendering"
tags: [技术美术, Rendering, RenderPath]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Forward Rendering

## 一句话定义

Forward Rendering 是在绘制物体时直接计算该物体受光结果的渲染路径。

## 为什么需要它

前向渲染结构直观，对透明、MSAA、材质多样性和移动端支持通常更友好。TA 在角色渲染、卡通渲染、移动端项目和透明特效中经常会遇到 Forward Rendering。

## 核心原理

- 输入：物体几何、材质参数、可影响该物体的光源。
- 处理过程：每个 Draw Call 在 Shader 中计算光照并输出颜色。
- 输出：颜色缓冲，可能同时写深度。
- 所在层级：引擎渲染路径。

## 技术美术中的典型用途

- 移动端角色和场景渲染。
- 半透明特效、玻璃、水体、粒子。
- 需要 MSAA 的 VR 或清晰边缘场景。
- 风格化渲染管线。

## Unity 中的相关场景

URP 默认以 Forward 为核心，也提供 Forward+ 等变体。TA 需要关注 Additional Lights、Shadow、Depth Texture 和 Renderer Feature 的影响。

## Unreal Engine 中的相关场景

Unreal 支持 Forward Shading，常用于 VR、MSAA 需求和特定性能目标项目。默认桌面高保真项目更多使用 Deferred。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| Forward Rendering | 绘制物体时直接算光 |
| [[Deferred_Rendering]] | 先写 G-Buffer，再统一算光 |
| Forward+ | 用屏幕分块或集群筛选光源，减少每物体光源遍历 |

## 常见误区

1. 认为 Forward 一定比 Deferred 慢：少量光源或移动端场景可能更合适。
2. 忽略多光源成本：每个物体可能重复计算多个光源。
3. 认为透明在 Deferred 中完全不能做：实际常用 Forward 额外路径处理透明。

## 面试可能怎么问

### Forward 和 Deferred 的主要区别是什么？

回答要点：Forward 在物体绘制时算光，Deferred 先写几何信息再屏幕空间算光；Forward 透明和 MSAA 友好，Deferred 多动态光更容易扩展。

## 实践建议

搭建一个多点光源场景，分别用 Forward 和 Deferred 观察 Draw Call、Pass、带宽和透明物体处理差异。

## 相关条目

- [[Deferred_Rendering]]
- [[G-Buffer]]
- [[PBR]]
- [[Alpha Blend]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。