---
title: "Texture Atlas"
aliases:
  - 贴图图集
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Texture]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Texture Atlas

## 一句话定义

Texture Atlas 是把多张小贴图合并到一张大贴图中，以减少材质或采样切换成本的方法。

## 为什么需要它

UI、场景小物件、粒子和模块化资产常有很多小图。图集能降低资源绑定和 Draw Call 压力，但也会增加 UV 管理、Mipmap 串色和局部更新复杂度。

## 核心原理

多个纹理区域被打包进一张大图，模型或 UI 通过对应 UV 区域采样。需要 padding、统一格式和合理分辨率。

## 技术美术中的典型用途

- UI 图集。
- 粒子序列或 Flipbook。
- 小道具贴图合并。
- 与 Trim Sheet、Mask Map 做资源复用。

## Unity 中的相关场景

Unity UI Sprite Atlas、粒子 Flipbook 和场景图集都与 Texture Atlas 思路相关。

## Unreal Engine 中的相关场景

Unreal 中可用于 UI、Flipbook、材质贴图合并和部分移动端优化。

## 常见误区

1. 图集过大导致内存浪费。
2. padding 不足导致 Mipmap 串色。
3. 把更新频率不同的贴图合进同一图集。

## 面试可能怎么问

### Texture Atlas 和 Trim Sheet 有什么区别？

回答要点：Atlas 更强调把多张贴图合并减少切换；Trim Sheet 更强调可复用条带和模块化建模贴图设计。

## 实践建议

把一组 UI 图标打成图集，检查边缘 padding、压缩格式和不同缩放下的清晰度。

## 相关条目

- [[Trim Sheet]]
- [[Texel Density]]
- [[Mipmap]]
- [[Texture Compression]]

## 参考来源

- 待补充

