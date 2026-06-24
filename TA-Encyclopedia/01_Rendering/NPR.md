---
title: "NPR"
aliases: []
category: "01_Rendering"
confidence: medium
tags: [rendering, npr]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# NPR

## 定义与解释

NPR（Non-Photorealistic Rendering）是非真实感渲染的统称，目标不是逼近物理真实，而是服务风格表达、可读性和艺术方向。卡通、描边、手绘、版画和技术可视化都可属于 NPR。

## 核心原理

NPR 的核心不是某一个算法，而是一组打破或重塑真实光照规律的表现策略。常见方法包括光照阶梯化、色块分层、法线或深度描边、笔触纹理、Ramp 贴图、屏幕空间线条和后处理风格化。

NPR 项目最重要的是风格一致性和可控性。TA 需要把光照模型、材质参数、轮廓线、阴影层级、后处理和美术规范绑定起来，否则不同角色、场景和平台会出现风格漂移。

## 用途

- 在渲染调试中定位与 NPR 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[PBR]] | PBR 追求物理一致性；NPR 追求风格目标和可控表达。 |
| [[Toon_Shading]] | Toon Shading 是 NPR 的具体风格化光照方案。 |

## 常见误区

1. 把 NPR 理解成低成本渲染，忽略描边、后处理和多 Pass 成本。
2. 没有统一 Ramp、阴影层级和材质规范，导致风格不一致。
3. 在真实光照管线里零散加效果，缺少整体风格设计。

## 相关条目

- [[Toon_Shading]]：Toon Shading 是常见 NPR 分支。
- [[后处理]]：许多 NPR 效果依赖屏幕空间后处理。
- [[Stencil Buffer]]：描边和分层渲染可能使用模板控制。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
