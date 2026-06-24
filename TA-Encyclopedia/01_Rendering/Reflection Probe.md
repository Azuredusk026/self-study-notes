---
title: "Reflection Probe"
aliases: []
category: "01_Rendering"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Reflection Probe

## 定义与解释

Reflection Probe 是在场景中捕获或提供局部环境反射数据的引擎对象，用于让材质获得比全局天空盒更贴合位置的反射。

## 核心原理

Reflection Probe 通常生成 Cubemap，并在材质采样环境反射时根据物体位置、探针权重和 Roughness 选择合适的反射数据。不同粗糙度会采样不同模糊级别，形成从清晰镜面到模糊反射的过渡。

探针的效果取决于位置、包围范围、更新频率、混合策略和是否做盒投影。室内、镜面地面、金属物体和高反射材质很容易暴露探针不匹配。TA 需要把探针布置、烘焙/实时更新和材质 Roughness 一起检查。

## 用途

- 在渲染调试中定位与 Reflection Probe 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Light Probe]] | Reflection Probe 偏镜面环境反射；Light Probe 偏低频间接光。 |
| [[Render Target]] | 实时反射探针可能渲染到 Cubemap Render Target。 |

## 常见误区

1. 全场景只放一个探针导致室内外反射不匹配。
2. 高反射材质调错时只改材质，不检查探针数据。
3. 忽略实时探针更新成本。

## 相关条目

- [[IBL]]：Reflection Probe 常作为局部 IBL 反射来源。
- [[Roughness]]：粗糙度决定反射探针采样的模糊程度。
- [[Light Probe]]：两者都提供环境信息但用途不同。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
