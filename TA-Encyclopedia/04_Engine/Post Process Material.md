---
title: "Post Process Material"
aliases:
  - 后处理材质
category: "04_Engine"
tags: [技术美术, Unreal, PostProcessing]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Post Process Material

## 一句话定义

Post Process Material 是 Unreal 中在后处理阶段执行的材质，用于基于屏幕数据修改最终画面。

## 为什么需要它

描边、X-Ray、屏幕扭曲、风格化颜色、深度雾和特殊镜头效果都常通过后处理材质实现。TA 需要理解它读取的是屏幕空间数据，而不是单个物体材质。

## 核心原理

后处理材质通常读取 Scene Color、Scene Depth、Custom Depth、GBuffer 或屏幕 UV，并输出修改后的屏幕颜色。

## 技术美术中的典型用途

- Custom Depth 描边。
- 屏幕空间风格化。
- 角色遮挡高亮。
- 演出镜头效果。

## Unity 中的相关场景

Unity URP/HDRP 中相近需求通常用 Renderer Feature、Custom Pass 或后处理 Volume 实现。

## Unreal Engine 中的相关场景

通过 Post Process Volume 或相机设置挂载材质，Blendable Location 决定执行时机。

## 常见误区

1. 期望后处理材质知道完整物体拓扑。
2. 忽略全屏 Pass 成本。
3. SceneDepth 和 CustomDepth 比较空间理解错误。

## 面试可能怎么问

### Unreal 后处理描边常用哪些数据？

回答要点：常用 SceneDepth、CustomDepth、CustomStencil 或法线/GBuffer 数据做边缘检测，再在后处理阶段合成轮廓。

## 实践建议

实现一个 Custom Stencil 多颜色描边后处理，并用参数控制线宽。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Unity]] | Unity 是引擎平台；本条目可能是其中某个系统或工作流。 |
| [[Unreal_Engine]] | Unreal 是引擎平台；本条目可能与其对应系统形成实现差异。 |

## 相关条目

- [[Custom Depth]]
- [[Material Editor]]
- [[Depth Buffer]]
- [[后处理]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
