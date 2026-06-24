---
title: "Z-Test"
aliases:
  - Depth Test
  - 深度测试
category: "Rendering"
tags: [技术美术, Rendering, Depth]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Z-Test

## 一句话定义

Z-Test 是用片元深度和 Depth Buffer 中已有深度比较，判断该片元是否可见的测试。

## 为什么需要它

没有 Z-Test，后绘制的物体会错误覆盖先绘制的物体。TA 需要理解 Z-Test 才能正确处理透明、描边、遮挡高亮、深度预通道和特殊材质。

## 核心原理

- 输入：当前片元深度、Depth Buffer 深度、比较函数。
- 处理过程：按 Less、LEqual、Greater、Always 等规则判断。
- 输出：通过则继续写颜色或深度，失败则丢弃片元。
- 所在层级：GPU 固定功能阶段。

## 技术美术中的典型用途

- 控制 X-Ray、遮挡轮廓、透视高亮。
- 透明物体排序和深度写入策略。
- 深度预通道配合 Early-Z 降低片元成本。

## Unity 中的相关场景

ShaderLab 中可通过 `ZTest`、`ZWrite`、`Queue` 控制深度行为。URP/HDRP 自定义 Shader 也需要明确深度状态。

## Unreal Engine 中的相关场景

Unreal 材质和渲染设置封装了大部分深度行为，Custom Depth、Disable Depth Test、Translucency Sort Priority 常用于特殊效果。

## 常见误区

1. 把 Z-Test 和 ZWrite 混为一谈：前者是测试，后者是写入。
2. 透明材质开启 ZWrite 后可能导致后续透明层被错误遮挡。
3. Always 不是免费，它可能增加无意义的片元写入。

## 面试可能怎么问

### Z-Test 和 ZWrite 有什么区别？

回答要点：Z-Test 决定片元是否通过深度比较；ZWrite 决定通过后是否更新 Depth Buffer。

## 实践建议

写三个材质分别设置 ZTest LEqual、Greater、Always，观察遮挡显示和透视效果差异。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[PBR]] | 更偏材质和光照模型；本条目更关注具体渲染环节或画面效果。 |
| [[Shader基础]] | Shader 是实现手段；本条目通常还涉及管线状态、缓冲读写和引擎配置。 |

## 相关条目

- [[Depth Buffer]]
- [[Early-Z]]
- [[Alpha Blend]]
- [[Render Pass]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
