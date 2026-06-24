---
title: "Deferred_Rendering"
aliases: []
category: "01_Rendering"
confidence: medium
tags: [rendering, deferred-rendering]
status: active
created: 2026-06-24
updated: "2026-06-24"
---



# Deferred Rendering

## 定义与解释

Deferred Rendering 是先把几何和材质属性写入 G-Buffer，再在后续阶段集中计算光照的渲染路径。它适合大量动态光源场景，但会增加缓冲带宽和透明物体处理复杂度。

## 核心原理

Deferred Rendering 把可见表面的材质信息延迟到光照阶段使用。几何阶段输出法线、深度、Base Color、Roughness、Metallic 等数据；光照阶段在屏幕空间读取这些数据，为每个像素累计光照。

它的优势是光照成本更多与屏幕像素和光源影响范围相关，而不是每个物体重复执行完整光照。代价是 G-Buffer 占用显存和带宽，MSAA、透明、特殊材质和自定义光照会更难处理。TA 需要理解各通道写入内容、调试视图和管线限制。

## 用途

- 在渲染调试中定位与 Deferred_Rendering 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Forward_Rendering]] | Forward 在物体绘制时计算光照；Deferred 在屏幕空间集中计算。 |
| [[G-Buffer]] | G-Buffer 是数据载体；Deferred Rendering 是使用这些数据的渲染路径。 |

## 常见误区

1. 认为 Deferred 一定更快，忽略带宽、平台和透明物体成本。
2. 在 G-Buffer 中塞入过多自定义数据，导致带宽和格式压力上升。
3. 忘记透明物体通常仍需要单独 Forward 或透明阶段处理。

## 相关条目

- [[G-Buffer]]：Deferred Rendering 依赖 G-Buffer 保存几何阶段结果。
- [[Forward_Rendering]]：Forward 是常见对照路径。
- [[Render Pass]]：延迟路径通常拆成几何、光照和后处理 Pass。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
