---
title: "Depth Buffer"
aliases:
  - 深度缓冲
category: "Rendering"
tags: [技术美术, Rendering, Depth]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---



# Depth Buffer

## 定义与解释

Depth Buffer 是记录屏幕像素对应深度值的缓冲，用于判断片元之间的前后遮挡关系。它是 Z-Test、Early-Z、阴影、后处理和许多屏幕空间效果的基础。

## 核心原理

Depth Buffer 存储的通常不是线性世界距离，而是经过投影变换后的深度值。透视投影下深度精度分布不均，Near Plane 越近，远处可用精度越差，容易出现 Z-Fighting。

深度缓冲的价值不只在可见性判断。后处理会用它重建位置或判断边缘，SSAO、Depth of Field、雾效、描边和软粒子都会依赖深度语义。TA 需要知道当前管线的深度范围、反向 Z、深度纹理生成时机和透明物体是否写深度。

## 用途

- 在渲染调试中定位与 Depth Buffer 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Framebuffer]] | Framebuffer 是一组渲染附件；Depth Buffer 是其中的深度附件。 |
| [[Render Target]] | Render Target 常指颜色输出；Depth Buffer 专门记录深度。 |

## 常见误区

1. 把深度值当作线性距离直接使用。
2. Near/Far Plane 设置不合理导致深度精度不足。
3. 忽略透明物体通常不写深度，导致屏幕空间效果缺失或穿帮。

## 相关条目

- [[Z-Test]]：Z-Test 读取 Depth Buffer 判断片元是否通过。
- [[Early-Z]]：Early-Z 依赖深度提前剔除片元。
- [[Depth of Field]]：DoF 使用深度估计离焦程度。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
