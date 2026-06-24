---
title: "Trim Sheet"
aliases:
  - 条带贴图
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Texture]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Trim Sheet

## 定义与解释

Trim Sheet 是把可重复使用的边条、倒角、面板和装饰细节集中在一张贴图中，供多个模型共享的纹理制作方法。

## 核心原理

Trim Sheet 的核心是用模型 UV 对齐到贴图中的条带区域，而不是为每个资产单独绘制完整贴图。它适合硬表面、建筑、科幻面板和模块化场景。

TA 需要规划条带比例、Texel Density、材质参数、法线方向和模块化资产 UV 规则。Trim Sheet 能显著提高复用率，但会限制独特脏污、破损和局部变化，需要结合顶点色、Mask 或 Decal 弥补。

## 用途

- 在资产制作和引擎导入中定位与 Trim Sheet 相关的质量、性能或表现问题。
- 把美术制作约定转成可检查的命名、尺寸、通道、骨骼、LOD 或导入规则。
- 帮助美术、TA 和程序在视觉质量、生产效率和运行时预算之间取得稳定平衡。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Texture Atlas]] | Atlas 打包多个独立区域；Trim Sheet 设计可重复条带和装饰。 |
| [[建模规范]] | Trim Sheet 需要模型模块和 UV 规范配合。 |

## 常见误区

1. 条带设计和模型尺度不匹配。
2. 所有资产都用同一 Trim，导致重复感明显。
3. 忽略法线方向和 UV 旋转造成光照不一致。

## 相关条目

- [[UV]]：Trim Sheet 依赖精确 UV 对齐。
- [[Texel Density]]：条带复用需要统一密度。
- [[Texture Atlas]]：两者都复用贴图空间但设计目标不同。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
