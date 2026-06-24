---
title: "UV与贴图采样"
aliases: []
category: "02_Shader"
confidence: medium
tags: [shader, uv, texture]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# UV与贴图采样

## 定义与解释

UV 与贴图采样描述模型表面二维坐标如何映射到纹理，并在 Shader 中被用来读取贴图数据。它连接 DCC 展 UV、贴图绘制、引擎导入和材质表现。

## 核心原理

UV 是每个顶点或片元携带的二维坐标，光栅化后在三角形内部插值。Shader 使用插值后的 UV 采样纹理，再根据纹理语义参与颜色、法线、遮罩或效果计算。

UV 问题通常跨越美术和 Shader：拉伸、接缝、重叠、密度不一致、Wrap、Tiling、Offset、Mip Bleeding 都会改变最终采样结果。TA 需要同时检查模型 UV、纹理边缘扩展、导入设置和材质节点。

## 用途

- 在材质或 Shader 调试中定位与 UV与贴图采样 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Texture Sampling]] | UV 是采样坐标；Texture Sampling 是读取纹理的过程。 |
| [[Texel Density]] | Texel Density 管贴图密度规范；UV 采样管坐标和读取结果。 |

## 常见误区

1. 只看贴图本身，不检查 UV 拉伸和接缝。
2. 忽略纹理边缘扩展导致 Mip 出血。
3. 多套 UV 用途混乱，导致光照贴图、材质贴图或特效采样错位。

## 相关条目

- [[Texture Sampling]]：UV 是纹理采样的主要坐标。
- [[Mipmap]]：UV 密度和 Mip 选择影响远处质量。
- [[UV]]：美术生产中的 UV 规范与 Shader 采样直接相关。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
