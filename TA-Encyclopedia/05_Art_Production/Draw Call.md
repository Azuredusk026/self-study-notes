---
title: "Draw Call"
aliases: []
category: "05_Art_Production"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Draw Call

## 定义与解释

Draw Call 是 CPU 向 GPU 提交一次绘制命令的抽象成本指标。它在美术生产中常与材质数量、网格拆分、批处理和实例化策略相关。

## 核心原理

Draw Call 的成本来自 CPU 准备渲染状态、绑定资源、提交命令和驱动/渲染线程处理。一个模型如果拆成多个材质槽、多个 Pass 或多个渲染状态，就可能产生多次绘制。

优化 Draw Call 不等于把所有东西合成一个网格。TA 需要同时考虑剔除粒度、材质复用、实例化、SRP Batcher、合批、透明排序和内存。降低提交成本不能以严重增加 Overdraw 或破坏资源管理为代价。

## 用途

- 在资产制作和引擎导入中定位与 Draw Call 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Overdraw]] | Draw Call 是提交成本；Overdraw 是屏幕重复着色成本。 |
| [[Texture Atlas]] | Atlas 可减少材质切换，但也可能增加贴图管理成本。 |

## 常见误区

1. 只追求 Draw Call 数字越低越好。
2. 合并网格后剔除粒度变差，反而增加渲染成本。
3. 忽略多 Pass、阴影 Pass 和透明 Pass 也会产生绘制。

## 相关条目

- [[GPU Instancing]]：实例化可减少重复对象提交成本。
- [[SRP Batcher]]：SRP Batcher 优化 Unity SRP 提交路径。
- [[Material Instance]]：材质复用有助于控制绘制状态差异。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
