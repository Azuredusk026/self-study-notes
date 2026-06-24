---
title: "Niagara"
aliases: []
category: "04_Engine"
tags: [技术美术, Unreal, VFX]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Niagara

## 定义与解释

Niagara 是 Unreal 的 VFX 和粒子系统，用于构建粒子、网格粒子、GPU 模拟、事件和复杂特效模块。

## 核心原理

Niagara 的核心是以 System、Emitter、Module 和 Parameter 组织特效逻辑。模块在 Spawn、Update、Render 等阶段修改粒子属性，参数可以来自用户、蓝图、材质或数据接口。

TA 需要关注特效表现和运行时成本之间的平衡：粒子数量、GPU/CPU 模拟、排序、碰撞、材质复杂度、透明 Overdraw、LOD 和平台裁剪都会影响性能。参数命名和模块复用也决定特效团队是否能稳定生产。

## 用途

- 在引擎项目中定位与 Niagara 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Editor]] | Material Editor 定义粒子材质；Niagara 定义粒子行为和发射逻辑。 |
| [[VFX]] | VFX 是美术效果领域；Niagara 是 Unreal 中的实现系统。 |

## 常见误区

1. 只看粒子数量，不看透明 Overdraw 和材质复杂度。
2. 所有效果都开 GPU 模拟而不评估平台限制。
3. 参数和模块没有规范，导致复用困难。

## 相关条目

- [[Unreal_Engine]]：Niagara 是 Unreal 特效系统。
- [[Blueprint]]：Blueprint 可驱动 Niagara 参数。
- [[Alpha Blend]]：粒子材质常涉及透明混合和 Overdraw。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
