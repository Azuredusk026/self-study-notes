---
title: "Vertex Shader"
aliases:
  - 顶点着色器
category: "Rendering"
tags: [技术美术, Rendering, Shader]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Vertex Shader

## 一句话定义

Vertex Shader 是 GPU 上处理每个顶点的程序，通常负责坐标变换和向后续阶段传递插值属性。

## 为什么需要它

模型文件中的顶点通常处于 Object Space，不能直接用于屏幕显示。Vertex Shader 会把顶点经过 Model、View、Projection 变换送入裁剪空间，也可以处理风吹草动、角色顶点动画、描边外扩和 GPU Instancing 参数。

## 核心原理

- 输入：顶点位置、法线、切线、UV、颜色、实例数据。
- 处理过程：坐标空间变换、属性计算、可选顶点偏移。
- 输出：裁剪空间位置和传给片元阶段的 varying/interpolator。
- 所在层级：GPU 可编程阶段，位于图元装配和 [[Rasterization]] 前。

## 技术美术中的典型用途

- 顶点动画、风场、旗帜、水面扰动。
- 反向法线或顶点外扩描边。
- GPU Instancing 中根据实例参数改变颜色、缩放或位置。
- 计算世界空间法线、视线方向等片元阶段需要的数据。

## Unity 中的相关场景

Unity 手写 HLSL、ShaderLab、Shader Graph Custom Function 都可能涉及顶点阶段。URP/HDRP 的 Shader Graph 也提供 Vertex Position、Normal、Tangent 等顶点修改入口。

## Unreal Engine 中的相关场景

Unreal 材质中的 World Position Offset 本质上影响顶点阶段输出，常用于植被风动、简单水面和材质驱动的模型形变。

## 常见误区

1. 把顶点阶段当成逐像素效果：顶点密度不足时形变会很粗糙。
2. 忽略坐标空间：Object、World、View 混用会导致方向错误。
3. 顶点动画影响阴影时，没有同步 Shadow Pass 或深度写入。

## 面试可能怎么问

### Vertex Shader 和 Fragment Shader 的主要区别是什么？

回答要点：Vertex Shader 按顶点执行，主要做坐标和顶点属性处理；Fragment Shader 按片元执行，主要计算最终颜色或材质数据。

### 为什么顶点动画需要考虑模型细分程度？

回答要点：顶点动画只能移动已有顶点，网格太稀会导致轮廓和表面变化不连续。

## 实践建议

实现一个简单 Wind Shader：用顶点颜色作为权重，让草叶顶部随时间和噪声摆动，底部保持稳定。

## 相关条目

- [[Fragment Shader]]
- [[矩阵变换]]
- [[World Space]]
- [[GPU Instancing]]

## 参考来源

- 待补充
