---
title: "Depth of Field"
aliases: []
category: "01_Rendering"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---



# Depth of Field

## 定义与解释

Depth of Field 是根据焦点距离让画面中焦外区域变模糊的后处理效果，用来模拟相机景深。它依赖深度信息和模糊半径控制，不等同于普通全屏模糊。

## 核心原理

DoF 通常根据 Depth Buffer 计算每个像素到焦平面的距离，再得到 Circle of Confusion 半径。后处理阶段按半径对颜色进行散焦模糊，并需要处理前景遮挡、背景泄漏和半透明边缘。

高质量 DoF 的难点在于视觉和性能平衡：大半径模糊成本高，前景虚化容易产生边缘光晕，透明物体和粒子可能没有可靠深度。TA 需要把焦距、光圈、深度范围、分辨率和后处理顺序一起检查。

## 用途

- 在渲染调试中定位与 Depth of Field 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Bloom]] | Bloom 基于亮度扩散；DoF 基于焦距和深度模糊。 |
| [[SSAO]] | SSAO 使用深度估计遮蔽；DoF 使用深度估计离焦。 |

## 常见误区

1. 把 DoF 当作简单模糊，忽略焦点和深度关系。
2. 忘记透明物体或粒子不写深度导致虚化异常。
3. 在移动端使用过大半径或过高分辨率造成明显带宽压力。

## 相关条目

- [[Depth Buffer]]：DoF 依赖深度判断焦内和焦外。
- [[Bloom]]：两者都是后处理，但驱动依据不同。
- [[Render Target]]：DoF 通常需要中间模糊缓冲。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
