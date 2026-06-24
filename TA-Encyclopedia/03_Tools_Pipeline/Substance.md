---
title: "Substance"
aliases: []
category: "03_Tools_Pipeline"
confidence: medium
tags: [dcc, substance, texture]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# Substance

## 定义与解释

Substance 是常用于程序化材质、贴图绘制和材质库管理的工具生态，通常指 Substance 3D Painter、Designer 等内容生产工具。

## 核心原理

Substance 管线的核心是把材质通道、图层、程序化节点和导出模板组织成可复用资产生产流程。Painter 更偏单资产绘制，Designer 更偏程序化材质和节点生成。

TA 需要关注导出模板、通道命名、颜色空间、分辨率、位深、压缩前数据和引擎材质输入对应关系。PBR 项目中，Base Color、Normal、Roughness、Metallic、AO 等通道必须和 Unity/Unreal 材质规范一致。

## 用途

- 把 Substance 纳入资产生产、检查、导出、导入或版本管理流程，减少人工操作和沟通成本。
- 把团队规范转成可执行规则、工具入口或自动化报告，让问题尽早暴露。
- 连接 DCC、引擎、版本库和 CI/CD，让美术资产从制作到落地有可追踪的状态。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Houdini]] | Houdini 偏几何和程序化生成；Substance 偏材质和纹理生产。 |
| [[贴图规范]] | Substance 是生产工具；贴图规范定义输出如何被项目使用。 |

## 常见误区

1. 导出模板和引擎材质输入不一致。
2. 把数据贴图按 sRGB 导出或导入。
3. 不同美术使用不同模板，导致通道语义混乱。

## 相关条目

- [[PBR]]：Substance 输出通常服务 PBR 材质。
- [[贴图规范]]：贴图通道和导出格式需要规范。
- [[Texture Sampling]]：引擎中采样这些贴图时要保持语义一致。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
