---
title: "Light Probe"
aliases: []
category: "01_Rendering"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Light Probe

## 定义与解释

Light Probe 是在场景中采样和存储局部间接光照信息的引擎机制，常用于让动态物体获得周围环境光。它解决的是动态对象无法直接使用静态光照贴图的问题。

## 核心原理

Light Probe 通常在空间中布点，烘焙或采样得到该位置的低频光照信息，再在运行时对动态物体所在位置进行插值。常见表达方式包括球谐系数，用于近似环境漫反射。

探针质量取决于布点密度、空间覆盖、插值关系和烘焙设置。探针过稀会导致动态物体光照跳变或不贴合环境；探针放在墙内、地面下或光照突变处也会产生错误结果。TA 需要结合场景结构和动态物体活动范围布置。

## 用途

- 在渲染调试中定位与 Light Probe 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Reflection Probe]] | Light Probe 常提供低频漫反射环境光；Reflection Probe 主要提供反射环境。 |
| [[IBL]] | IBL 是图像环境光方法；Light Probe 是引擎中的空间采样机制。 |

## 常见误区

1. 只在静态物体附近放探针，忽略动态物体移动路径。
2. 探针密度不足导致角色光照突然变化。
3. 把反射问题误判为 Light Probe 问题。

## 相关条目

- [[IBL]]：Light Probe 和 IBL 都用于环境光，但数据形式和用途不同。
- [[Reflection Probe]]：Reflection Probe 更偏环境反射。
- [[PBR]]：PBR 材质会响应探针提供的间接光。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
