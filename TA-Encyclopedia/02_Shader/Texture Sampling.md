---
title: "Texture Sampling"
aliases:
  - 纹理采样
category: "Shader"
tags: [技术美术, Shader, Texture]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Texture Sampling

## 一句话定义

Texture Sampling 是 Shader 根据 UV 或其他坐标从纹理中读取颜色或数据的过程。

## 为什么需要它

游戏材质的大量信息来自纹理：Base Color、Normal、Roughness、Metallic、AO、Mask、Flow Map、Noise。TA 需要理解采样坐标、过滤、Mipmap、颜色空间和通道打包，否则贴图看起来正确也可能在引擎中出错。

## 核心原理

- 输入：纹理资源、采样器状态、UV、LOD 或偏导信息。
- 处理过程：按 Wrap、Filter、Mipmap 规则读取一个或多个 texel 并插值。
- 输出：采样值，可能代表颜色、法线、遮罩或任意数据。
- 所在层级：Fragment Shader、Vertex Shader 或 Compute Shader。

## 技术美术中的典型用途

- 材质贴图采样。
- Mask Map 和 ORM 通道读取。
- Flow Map、Dissolve、噪声扰动。
- 后处理读取 Scene Color、Depth、Normal。

## Unity 中的相关场景

Unity Shader Graph 使用 Sample Texture 2D 节点；HLSL 中常见 `SAMPLE_TEXTURE2D`。导入设置中的 sRGB、Wrap Mode、Filter Mode、Mipmap 会直接影响采样结果。

## Unreal Engine 中的相关场景

Unreal Material Graph 使用 Texture Sample 节点。Sampler Source、Compression Settings、sRGB、Mip Gen Settings 会影响材质表现和性能。

## 常见误区

1. 把所有贴图都当 sRGB：Normal、Roughness、Metallic、Mask 通常应按线性数据处理。
2. 忽略 Mipmap 导致远处闪烁。
3. 过度采样高分辨率贴图，增加带宽压力。

## 面试可能怎么问

### 为什么法线贴图不能按普通颜色贴图处理？

回答要点：法线贴图存储方向数据，不是颜色；如果开启 sRGB 会改变数值分布，导致光照错误。

## 实践建议

在同一材质中切换 sRGB、Filter 和 Mipmap 设置，观察颜色贴图、Mask 贴图和法线贴图的差异。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Graph]] | Material Graph 偏节点化编辑；本条目可能涉及更底层的代码、编译和采样细节。 |
| [[Texture Sampling]] | Texture Sampling 是常见操作；本条目可能覆盖更完整的 Shader 结构或控制策略。 |

## 相关条目

- [[UV与贴图采样]]
- [[Normal Map]]
- [[Mipmap]]
- [[Fragment Shader]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
