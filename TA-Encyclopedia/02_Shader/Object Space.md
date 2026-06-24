---
title: "Object Space"
aliases:
  - Local Space
  - 模型空间
category: "Shader"
tags: [技术美术, Shader, Space]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Object Space

## 一句话定义

Object Space 是以模型自身原点和轴向为基准的局部坐标空间。

## 为什么需要它

模型顶点、法线和绑定数据通常从 Object Space 开始。TA 在写顶点动画、描边、对象局部渐变、模型扫描线和程序化材质时，需要判断数据是否应该跟随物体自身移动和旋转。

## 核心原理

- 输入：模型局部顶点和方向。
- 处理过程：通过 Model Matrix 转换到 World Space。
- 输出：世界空间位置或方向。
- 所在层级：Vertex Shader、DCC、引擎 Transform。

## 技术美术中的典型用途

- 局部坐标驱动的溶解和扫描。
- 按模型高度做渐变。
- 顶点偏移动画。
- Pivot 和 Scale 问题排查。

## Unity 中的相关场景

Unity Shader 中 object space position 通常来自 mesh vertex。`unity_ObjectToWorld` 用于转到世界空间。

## Unreal Engine 中的相关场景

Unreal Material 中 Local Position、Object Position、Actor Position 等节点常用于对象局部效果。

## 常见误区

1. 用 Object Space 做世界方向效果，物体旋转后效果也跟着转。
2. 忽略非均匀缩放对法线和方向转换的影响。
3. 模型 Pivot 不规范导致局部渐变或旋转异常。

## 面试可能怎么问

### Object Space 和 World Space 的区别是什么？

回答要点：Object Space 相对模型自身，World Space 相对场景全局；前者随物体变换，后者用于统一场景计算。

## 实践建议

写一个按 Object Space Y 轴高度变色的材质，旋转模型观察渐变方向是否随模型变化。

## 相关条目

- [[World Space]]
- [[矩阵变换]]
- [[Vertex Shader]]
- [[Pivot]]

## 参考来源

- 待补充

