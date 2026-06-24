---
title: "Texture Atlas"
aliases:
  - 贴图图集
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Texture]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Texture Atlas

## 定义与解释

Texture Atlas 是把多张小贴图合并到一张大贴图中的技术，用于减少材质切换、批处理成本和采样资源数量。

## 核心原理

Atlas 的核心是把多个 UV 岛或多个资产的纹理区域排布到同一纹理空间。模型材质通过调整 UV 采样对应区域，从而共享同一材质和贴图资源。

Atlas 需要处理 padding、Mip Bleeding、压缩块、旋转缩放、通道一致性和更新粒度。TA 不能只看合并后 Draw Call 下降，还要评估贴图浪费、内存、局部更新和美术迭代成本。

## 用途

- 在资产制作和引擎导入中定位与 Texture Atlas 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Trim Sheet]] | Trim Sheet 是可复用条带纹理；Atlas 是把多个纹理区域打包。 |
| [[Texture Compression]] | Atlas 管布局；压缩管存储格式。 |

## 常见误区

1. Padding 不足导致 Mip 边缘串色。
2. 把更新频率不同的贴图打在一起。
3. 合并贴图后材质参数差异仍导致无法批处理。

## 相关条目

- [[UV]]：Atlas 依赖 UV 重新布局。
- [[Texel Density]]：Atlas 中不同资产仍要控制贴图密度。
- [[Draw Call]]：Atlas 常用于减少材质切换。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
