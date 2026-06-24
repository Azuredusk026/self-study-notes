---
title: "CommandBuffer"
aliases:
  - Command Buffer
category: "04_Engine"
tags: [技术美术, Unity, Rendering]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# CommandBuffer

## 一句话定义

CommandBuffer 是记录一组 GPU 渲染命令并在指定时机执行的命令列表。

## 为什么需要它

自定义渲染效果往往需要“在某个阶段画一些东西、拷贝一张图、设置一个 Render Target”。CommandBuffer 让 TA 或图形程序可以把这些操作组织成明确的命令序列。

## 核心原理

CommandBuffer 通常记录 SetRenderTarget、Clear、DrawRenderer、DrawMesh、Blit、SetGlobalTexture 等操作。命令本身不一定立即执行，而是在渲染管线指定位置提交给 GPU。

> 待核验：Unity 不同渲染管线和版本中，CommandBuffer 与 Render Graph、RTHandle、Blit API 的推荐用法可能不同。

## 技术美术中的典型用途

- 自定义后处理。
- 角色描边和遮挡高亮。
- 拷贝相机颜色或深度。
- 生成临时 Mask、Blur、Outline 纹理。

## Unity 中的相关场景

Built-in 管线可以把 CommandBuffer 挂到 CameraEvent 或 LightEvent。URP 中更常通过 ScriptableRenderPass 间接使用命令缓冲。

## Unreal Engine 中的相关场景

Unreal 不以 Unity CommandBuffer 形式暴露给 TA，但底层同样通过渲染命令和 Render Graph 调度 GPU 工作。

## 常见误区

1. 以为 CommandBuffer 会自动管理资源生命周期。
2. 每帧创建大量临时对象，造成 CPU 和 GC 压力。
3. 不清楚执行时机，导致读取还没写好的纹理。

## 面试可能怎么问

### CommandBuffer 适合解决什么问题？

回答要点：适合把一组自定义渲染命令插入到管线指定位置，用于额外绘制、拷贝、后处理或生成中间纹理。

## 实践建议

写一个把角色渲染到单独 RenderTexture 的 CommandBuffer，再把结果合成回主画面。

## 相关条目

- [[URP]]
- [[Render Pass]]
- [[RenderTexture]]
- [[后处理]]

## 参考来源

- 待补充

