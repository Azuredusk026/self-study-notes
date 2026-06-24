---
title: "RenderTexture"
aliases:
  - Render Texture
category: "04_Engine"
tags: [技术美术, Unity, Rendering]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# RenderTexture

## 一句话定义

RenderTexture 是 Unity 中可作为渲染输出目标并可被后续采样的纹理资源。

## 为什么需要它

很多 TA 效果都需要中间图：小地图、角色头像、后处理、模糊、描边 Mask、场景捕捉、UI 预览、深度或法线缓存。RenderTexture 是 Unity 中承载这些中间结果的常用资源。

## 核心原理

相机、CommandBuffer 或 Render Pass 可以把颜色、深度等输出写入 RenderTexture。后续 Shader 再把它作为普通纹理采样。

## 技术美术中的典型用途

- 小地图和监视器画面。
- Bloom、Blur、Outline 等后处理。
- UI 角色预览。
- 低分辨率特效缓冲。
- 与 [[Render Target]] 和 [[Framebuffer]] 概念对应。

## Unity 中的相关场景

常见参数包括分辨率、颜色格式、深度位数、MSAA、sRGB、MipMap 和生命周期管理。移动端尤其需要控制格式和尺寸。

## Unreal Engine 中的相关场景

Unreal 中相近概念是 Render Target 资源，可被 Scene Capture、材质和蓝图使用。

## 常见误区

1. 使用全分辨率 HDR RenderTexture 做所有中间效果。
2. 忘记释放临时 RenderTexture。
3. 颜色空间、格式或深度配置错误导致画面偏色或不可采样。

## 面试可能怎么问

### RenderTexture 和普通 Texture 有什么区别？

回答要点：RenderTexture 可以作为渲染输出目标，普通 Texture 更多作为资源输入；RenderTexture 写入后也可以被 Shader 采样。

## 实践建议

做一个半分辨率模糊 Pass，对比全分辨率和半分辨率的性能与画质。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Unity]] | Unity 是引擎平台；本条目可能是其中某个系统或工作流。 |
| [[Unreal_Engine]] | Unreal 是引擎平台；本条目可能与其对应系统形成实现差异。 |

## 相关条目

- [[CommandBuffer]]
- [[Render Target]]
- [[Bloom]]
- [[后处理]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
