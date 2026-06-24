---
title: "ScriptableRendererFeature"
aliases:
  - Renderer Feature
category: "04_Engine"
tags: [技术美术, Unity, URP, Rendering]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# ScriptableRendererFeature

## 一句话定义

ScriptableRendererFeature 是 URP 中用于向 Renderer 注入自定义 Render Pass 的扩展入口。

## 为什么需要它

TA 做 URP 项目时，常要实现描边、遮挡高亮、自定义后处理、角色 Mask、模糊或特殊渲染层。Renderer Feature 是这些效果进入 URP 管线的常用方式。

## 核心原理

Renderer Feature 创建并配置一个或多个 ScriptableRenderPass，在指定渲染事件执行，读取或写入颜色、深度、临时 RenderTexture 等资源。

> 待核验：Unity 不同版本中 Render Graph、Blit、RTHandle 和 Compatibility Mode 的推荐写法不同。

## 技术美术中的典型用途

- 角色描边和交互高亮。
- 自定义后处理。
- 分层渲染 Mask。
- 屏幕空间效果调试。

## Unity 中的相关场景

在 URP Renderer Data 中添加 Feature，配置执行时机和材质。TA 需要关注目标平台、Pass 顺序、临时纹理释放和 Scene/Game View 差异。

## Unreal Engine 中的相关场景

Unreal 中类似需求常通过 Post Process Material、Custom Depth、材质域或渲染插件实现。

## 常见误区

1. 不清楚 Pass 插入时机，读取到错误的相机颜色。
2. 每帧创建临时资源但不释放。
3. 用全屏 Pass 解决本可局部处理的问题。

## 面试可能怎么问

### URP 里如何做一个自定义描边？

回答要点：可用 Renderer Feature 注入 Pass，先写 Mask 或法线/深度，再用全屏 Pass 做边缘检测并合成。

## 实践建议

实现一个“选中物体描边”Renderer Feature，支持 Layer 过滤、颜色参数和开关。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Unity]] | Unity 是引擎平台；本条目可能是其中某个系统或工作流。 |
| [[Unreal_Engine]] | Unreal 是引擎平台；本条目可能与其对应系统形成实现差异。 |

## 相关条目

- [[URP]]
- [[Render Pass]]
- [[CommandBuffer]]
- [[RenderTexture]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
