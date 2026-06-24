---
title: "Mipmap"
aliases: []
category: "02_Shader"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Mipmap

## 定义与解释

Mipmap 是同一纹理的多级缩小版本，用于在远距离或小屏幕覆盖时采样合适分辨率。它减少闪烁、锯齿和带宽浪费，是纹理采样质量的基础机制。

## 核心原理

GPU 根据纹理坐标在屏幕上的变化率估算需要的 LOD，再从对应 Mip 级别采样。距离远、表面倾斜或屏幕占比小时，会选择更小的 Mip，必要时进行双线性或三线性过滤。

Mipmap 的问题在于它会混合纹理信息。颜色贴图通常受益明显，但 Mask、UI、法线、SDF 和通道打包贴图需要特殊生成策略。TA 需要检查 Mip 生成、锐化、边缘扩展、Streaming 和各平台压缩。

## 用途

- 在材质或 Shader 调试中定位与 Mipmap 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Texture Sampling]] | Texture Sampling 是读取过程；Mipmap 是选择合适纹理级别的机制。 |
| [[Texture Compression]] | 压缩改变存储格式；Mipmap 改变距离级别。 |

## 常见误区

1. 为所有纹理关闭 Mipmap 导致远处闪烁。
2. Mask 或 SDF 的 Mip 生成策略错误导致边界变形。
3. 忽略纹理 Streaming 造成低清或显存压力。

## 相关条目

- [[Texture Sampling]]：Mipmap 是纹理采样 LOD 机制。
- [[Normal Map]]：法线贴图 Mip 处理会影响远处光照。
- [[Precision]]：采样 LOD 和压缩精度共同影响结果。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
