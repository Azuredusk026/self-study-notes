---
title: "World Space"
aliases:
  - 世界空间
category: "Shader"
tags: [技术美术, Shader, Space]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# World Space

## 一句话定义

World Space 是以场景全局坐标系为基准的空间。

## 为什么需要它

灯光、相机、场景位置、世界法线、角色脚底检测、世界坐标投射和场景级渐变都需要统一坐标基准。TA 在 Shader 中混用空间会导致光照方向、雾效、扫描线和位置特效错误。

## 核心原理

- 输入：Object Space 数据和对象变换矩阵。
- 处理过程：用 Model Matrix 将局部位置转换到世界坐标。
- 输出：世界位置、世界法线、世界方向。
- 所在层级：Shader、引擎 Transform、场景系统。

## 技术美术中的典型用途

- 世界坐标贴图和三平面映射。
- 场景高度雾、扫描线、范围特效。
- 光照方向和视线方向计算。
- VFX 与场景位置同步。

## Unity 中的相关场景

Unity HLSL 常用 `TransformObjectToWorld` 或矩阵转换。Shader Graph 中有 Position 节点可选择 World。

## Unreal Engine 中的相关场景

Unreal Material 常用 Absolute World Position、World Space Normal、Camera Vector 等节点。

## 常见误区

1. 忽略坐标空间转换，直接把 Object Space 法线用于世界光照。
2. 世界坐标贴图在大世界中出现精度问题。
3. 以为 World Space 效果会跟随模型局部旋转。

## 面试可能怎么问

### 为什么 Shader 中要区分 Object、World、View、Clip Space？

回答要点：不同计算需要不同基准；模型局部效果用 Object，光照和场景交互常用 World，相机相关用 View，屏幕投影用 Clip/Screen。

## 实践建议

实现一个世界坐标棋盘格材质，让多个不同缩放和旋转的物体保持连续图案。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Graph]] | Material Graph 偏节点化编辑；本条目可能涉及更底层的代码、编译和采样细节。 |
| [[Texture Sampling]] | Texture Sampling 是常见操作；本条目可能覆盖更完整的 Shader 结构或控制策略。 |

## 相关条目

- [[Object Space]]
- [[View Space]]
- [[Clip Space]]
- [[矩阵变换]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
