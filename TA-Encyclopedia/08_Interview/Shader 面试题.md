---
title: "Shader 面试题"
aliases: []
category: "08_Interview"
tags: [技术美术, Interview, Shader]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Shader 面试题

## 使用方式

这页不是背诵稿，而是面试前用于组织回答的检查表。回答时尽量从“原理、项目场景、性能、排查方式”四个角度展开。

## 问题 1：Vertex Shader 和 Fragment Shader 有什么区别？

### 考察点

- GPU 渲染管线基础
- 顶点阶段和片元阶段的职责
- TA 对性能瓶颈的判断能力

### 推荐回答

Vertex Shader 按顶点执行，主要处理坐标变换、顶点属性传递和顶点动画；Fragment Shader 按片元执行，主要处理贴图采样、光照、透明和材质颜色。顶点阶段成本更接近顶点数量，片元阶段成本更接近屏幕覆盖、Overdraw 和采样复杂度。

### 追问方向

- 顶点动画会受模型细分影响吗？
- 透明粒子为什么更容易造成片元压力？

### 相关条目

- [[Vertex Shader]]
- [[Fragment Shader]]
- [[Overdraw]]

## 问题 2：法线贴图为什么要注意 Tangent Space？

### 考察点

- Normal Map 解码
- TBN 矩阵
- DCC 与引擎一致性

### 推荐回答

常见法线贴图存储的是切线空间方向，需要通过 Tangent、Bitangent、Normal 构成的 TBN 基底转到世界或视图空间参与光照。如果 DCC 烘焙和引擎使用的切线空间不一致，就会出现接缝、高光断裂或法线方向错误。

### 易错回答

- “法线贴图就是一张颜色图。”
- “把绿通道翻一下就一定能修好。”

### 相关条目

- [[Normal Map]]
- [[Tangent Space]]
- [[Texture Sampling]]

## 问题 3：Shader Variant 膨胀怎么排查？

### 考察点

- Keyword 管理
- 构建体积和加载性能
- Unity/Unreal 材质编译理解

### 推荐回答

先统计变体来源：全局 Keyword、材质功能开关、光照和阴影组合、平台宏、URP/HDRP 设置。然后区分必须保留和可剔除的功能，减少无用 `multi_compile`，把运行时连续参数改成 uniform 而不是静态开关，最后用构建报告或引擎工具验证数量变化。

### 相关条目

- [[Shader Variant]]
- [[Keyword]]
- [[URP]]
- [[SRP Batcher]]

