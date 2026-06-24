---
title: "Shader基础"
aliases: []
category: "02_Shader"
confidence: medium
tags: [shader, basics]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# Shader基础

## 定义与解释

Shader 是运行在 GPU 管线中的程序，用于控制顶点处理、片元着色、材质属性、屏幕效果或计算任务。Shader 基础关注的是阶段、数据流、资源绑定和引擎封装之间的关系。

## 基础主题

- 顶点着色器
- 片元/像素着色器
- Uniform/常量缓冲
- 纹理采样
- 坐标空间

## 核心原理

Shader 的核心不是单个公式，而是 GPU 在不同阶段执行小程序。顶点阶段处理几何和空间变换，光栅化产生片元，片元阶段采样纹理、计算光照或写入缓冲；计算 Shader 则脱离传统图形阶段执行通用并行任务。

引擎会把 Shader 组织成材质、Pass、Keyword、Variant 和参数面板。TA 需要理解这些封装如何映射到实际 GPU 工作，否则很难判断一个材质问题来自代码、资源、管线状态还是平台差异。

## 用途

- 在材质或 Shader 调试中定位与 Shader基础 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Graph]] | Material Graph 是创作界面；Shader基础解释底层执行关系。 |
| [[Shader Variant]] | Variant 是 Shader 工程化产物，不是 Shader 概念本身。 |

## 常见误区

1. 把 Shader 只理解为材质颜色公式。
2. 只看节点或代码，不看 Pass、队列、变体和资源绑定。
3. 忽略平台差异导致同一 Shader 表现或性能不同。

## 相关条目

- [[HLSL]]：常见 Shader 语言。
- [[Fragment Shader]]：片元阶段是 Shader 的重要执行阶段。
- [[Texture Sampling]]：纹理采样是 Shader 高频操作。
- [[Material Graph]]：节点材质是 Shader 的封装形式。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
