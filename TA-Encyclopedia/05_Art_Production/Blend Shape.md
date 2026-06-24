---
title: "Blend Shape"
aliases:
  - Shape Key
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Animation]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Blend Shape

## 一句话定义

Blend Shape 是通过混合预设顶点形态来实现表情、变形或局部形状变化的技术。

## 为什么需要它

面部表情、口型、肌肉变形、角色自定义和某些特效变形，很难只靠骨骼完成。Blend Shape 提供了直接控制顶点形态的方式。

## 核心原理

每个 Blend Shape 存储一组顶点偏移，运行时根据权重把多个形态混合到基础网格上。它要求拓扑和顶点顺序稳定。

## 技术美术中的典型用途

- 面部表情和口型。
- 角色体型变化。
- 关节修型。
- 特效模型变形。

## Unity 中的相关场景

Unity Skinned Mesh Renderer 支持 BlendShape 权重控制，可由动画、脚本或 Timeline 驱动。

## Unreal Engine 中的相关场景

Unreal 中相近概念常称 Morph Target，可用于表情、修型和动画曲线驱动。

## 常见误区

1. 修改拓扑后 Blend Shape 失效。
2. Blend Shape 数量过多造成内存和计算成本。
3. 表情形态没有统一命名和范围。

## 面试可能怎么问

### Blend Shape 和骨骼动画有什么区别？

回答要点：骨骼动画通过骨骼矩阵变形，Blend Shape 通过顶点偏移混合形态。前者适合整体关节，后者适合表情和局部形状。

## 实践建议

制作 5 个基础表情 Blend Shape：眨眼、张嘴、微笑、皱眉、鼓腮，并在引擎中用滑条控制。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[建模规范]] | 建模规范偏输入资产质量；本条目可能关注某个具体制作或优化环节。 |
| [[贴图规范]] | 贴图规范偏纹理侧约束；本条目可能覆盖几何、绑定、动画或特效。 |

## 相关条目

- [[Morph Target]]
- [[Skinning]]
- [[角色绑定]]
- [[动画技术]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
