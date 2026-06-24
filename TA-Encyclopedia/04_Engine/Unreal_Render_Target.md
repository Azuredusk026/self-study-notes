---
title: "Unreal Render Target"
aliases:
  - Unreal Render Target
category: "04_Engine"
tags: [技术美术, Unreal, Rendering]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Unreal Render Target

## 一句话定义

Render Target 是 Unreal 中可被相机、材质或蓝图写入并再次采样的渲染目标资源。

## 为什么需要它

小地图、监控屏、绘制到纹理、动态遮罩、角色预览和交互式材质都需要中间纹理。Render Target 是实现这些效果的基础资源。

## 核心原理

Scene Capture、Canvas、材质或渲染流程可以把颜色写入 Render Target。后续材质可像普通贴图一样读取它。

## 技术美术中的典型用途

- 小地图和监控屏。
- 动态绘制遮罩。
- UI 角色预览。
- Niagara 或材质数据交互。

## Unity 中的相关场景

Unity 中对应概念是 [[RenderTexture]]。

## Unreal Engine 中的相关场景

常与 Scene Capture 2D、Blueprint、Material 和 UMG 配合使用。需要关注分辨率、格式、更新频率和内存。

## 常见误区

1. 每帧高分辨率更新，成本过高。
2. 忘记 Render Target 格式和颜色空间。
3. 用 Render Target 保存本可用参数表达的简单状态。

## 面试可能怎么问

### Render Target 可以做哪些 TA 效果？

回答要点：小地图、动态遮罩、屏幕显示器、角色预览、绘制轨迹和材质交互。

## 实践建议

做一个角色脚印系统，把移动轨迹写入 Render Target，再在地面材质中采样显示。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Unity]] | Unity 是引擎平台；本条目可能是其中某个系统或工作流。 |
| [[Unreal_Engine]] | Unreal 是引擎平台；本条目可能与其对应系统形成实现差异。 |

## 相关条目

- [[RenderTexture]]
- [[Post Process Material]]
- [[Blueprint]]
- [[Material Editor]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
