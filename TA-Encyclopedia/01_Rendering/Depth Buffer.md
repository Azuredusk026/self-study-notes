---
title: "Depth Buffer"
aliases:
  - 深度缓冲
category: "Rendering"
tags: [技术美术, Rendering, Depth]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Depth Buffer

## 一句话定义

Depth Buffer 保存屏幕每个像素位置当前最近表面的深度值。

## 为什么需要它

深度缓冲让 GPU 判断新片元是否被已有表面遮挡。TA 在处理遮挡、描边、软粒子、景深、SSAO、透明排序、Z-Fighting 和性能优化时都会用到深度概念。

## 核心原理

- 输入：片元深度值。
- 处理过程：按 Z-Test 函数与缓冲中已有深度比较。
- 输出：通过测试的片元可写颜色并更新深度。
- 所在层级：GPU 深度测试阶段。

## 技术美术中的典型用途

- 深度预通道和 Early-Z 优化。
- 屏幕空间边缘检测、景深、雾效、软粒子。
- 角色遮挡高亮和 Custom Depth 效果。
- 排查 Z-Fighting、透明穿插。

## Unity 中的相关场景

Unity URP 中 `_CameraDepthTexture` 常被后处理和 Shader 读取。TA 需要注意 Depth Texture 是否开启、深度精度、平台差异。

## Unreal Engine 中的相关场景

Unreal 中 Scene Depth、Custom Depth、Virtual Shadow Maps 等都和深度密切相关。Post Process Material 可以读取 SceneDepth 做屏幕空间效果。

## 常见误区

1. 认为深度值是线性的：透视投影下通常是非线性的。
2. 忘记透明物体通常不写深度或写深度策略不同。
3. 近远裁剪面设置不合理，导致深度精度不足。

## 面试可能怎么问

### 为什么会出现 Z-Fighting？

回答要点：两个表面的深度非常接近，深度缓冲精度无法稳定区分，常见于重叠面、过大的远裁剪面或过小的近裁剪面。

## 实践建议

做一个深度可视化 Shader，观察相机近远裁剪面对深度分布的影响。

## 相关条目

- [[Z-Test]]
- [[Early-Z]]
- [[SSAO]]
- [[Depth of Field]]

## 参考来源

- 待补充

