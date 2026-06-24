---
title: "Branch"
aliases: []
category: "02_Shader"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Branch

## 定义与解释

Branch 是 Shader 中根据条件选择不同执行路径的控制结构。它可以表达功能开关、阈值判断和材质逻辑分流，但在 GPU 上不一定像 CPU 分支那样直接节省成本。

## 核心原理

Shader Branch 的核心问题是 GPU 以线程组、Wave 或 Warp 的方式并行执行。若同一组线程走不同分支，硬件可能需要分别执行多个路径并用掩码选择结果，这会产生 divergence 成本。

静态分支通常由编译期关键字或常量决定，可能生成不同变体；动态分支由运行时数据决定，能减少变体但可能增加执行不一致。TA 需要判断分支条件是材质级、对象级还是像素级，并结合平台、分支复杂度和采样成本决定是否使用。

## 用途

- 在材质或 Shader 调试中定位与 Branch 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Keyword]] | Keyword 是开关机制；Branch 是 Shader 中的控制流表达。 |
| [[Shader Variant]] | Variant 是编译产物；Branch 是代码或节点逻辑。 |

## 常见误区

1. 以为所有 if 都能省性能。
2. 用像素级条件控制昂贵采样，结果导致线程分歧严重。
3. 把所有功能都做成静态分支，造成变体爆炸。

## 相关条目

- [[Keyword]]：Keyword 常用于控制静态分支和变体。
- [[Shader Variant]]：静态分支可能生成 Shader Variant。
- [[Precision]]：分支内计算仍受精度和平台影响。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
