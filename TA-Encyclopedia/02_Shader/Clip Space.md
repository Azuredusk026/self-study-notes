---
title: "Clip Space"
aliases:
  - 裁剪空间
category: "Shader"
tags: [技术美术, Shader, Space]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Clip Space

## 一句话定义

Clip Space 是顶点经过 Model、View、Projection 变换后，用于裁剪和透视除法前的空间。

## 为什么需要它

GPU 需要判断顶点是否在视锥内，并将 3D 位置投影到屏幕。Clip Space 是顶点着色器通常必须输出的位置空间。TA 写自定义顶点变换、屏幕空间效果和全屏三角形时需要理解它。

## 核心原理

- 输入：Object 或 World Space 顶点位置。
- 处理过程：乘以 MVP 矩阵得到 homogeneous clip position。
- 输出：`x, y, z, w`，随后进行裁剪和透视除法。
- 所在层级：Vertex Shader 输出。

## 技术美术中的典型用途

- 自定义投影和顶点偏移。
- 全屏 Pass。
- 屏幕空间 UV 推导。
- 解决平台 NDC 深度范围差异。

## Unity 中的相关场景

Unity HLSL 中常用 `TransformObjectToHClip` 输出裁剪空间位置。平台差异通常由 SRP 函数封装。

## Unreal Engine 中的相关场景

Unreal 材质中较少直接暴露 Clip Space，但自定义 HLSL、后处理和插件开发可能涉及投影矩阵。

## 常见误区

1. 忘记 Clip Space 还没有除以 w。
2. 直接把 Clip Space xy 当屏幕 UV。
3. 忽略不同图形 API 的 NDC 深度范围差异。

## 面试可能怎么问

### MVP 矩阵最终把顶点变到什么空间？

回答要点：通常变到 Clip Space，经过裁剪和透视除法后才进入 NDC，再映射到屏幕。

## 实践建议

写一个全屏三角形后处理，手动输出 Clip Space 顶点位置，理解屏幕覆盖。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Graph]] | Material Graph 偏节点化编辑；本条目可能涉及更底层的代码、编译和采样细节。 |
| [[Texture Sampling]] | Texture Sampling 是常见操作；本条目可能覆盖更完整的 Shader 结构或控制策略。 |

## 相关条目

- [[矩阵变换]]
- [[Vertex Shader]]
- [[Screen Space]]
- [[View Space]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
