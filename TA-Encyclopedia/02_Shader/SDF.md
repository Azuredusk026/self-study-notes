---
title: "SDF"
aliases:
  - Signed Distance Field
  - 有符号距离场
category: "Shader"
tags: [技术美术, Shader, Math, VFX]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# SDF

## 一句话定义

SDF 用数值表示空间中一点到形状边界的有符号距离，通常内部为负、外部为正或相反。

## 为什么需要它

SDF 可以用较低分辨率表达清晰边缘、可缩放字体、软边遮罩、形状混合和程序化 VFX。TA 常用它制作 UI 字体、描边、溶解边缘、技能范围、体积近似和屏幕特效。

## 核心原理

- 输入：位置坐标和目标形状或预计算距离场纹理。
- 处理过程：计算或采样到边界的距离，根据阈值生成边缘、填充、模糊或混合。
- 输出：遮罩、颜色、法线近似或命中信息。
- 所在层级：Shader、VFX、字体渲染和程序化图形。

## 技术美术中的典型用途

- 字体清晰缩放。
- UI 图标描边和阴影。
- 溶解、护盾、能量场。
- 软粒子碰撞和体积近似。

## Unity 中的相关场景

TextMeshPro 使用 SDF 字体技术。Shader Graph 或 HLSL 可采样 SDF 贴图制作边缘控制和描边。

## Unreal Engine 中的相关场景

Unreal 中 Mesh Distance Fields 可用于距离场阴影、AO、材质效果等；UI 和材质也可使用 SDF 贴图。

## 常见误区

1. 把 SDF 当普通黑白遮罩，浪费距离信息。
2. 距离场分辨率不足导致细节丢失。
3. 忽略符号约定，内部外部判断反了。

## 面试可能怎么问

### SDF 为什么适合做可缩放字体？

回答要点：它存的是到边界的距离，Shader 可以根据阈值重建清晰边缘，并通过距离范围做描边和软阴影。

## 实践建议

用一张圆形 SDF 贴图实现填充、描边、软边和发光四种效果。

## 相关条目

- [[Texture Sampling]]
- [[Fragment Shader]]
- [[Dissolve]]
- [[几何算法]]

## 参考来源

- 待补充

