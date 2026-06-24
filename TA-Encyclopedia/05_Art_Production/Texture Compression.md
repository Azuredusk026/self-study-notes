---
title: "Texture Compression"
aliases:
  - 贴图压缩
category: "05_Art_Production"
tags: [技术美术, ArtProduction, Texture, Optimization]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Texture Compression

## 一句话定义

Texture Compression 是把贴图编码成 GPU 可直接采样的压缩格式，以降低显存、包体和带宽成本。

## 为什么需要它

贴图通常是游戏资产中最占空间的部分之一。正确压缩能显著降低内存和加载压力；错误压缩会带来色带、块状伪影、法线错误和透明边缘问题。

## 核心原理

不同平台支持不同压缩格式，例如移动端、PC、主机有不同 GPU 格式。TA 需要根据贴图类型选择格式：颜色、法线、Mask、HDR、UI、透明贴图的要求并不一样。

> 待核验：具体格式选择和平台支持需要按 Unity/Unreal 版本、目标设备和项目设置确认。

## 技术美术中的典型用途

- 控制贴图内存和包体。
- 为 Normal、Mask、UI、HDR 贴图选择不同策略。
- 排查压缩伪影。
- 制定平台导入规则。

## Unity 中的相关场景

Unity Texture Importer 可按平台覆盖格式、尺寸、压缩质量、sRGB 和 Mipmap。TA 常用编辑器工具批量检查。

## Unreal Engine 中的相关场景

Unreal Texture Compression Settings、LOD Group、Texture Streaming 和平台 Cook 设置会影响最终纹理格式。

## 常见误区

1. 所有贴图用同一种压缩格式。
2. Normal Map 压缩错误导致光照异常。
3. UI 图标过度压缩导致边缘脏。

## 面试可能怎么问

### 为什么贴图压缩要按类型区分？

回答要点：颜色、法线、Mask、HDR 和 UI 对颜色空间、精度、Alpha 和伪影容忍度不同，不能套同一规则。

## 实践建议

选一组 BaseColor、Normal、Mask 和 UI 贴图，在目标平台比较不同压缩格式下的内存和画质。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[建模规范]] | 建模规范偏输入资产质量；本条目可能关注某个具体制作或优化环节。 |
| [[贴图规范]] | 贴图规范偏纹理侧约束；本条目可能覆盖几何、绑定、动画或特效。 |

## 相关条目

- [[贴图规范]]
- [[Texture Sampling]]
- [[Mipmap]]
- [[Unity Editor Tool]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
