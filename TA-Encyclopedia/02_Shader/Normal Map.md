---
title: "Normal Map"
aliases:
  - 法线贴图
category: "Shader"
tags: [技术美术, Shader, Texture, Lighting]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Normal Map

## 一句话定义

Normal Map 用纹理存储表面法线扰动，让低模在光照中表现出更多细节。

## 为什么需要它

游戏资产不能无限增加面数。法线贴图让低模在不改变轮廓的情况下表现高模细节，是角色、道具、场景和材质生产的基础。TA 需要处理切线空间、通道方向、压缩格式和导入设置。

## 核心原理

- 输入：法线贴图、模型切线空间、片元基础法线。
- 处理过程：将贴图颜色解码为方向，再从 Tangent Space 转换到 World/View Space 参与光照。
- 输出：扰动后的法线方向。
- 所在层级：Fragment Shader 光照计算。

## 技术美术中的典型用途

- 高模到低模 Baking。
- PBR 材质细节。
- 角色皮肤、布料、硬表面刻线。
- 排查接缝、翻绿通道、压缩伪影。

## Unity 中的相关场景

Unity 导入纹理时需要设置 Texture Type 为 Normal Map。不同平台压缩格式和 Y 通道方向会影响最终光照。

## Unreal Engine 中的相关场景

Unreal 通常自动识别 Normal 压缩设置，材质中接入 Normal 输入。若来自不同 DCC 或烘焙工具，需要确认 DirectX/OpenGL 法线方向。

## 常见误区

1. 法线贴图会改变模型轮廓：它只影响光照，不改变几何边界。
2. 忽略切线空间一致性，导致接缝或高光断裂。
3. 把 Normal Map 当 sRGB 颜色处理。

## 面试可能怎么问

### Tangent Space Normal Map 为什么常用？

回答要点：它可以随模型变形和旋转使用，适合角色动画和通用材质；但依赖正确的切线、法线和副切线基底。

## 实践建议

用同一低模分别导入 DirectX 和 OpenGL 法线贴图，观察绿通道翻转对光照方向的影响。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Graph]] | Material Graph 偏节点化编辑；本条目可能涉及更底层的代码、编译和采样细节。 |
| [[Texture Sampling]] | Texture Sampling 是常见操作；本条目可能覆盖更完整的 Shader 结构或控制策略。 |

## 相关条目

- [[Tangent Space]]
- [[Texture Sampling]]
- [[PBR]]
- [[Baking]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
