---
title: "Custom Depth"
aliases:
  - CustomDepth
category: "04_Engine"
tags: [技术美术, Unreal, Rendering]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Custom Depth

## 一句话定义

Custom Depth 是 Unreal 中把指定物体写入独立深度缓冲，用于后处理和特殊遮罩的机制。

## 为什么需要它

角色描边、交互物高亮、遮挡透视、队友轮廓和选择框常需要知道“哪些物体属于特殊对象”。Custom Depth 提供了比直接扫描场景颜色更稳定的对象遮罩入口。

## 核心原理

被启用 Custom Depth 的物体会在额外深度通道中写入深度值。后处理材质可以读取 CustomDepth 或 CustomStencil，与 SceneDepth 比较后生成描边、遮挡或高亮。

> 待核验：Custom Depth/Stencil 的项目设置、透明材质写入能力和平台支持需按 Unreal 版本确认。

## 技术美术中的典型用途

- 交互物描边。
- 被墙遮挡角色轮廓。
- 队伍颜色或目标高亮。
- 后处理 Mask 分层。

## Unity 中的相关场景

Unity 中可通过单独 Layer、Renderer Feature、Depth/Mask RenderTexture 做类似对象遮罩。

## Unreal Engine 中的相关场景

需要在 Mesh 设置中开启 Render CustomDepth Pass，并在 Post Process Material 中采样 CustomDepth/CustomStencil。

## 常见误区

1. 忘记在项目设置中启用 Stencil 或相关缓冲选项。
2. 只比较 CustomDepth，不处理物体被遮挡和未遮挡两种情况。
3. 大量对象写 Custom Depth 增加额外 Pass 成本。

## 面试可能怎么问

### Unreal 如何实现角色描边？

回答要点：常见方案是让目标物体写 Custom Depth/Stencil，再用后处理材质做边缘检测或深度比较生成轮廓。

## 实践建议

做一个可交互物描边效果，使用 Custom Stencil 区分不同颜色。

## 相关条目

- [[Depth Buffer]]
- [[后处理]]
- [[Unreal_Engine|Unreal Engine]]
- [[Render Pass]]

## 参考来源

- 待补充
