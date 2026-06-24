---
title: "SSAO"
aliases: []
category: "01_Rendering"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# SSAO

## 定义与解释

SSAO（Screen Space Ambient Occlusion）是在屏幕空间估算环境遮蔽的后处理技术，用来增强接触阴影和几何缝隙的层次感。

## 核心原理

SSAO 根据当前像素的深度和法线，在屏幕空间周围采样邻近位置，估算这些位置是否遮挡环境光。采样结果经过降噪、模糊和强度调整后叠加到环境光或最终颜色中。

因为 SSAO 只知道屏幕上可见的信息，它无法感知屏幕外或被遮挡的几何，容易产生光晕、噪点和距离错误。TA 需要调半径、强度、采样数、法线来源和深度精度，并确认它和 baked AO、材质 AO 不重复变脏。

## 用途

- 在渲染调试中定位与 SSAO 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Shadow_Mapping]] | Shadow Mapping 计算直接光阴影；SSAO 估算环境遮蔽。 |
| [[PBR]] | PBR 材质中的 AO 通道和 SSAO 都会影响环境遮蔽观感。 |

## 常见误区

1. 把 SSAO 当成真实全局光照。
2. 强度过高导致模型边缘和缝隙发脏。
3. 忽略屏幕空间限制导致的边缘断裂和遮挡缺失。

## 相关条目

- [[Depth Buffer]]：SSAO 依赖深度重建空间关系。
- [[G-Buffer]]：Deferred 管线中 SSAO 常读取法线和深度。
- [[后处理]]：SSAO 属于屏幕空间后处理效果。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
