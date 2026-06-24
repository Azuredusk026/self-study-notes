---
title: "UV"
aliases: []
category: "05_Art_Production"
confidence: medium
tags: [art-production, uv]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# UV

## 定义与解释

UV 是模型表面映射到二维纹理空间的坐标系统，用于贴图采样、烘焙、Lightmap、Trim Sheet 和材质遮罩。

## 核心原理

UV 的核心是把三维表面展开成二维区域。展开方式决定贴图拉伸、接缝位置、纹理密度、烘焙边界和 Mipmap 质量。

不同用途需要不同 UV：材质贴图强调少拉伸和可绘制，Lightmap 强调不重叠和 padding，Trim Sheet 强调对齐条带，Atlas 强调空间利用。TA 需要把 UV 规范和贴图规范、烘焙流程、导入设置绑定。

## 用途

- 在资产制作和引擎导入中定位与 UV 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Texture Atlas]] | UV 是坐标；Atlas 是贴图空间组织方式。 |
| [[Trim Sheet]] | Trim Sheet 是特殊 UV 使用策略。 |

## 常见误区

1. UV 拉伸只在 DCC 中看，不进引擎验证。
2. Lightmap UV 和材质 UV 混用。
3. Padding 不足导致 Mip 出血和烘焙接缝。

## 相关条目

- [[Texture Sampling]]：Shader 通过 UV 采样贴图。
- [[Texel Density]]：UV 面积决定贴图密度。
- [[Baking]]：烘焙依赖稳定 UV 和 padding。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
