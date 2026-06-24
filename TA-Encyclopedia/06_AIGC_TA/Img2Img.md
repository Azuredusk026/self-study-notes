---
title: "Img2Img"
aliases:
  - Image to Image
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Workflow]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Img2Img

## 一句话定义

Img2Img 是以已有图像作为输入，在保留一定结构或风格的基础上生成新图像的工作流。

## 为什么需要它

TA 和美术团队经常不是从零生成，而是基于草图、白模截图、灰盒场景、旧图标或风格参考做迭代。Img2Img 能把已有资产或构图作为起点，提高可控性。

## 核心原理

输入图会被编码到潜空间并加入一定噪声，模型再根据 Prompt 和参数去噪生成结果。噪声强度越高，越容易偏离原图；越低，越接近原图。

> 待核验：不同工具中 denoise strength、resize mode 和 mask 行为需要按具体版本确认。

## 技术美术中的典型用途

- 白模截图转概念图。
- 旧图标风格重绘。
- 材质参考图风格统一。
- 与 [[ControlNet]]、[[IP-Adapter]] 组合增强结构和风格控制。

## Unity 中的相关场景

Unity 场景截图可以作为 Img2Img 输入，用于快速探索关卡氛围、UI 图标或宣传概念。

## Unreal Engine 中的相关场景

Unreal 高质量视口截图可作为环境概念、灯光方向和材质风格迭代的输入。

## 常见误区

1. denoise 强度过高，失去原图结构。
2. 只用 Img2Img 控制姿态，忽略更适合的 ControlNet。
3. 输入图版权或来源不清。

## 面试可能怎么问

### Img2Img 在游戏美术生产中适合做什么？

回答要点：适合基于草图、截图或旧资产做风格迭代和参考生成，但需要控制结构保留、版权和审核。

## 实践建议

用一张 Unity 灰盒场景截图生成三种氛围概念图，并记录 denoise 强度和 Prompt。

## 相关条目

- [[Inpainting]]
- [[ControlNet]]
- [[IP-Adapter]]
- [[游戏美术资产生成]]

## 参考来源

- 待补充

