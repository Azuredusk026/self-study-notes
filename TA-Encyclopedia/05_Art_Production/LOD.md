---
title: "LOD"
aliases:
  - Level of Detail
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Optimization]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# LOD

## 一句话定义

LOD 是根据观察距离、屏幕占比或性能需求切换不同细节级别资产的优化方法。

## 为什么需要它

远处物体不需要和近处一样的面数、材质复杂度和贴图分辨率。LOD 能降低顶点、片元、骨骼、材质和内存成本，是大场景和移动端优化的基础策略。

## 核心原理

LOD 通常准备多个版本：LOD0 最高质量，后续逐级减少面数、材质槽、骨骼或贴图成本。引擎按距离或屏幕占比切换。

## 技术美术中的典型用途

- 场景静态物优化。
- 角色远距离简化。
- 植被和建筑群优化。
- 与 Occlusion、Frustum Culling、HLOD 配合。

## Unity 中的相关场景

Unity 使用 LOD Group 控制多个 Renderer 的切换比例。TA 需要关注切换突变、阴影 LOD 和资源导入。

## Unreal Engine 中的相关场景

Unreal Static Mesh 和 Skeletal Mesh 都支持 LOD。大型场景还会涉及 HLOD、Nanite 和平台特定策略。

## 常见误区

1. LOD 只减面，不减材质和贴图成本。
2. 切换距离设置不合理，产生明显跳变。
3. LOD 版本法线、UV 或材质不一致，导致闪烁。

## 面试可能怎么问

### LOD 优化能降低哪些成本？

回答要点：可以降低顶点处理、片元覆盖、材质复杂度、骨骼计算、贴图内存和 Draw Call 相关成本，具体取决于 LOD 设计。

## 实践建议

给一个树模型制作 3 级 LOD，并记录每级三角面、材质数量和切换屏幕比例。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[建模规范]] | 建模规范偏输入资产质量；本条目可能关注某个具体制作或优化环节。 |
| [[贴图规范]] | 贴图规范偏纹理侧约束；本条目可能覆盖几何、绑定、动画或特效。 |

## 相关条目

- [[Low Poly]]
- [[Frustum Culling]]
- [[Overdraw]]
- [[建模规范]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
