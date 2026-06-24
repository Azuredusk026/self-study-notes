---
title: "Roughness"
aliases: []
category: "01_Rendering"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Roughness

## 定义与解释

Roughness 是 PBR 中描述微表面粗糙程度的参数，主要控制镜面反射的扩散程度和高光宽度。粗糙度越高，反射越模糊；粗糙度越低，反射越集中。

## 核心原理

Roughness 通过影响微表面法线分布改变 BRDF 的镜面项。它不会简单让材质变暗，而是改变能量在角度和区域上的分布：低粗糙度产生锐利高光，高粗糙度产生宽而柔的反射。

工程上，Roughness 对 IBL 采样 Mip、反射探针模糊、压缩精度和贴图通道非常敏感。Unity 的 Smoothness 和 Unreal 的 Roughness 方向相反，跨工具链导出时尤其容易出错。

## 用途

- 在渲染调试中定位与 Roughness 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Metallic]] | Metallic 决定材质类别；Roughness 决定反射扩散。 |
| [[Fresnel]] | Fresnel 控制角度相关强度；Roughness 控制高光形状。 |

## 常见误区

1. 把 Roughness 当作亮度贴图使用。
2. Smoothness/Roughness 反相关系处理错误。
3. 粗糙度贴图走 sRGB 导致中间值不准。

## 相关条目

- [[PBR]]：Roughness 是 PBR 关键参数。
- [[BRDF]]：Roughness 控制微表面分布。
- [[Reflection Probe]]：Roughness 决定环境反射模糊级别。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
