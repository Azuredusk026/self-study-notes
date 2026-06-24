---
title: "Tone Mapping"
aliases: []
category: "01_Rendering"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Tone Mapping

## 定义与解释

Tone Mapping 是把 HDR 颜色映射到显示设备可表达范围的过程。它决定高光如何压缩、暗部如何保留，以及最终画面的曝光和对比观感。

## 核心原理

实时渲染中光照和 Bloom 等效果常在 HDR 空间计算，最终需要通过 Tone Mapping 转成 LDR 或目标显示格式。不同曲线如 Reinhard、ACES 或引擎自定义曲线，会产生不同的高光滚降、饱和度和肤色表现。

Tone Mapping 不是简单的亮度缩放，它与曝光、色彩管理、Bloom、后处理 LUT 和显示设备相关。TA 需要统一项目的亮度基准和校色流程，否则材质、灯光和后期会互相补偿，难以稳定复现。

## 用途

- 在渲染调试中定位与 Tone Mapping 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Bloom]] | Bloom 扩散高亮；Tone Mapping 压缩动态范围。 |
| [[后处理]] | Tone Mapping 是后处理链中的关键颜色转换步骤。 |

## 常见误区

1. 把 Tone Mapping 当成最终调色滤镜，忽略 HDR 到显示范围的转换职责。
2. 材质和灯光没有亮度基准，只靠后期曲线补救。
3. 不同平台使用不同 Tone Mapping 曲线导致画面风格不一致。

## 相关条目

- [[Bloom]]：Bloom 与 Tone Mapping 共同决定高亮观感。
- [[PBR]]：PBR 光照通常需要合理曝光和 Tone Mapping 呈现。
- [[Render Target]]：Tone Mapping 常读取 HDR RT 并输出到显示目标。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
