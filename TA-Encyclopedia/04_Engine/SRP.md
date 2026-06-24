---
title: "SRP"
aliases:
  - Scriptable Render Pipeline
category: "04_Engine"
tags: [技术美术, Unity, Rendering]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# SRP

## 一句话定义

SRP 是 Unity 允许开发者用脚本控制渲染流程的渲染管线架构。

## 为什么需要它

Built-in 管线封装较深，很多自定义效果只能绕路。SRP 让项目可以明确控制相机、剔除、Pass 调度、Render Target、后处理和 Shader Library。TA 在 URP/HDRP 项目中做工具和效果时，实际面对的是 SRP 思维。

## 核心原理

SRP 的核心是由 C# 端组织渲染：获取相机数据，执行剔除，安排 Draw Call、Render Pass 和后处理，并把 GPU 资源在不同阶段传递。

## 技术美术中的典型用途

- 理解 URP/HDRP 的渲染入口。
- 定位一个效果应该插入哪个 Pass。
- 管理 [[RenderTexture]]、深度、法线和颜色缓冲。
- 解释 SRP Batcher、Shader Variant 和材质兼容性问题。

## Unity 中的相关场景

URP 和 HDRP 都建立在 SRP 之上。自定义 SRP 成本较高，但理解 SRP 对写 Renderer Feature、Debug Pass 和性能分析很有帮助。

## Unreal Engine 中的相关场景

Unreal 的渲染管线不是 SRP，但同样有 Pass、Render Target、后处理和材质编译概念。面试中可用 SRP 与 Unreal 的渲染扩展方式做对比。

## 常见误区

1. 把 SRP 只理解成 URP：URP/HDRP 是 SRP 的官方实现。
2. 认为 SRP 只影响渲染，不影响 Shader 和资源规范。
3. 在不了解内置 Pass 的情况下盲目插入全屏效果。

## 面试可能怎么问

### SRP 相比 Built-in 管线的价值是什么？

回答要点：SRP 给项目更多渲染流程控制能力，便于定制渲染路径、Pass、后处理和平台策略，但也要求团队理解更完整的渲染流程。

## 实践建议

阅读一个 URP Frame Debugger 帧，按顺序记录 Shadow、Depth、Opaque、Transparent、PostProcess 的输入输出。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Unity]] | Unity 是引擎平台；本条目可能是其中某个系统或工作流。 |
| [[Unreal_Engine]] | Unreal 是引擎平台；本条目可能与其对应系统形成实现差异。 |

## 相关条目

- [[URP]]
- [[HDRP]]
- [[Render Pass]]
- [[SRP Batcher]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
