---
title: "Precision"
aliases:
  - Shader 精度
category: "Shader"
tags: [技术美术, Shader, Optimization]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Precision

## 一句话定义

Precision 指 Shader 中数值类型的精度选择，例如 half、float、fixed 或平台对应的低/中/高精度。

## 为什么需要它

精度影响寄存器、带宽、运算吞吐和画面稳定性。移动端和低功耗设备上，合理使用 half 可能降低成本；但在世界坐标、深度、法线重建、时间累积等场景中过低精度会产生抖动、条带或计算错误。

## 核心原理

- 输入：数值范围、精度需求、目标平台。
- 处理过程：编译器将类型映射到平台支持的寄存器和指令。
- 输出：不同精度下的性能和误差表现。
- 所在层级：Shader 代码和 GPU 编译。

## 技术美术中的典型用途

- 移动端材质优化。
- 控制颜色、法线、UV、世界坐标的类型。
- 排查条带、闪烁、深度重建错误。
- 平衡画质和性能。

## Unity 中的相关场景

Unity HLSL 中常见 `half`、`float`。Shader Graph 也允许部分节点设置 Precision。不同平台实际映射需要以目标设备测试为准。

## Unreal Engine 中的相关场景

Unreal 材质通常由编译器和平台后端决定精度，移动端材质和项目设置会影响实际生成代码。

## 常见误区

1. 全部用 float 保守处理，导致移动端成本偏高。
2. 全部用 half，导致大世界坐标和深度计算不稳定。
3. 不在目标机验证精度假设。

## 面试可能怎么问

### half 和 float 应该怎么选择？

回答要点：颜色、局部向量、部分中间结果可优先 half；世界坐标、深度、矩阵变换和高动态范围计算更谨慎使用 float，并以目标平台验证。

## 实践建议

在移动设备上比较同一材质 half/float 版本的 GPU 时间和画面误差。

## 相关条目

- [[Shader Variant]]
- [[Texture Sampling]]
- [[World Space]]
- [[Depth Buffer]]

## 参考来源

- 待核验：不同 GPU 架构的 half/float 性能差异需要查阅厂商文档和实机验证。

