---
title: "Tangent Space"
aliases:
  - 切线空间
category: "Shader"
tags: [技术美术, Shader, Math]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Tangent Space

## 定义与解释

Tangent Space 是以表面法线、切线和副切线组成的局部坐标空间。它常用于法线贴图，使贴图中的方向能随模型表面和动画正确变化。

## 核心原理

Tangent Space 的基底通常由 Normal、Tangent、Bitangent 组成，形成 TBN 矩阵。Shader 采样 Normal Map 后，会把贴图中的局部方向通过 TBN 转换到 World 或 View Space 参与光照。

切线空间的可靠性依赖模型 UV、切线生成算法、镜像 UV、DCC 烘焙工具和引擎导入设置一致。只要烘焙和引擎使用的切线基底不同，就可能出现接缝、高光断裂或绿通道方向错误。

## 用途

- 在材质或 Shader 调试中定位与 Tangent Space 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Object Space]] | Object Space 依附模型整体；Tangent Space 依附表面局部基底。 |
| [[View Space]] | View Space 以相机为参考；Tangent Space 以表面为参考。 |

## 常见误区

1. 忽略 DCC 和引擎切线基底不一致。
2. 镜像 UV 没处理好导致法线接缝。
3. 把 Tangent Space Normal 当作 World Space 方向使用。

## 相关条目

- [[Normal Map]]：切线空间是法线贴图最常见的解释空间。
- [[Object Space]]：Object Space 是模型整体局部空间。
- [[World Space]]：Tangent Space 法线常转换到 World Space 参与光照。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
