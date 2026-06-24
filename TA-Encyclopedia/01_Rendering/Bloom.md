---
title: "Bloom"
aliases:
  - 泛光
category: "Rendering"
tags: [技术美术, Rendering, PostProcessing]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---



# Bloom

## 定义与解释

Bloom 是把画面中高亮区域扩散到周围，模拟镜头或眼睛对强光产生的泛光效果。它属于后处理效果，不会真实增加几何光照，只会改变最终图像的亮部观感。

## 核心原理

Bloom 通常先从 HDR 颜色缓冲中按阈值提取高亮区域，再经过多级降采样和模糊，最后把模糊结果叠加回原图。阈值、强度、半径、色调映射顺序和曝光会共同决定 Bloom 是否自然。

核心风险是 Bloom 很容易掩盖材质和灯光问题：如果曝光、Tone Mapping 或发光材质亮度没有统一规范，Bloom 会在不同平台、不同相机设置下表现差异很大。TA 需要把 Bloom 当作图像管线的一环，而不是单独调一个漂亮参数。

## 用途

- 在渲染调试中定位与 Bloom 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Tone Mapping]] | Tone Mapping 负责动态范围压缩；Bloom 负责高亮扩散。 |
| [[Depth of Field]] | 两者都是后处理，但 Bloom 基于亮度，DoF 基于焦距和深度。 |

## 常见误区

1. 用 Bloom 修复本应由灯光、材质或曝光解决的问题。
2. 在 LDR 颜色上强行做 Bloom，导致阈值和亮度语义混乱。
3. 忽略移动端多次模糊和高分辨率 RT 的带宽成本。

## 相关条目

- [[Tone Mapping]]：Bloom 常在 HDR 到 LDR 转换前后与曝光共同决定亮部。
- [[Render Target]]：Bloom 依赖中间颜色缓冲和降采样纹理。
- [[HDRP]]：具体后处理入口与管线设置有关。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
