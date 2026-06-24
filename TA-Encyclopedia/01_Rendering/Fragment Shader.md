---
title: "Fragment Shader"
aliases:
  - Pixel Shader
  - 片元着色器
category: "Rendering"
tags: [技术美术, Rendering, Shader]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Fragment Shader

## 一句话定义

Fragment Shader 是对光栅化产生的片元执行的 GPU 程序，用于计算颜色、材质属性或其他 Render Target 输出。

## 为什么需要它

一个三角形覆盖屏幕后，每个片元可能有不同的 UV、法线、深度和光照结果。Fragment Shader 负责采样贴图、计算光照、透明、溶解、描边遮罩等效果，是 TA 最常接触的 Shader 阶段。

## 核心原理

- 输入：插值后的 UV、法线、颜色、深度、屏幕坐标等。
- 处理过程：纹理采样、光照计算、分支、混合前颜色输出。
- 输出：颜色、G-Buffer 数据、深度或自定义 Render Target。
- 所在层级：GPU 可编程阶段，位于 [[Rasterization]] 后。

## 技术美术中的典型用途

- PBR、NPR、Toon、MatCap、溶解、流光、水、火、护盾等材质。
- 后处理和全屏 Pass。
- G-Buffer 写入和屏幕空间效果。
- 性能分析中评估采样次数、分支、Overdraw 和精度。

## Unity 中的相关场景

Unity 中常写 `frag` 函数或通过 Shader Graph Fragment 端口输出 Base Color、Normal、Emission、Alpha 等。URP 自定义后处理也常使用全屏 Fragment Shader。

## Unreal Engine 中的相关场景

Unreal Material Graph 主要面向像素阶段表达材质逻辑。Post Process Material、Custom 节点和 Material Function 都常涉及片元计算。

## 常见误区

1. 认为屏幕上看不到就没有成本：被透明层覆盖的片元仍可能被执行。
2. 忽略纹理采样成本：多张高分辨率采样会显著增加带宽压力。
3. 在移动端滥用高精度和复杂分支。

## 面试可能怎么问

### Fragment Shader 的输入通常来自哪里？

回答要点：来自顶点阶段输出的插值属性、纹理、常量缓冲、屏幕数据和引擎传入的光照或相机参数。

### 为什么后处理通常是 Fragment Shader？

回答要点：后处理主要在屏幕空间对每个像素处理颜色、深度或法线等缓冲数据。

## 实践建议

实现一个屏幕空间灰度后处理，再加入深度边缘检测，理解片元阶段和屏幕空间采样的关系。

## 相关条目

- [[Vertex Shader]]
- [[Texture Sampling]]
- [[G-Buffer]]
- [[后处理]]

## 参考来源

- 待补充

