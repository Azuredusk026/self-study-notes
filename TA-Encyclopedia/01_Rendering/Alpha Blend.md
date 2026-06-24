---
title: "Alpha Blend"
aliases:
  - 透明混合
category: "Rendering"
tags: [技术美术, Rendering, Transparency]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---



# Alpha Blend

## 定义与解释

Alpha Blend 是在片元完成着色后，根据混合状态把当前颜色与颜色缓冲中已有颜色组合起来的透明渲染机制。它主要用于半透明材质、粒子、UI 和叠加类特效，核心边界是它通常不再像不透明物体那样只由最近表面决定最终颜色。

## 核心原理

Alpha Blend 的关键在于目标颜色已经存在，当前片元只是按 Blend Factor 参与组合。常见公式会用源 Alpha 控制当前颜色权重，用 OneMinusSrcAlpha 控制背景权重；Additive、Multiply、Premultiplied Alpha 等模式则改变颜色贡献方式。

因为混合依赖已有目标颜色，绘制顺序会直接改变结果。半透明对象通常关闭深度写入但保留深度测试，以避免遮住后续透明物体；这会带来排序、交叉几何、粒子堆叠和 Overdraw 成本问题。TA 在项目中需要同时检查贴图 Alpha 类型、材质队列、ZWrite、排序规则和后处理前后的颜色空间。

## 用途

- 在渲染调试中定位与 Alpha Blend 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Alpha Test]] | Alpha Test 是二值裁剪；Alpha Blend 是连续混合。 |
| [[Forward_Rendering]] | 透明物体常在 Forward 或单独透明阶段处理，和不透明光照路径不同。 |

## 常见误区

1. 认为只调 Alpha 就能得到正确透明效果，忽略混合模式、排序和深度写入。
2. 把 Straight Alpha 和 Premultiplied Alpha 贴图混用，导致边缘发黑或发亮。
3. 期望复杂交叉透明几何在普通排序下完全正确。

## 相关条目

- [[Alpha Test]]：同样处理透明边界，但 Alpha Blend 保留连续透明度。
- [[Overdraw]]：半透明对象常造成大量重复片元着色。
- [[Z-Test]]：透明材质通常仍依赖深度测试控制遮挡。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
