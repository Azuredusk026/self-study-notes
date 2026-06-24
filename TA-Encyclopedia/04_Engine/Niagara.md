---
title: "Niagara"
aliases: []
category: "04_Engine"
tags: [技术美术, Unreal, VFX]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Niagara

## 一句话定义

Niagara 是 Unreal Engine 的程序化实时特效系统，用于构建粒子、网格、GPU 模拟和数据驱动 VFX。

## 为什么需要它

TA 在 Unreal 项目中经常需要把美术特效变成可复用、可调参、可优化的系统。Niagara 不只是粒子编辑器，它还涉及材质、蓝图、事件、数据接口、LOD、性能预算和团队规范。

## 核心原理

Niagara 通常由 System、Emitter、Module、Parameter 和 Renderer 组成。粒子数据经过 Spawn、Update、Render 阶段，被 Sprite、Mesh、Ribbon 等 Renderer 输出。

> 待核验：Niagara 模块、数据接口和 GPU 模拟能力随 Unreal 版本持续变化，具体功能需要查官方文档。

## 技术美术中的典型用途

- 命中特效、技能轨迹、环境粒子。
- Mesh Particle、Ribbon、Beam。
- GPU 粒子和大量实例特效。
- 特效参数暴露给蓝图或策划。

## Unity 中的相关场景

Unity 中相近方向是 Particle System 和 VFX Graph。TA 可以从“模块化粒子系统”和“GPU 特效图”的角度对比。

## Unreal Engine 中的相关场景

Niagara 与 Material、Blueprint、Sequencer、Gameplay Cue、User Parameter 和性能分析工具紧密相关。

## 常见误区

1. 只追求粒子数量，不控制 Overdraw 和材质复杂度。
2. 所有特效都开 GPU 模拟，忽略平台和交互限制。
3. 参数暴露混乱，导致特效模板不可复用。

## 面试可能怎么问

### Niagara 中 System 和 Emitter 的区别是什么？

回答要点：System 是一个完整特效资产容器，可以包含多个 Emitter；Emitter 定义某一类粒子的生成、更新和渲染逻辑。

## 实践建议

做一个命中特效模板：包含火花、冲击波、烟尘三个 Emitter，并暴露颜色、尺寸、持续时间参数。

## 相关条目

- [[VFX]]
- [[Overdraw]]
- [[Texture Sampling]]
- [[Unreal_Engine|Unreal Engine]]

## 参考来源

- 待补充
