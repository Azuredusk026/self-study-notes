---
title: "Forward Rendering"
aliases:
  - 前向渲染
category: "Rendering"
tags: [技术美术, Rendering, RenderPath]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Forward Rendering

## 定义与解释

Forward Rendering 是在绘制物体时直接完成材质着色和光照计算的渲染路径。它路径直观、透明和 MSAA 支持相对自然，但大量动态光源可能造成重复计算。

## 核心原理

Forward Rendering 的核心是物体提交后，在对应 Shader Pass 中计算可见片元的光照并写入颜色缓冲。每个物体或每个 Pass 需要处理影响它的灯光、阴影和材质逻辑。

Forward 的优势是材质自由度高，对透明、特殊光照和 MSAA 更友好；问题是光源数量、Pass 数量和物体数量会放大成本。现代 URP、HDRP 和 Unreal 可能提供 Forward+、Clustered 或混合路径，TA 需要确认项目实际使用的灯光裁剪和材质限制。

## 用途

- 在渲染调试中定位与 Forward Rendering 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Deferred_Rendering]] | Forward 绘制时算光；Deferred 先写 G-Buffer 再屏幕空间算光。 |
| [[Render Pass]] | Forward 是路径选择；Render Pass 是具体绘制阶段。 |

## 常见误区

1. 认为 Forward 只适合低端或简单场景。
2. 忽略多光源、多 Pass、阴影和透明叠加带来的成本。
3. 没有确认项目使用的是传统 Forward 还是 Forward+/Clustered 变体。

## 相关条目

- [[Deferred_Rendering]]：两者是主要渲染路径对照。
- [[Alpha Blend]]：透明物体常在 Forward 路径处理。
- [[Render Pass]]：Forward 材质可能包含多个 Pass。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
