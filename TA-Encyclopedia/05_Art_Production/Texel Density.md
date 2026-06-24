---
title: "Texel Density"
aliases:
  - 纹素密度
category: "05_Art_Production"
tags: [技术美术, ArtProduction, UV, Texture]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Texel Density

## 定义与解释

Texel Density 是单位模型尺寸对应的纹理像素密度，用来控制不同资产在画面中的贴图清晰度一致性。

## 核心原理

Texel Density 把 UV 面积、模型真实尺寸和贴图分辨率联系起来。相同材质或同一场景中的资产如果密度差异过大，会出现有的清晰、有的模糊的观感不一致。

TA 需要根据镜头距离、资产等级、平台内存和材质类型制定密度标准。Trim Sheet、Atlas、LOD 和虚拟纹理都会改变具体执行方式，但核心仍是让纹理预算服务画面优先级。

## 用途

- 在资产制作和引擎导入中定位与 Texel Density 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Texture Atlas]] | Atlas 组织贴图区域；Texel Density 控制单位面积清晰度。 |
| [[LOD]] | LOD 可随距离降低几何和贴图需求。 |

## 常见误区

1. 所有资产用同一贴图尺寸，不看实际尺寸。
2. UV 缩放随意导致清晰度不一致。
3. 只追求高密度，忽略内存和下载体积。

## 相关条目

- [[UV]]：Texel Density 依赖 UV 展开和缩放。
- [[贴图规范]]：贴图规范应定义密度和分辨率。
- [[Trim Sheet]]：Trim Sheet 需要特殊密度规划。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
