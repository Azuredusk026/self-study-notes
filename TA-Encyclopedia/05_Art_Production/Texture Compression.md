---
title: "Texture Compression"
aliases:
  - 贴图压缩
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Texture, Optimization]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Texture Compression

## 定义与解释

Texture Compression 是把贴图用 GPU 可采样压缩格式存储，以降低显存、带宽和包体成本的技术。

## 核心原理

纹理压缩通常按固定块编码颜色或数据，GPU 可以直接采样压缩格式。不同平台支持 BC、ETC、ASTC、PVRTC 等格式，质量、体积、透明通道和法线贴图表现不同。

TA 需要按贴图语义选择压缩：颜色贴图、法线、Mask、HDR、UI 和 SDF 的容错不同。压缩不是越小越好，错误格式会造成色带、块状伪影、法线噪声或遮罩阈值错误。

## 用途

- 在资产制作和引擎导入中定位与 Texture Compression 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Mipmap]] | Mipmap 管距离级别；Texture Compression 管存储和带宽。 |
| [[Texture Atlas]] | Atlas 组织贴图布局；压缩决定存储格式。 |

## 常见误区

1. 所有贴图使用同一压缩格式。
2. Mask 贴图压缩后阈值不稳定。
3. 只在 PC 上看效果，不验证移动端格式。

## 相关条目

- [[贴图规范]]：贴图规范应定义平台压缩格式。
- [[Normal Map]]：法线贴图需要适合方向数据的压缩方式。
- [[Texture Sampling]]：压缩格式会影响采样结果和带宽。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
