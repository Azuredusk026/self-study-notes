---
title: "Stencil Buffer"
aliases: []
category: "01_Rendering"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Stencil Buffer

## 定义与解释

Stencil Buffer 是按像素存储小整数标记的缓冲，用于在渲染时根据模板值控制片元是否通过、如何修改标记。它常用于遮罩、描边、传送门、分层渲染和后处理区域控制。

## 核心原理

Stencil 的机制是每个片元在写颜色前执行模板测试。测试会比较当前 Stencil 值和参考值，并根据通过或失败结果执行 Keep、Replace、Increment 等操作。后续 Pass 可以用这些标记限制绘制区域。

Stencil 强大但容易被 Pass 顺序和清理策略影响。TA 需要明确哪个 Pass 写模板、哪个 Pass 读模板、何时清空，以及不同材质是否会互相覆盖模板值。移动端还要注意深度模板格式和带宽。

## 用途

- 在渲染调试中定位与 Stencil Buffer 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Z-Test]] | Z-Test 比较深度；Stencil Test 比较模板值。 |
| [[Custom Depth]] | Custom Depth 常用于特殊对象标记；Stencil 可提供更细的像素级分类。 |

## 常见误区

1. 没有规划模板值分配，多个效果互相覆盖。
2. 忘记清理 Stencil，导致后续 Pass 被旧标记影响。
3. 只在主 Pass 设置 Stencil，忽略阴影、深度或后处理 Pass 的读写关系。

## 相关条目

- [[Depth Buffer]]：Stencil 常和 Depth 作为同一附件的不同部分。
- [[Render Pass]]：模板写入和读取通常跨多个 Pass。
- [[NPR]]：描边和遮罩类 NPR 效果常用 Stencil。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
