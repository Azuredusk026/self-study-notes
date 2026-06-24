---
title: "MaterialPropertyBlock"
aliases: []
category: "04_Engine"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# MaterialPropertyBlock

## 定义与解释

MaterialPropertyBlock 是 Unity 中按 Renderer 覆盖材质参数的机制，常用于在不复制材质的情况下给不同对象设置颜色、数值或纹理。

## 核心原理

它的核心是把 per-renderer 参数单独传给渲染器，而不修改共享材质资源。这样多个对象可以使用同一材质和 Shader，同时拥有不同显示参数。

TA 需要理解它对批处理、SRP Batcher、GPU Instancing 和材质实例化的影响。频繁创建、滥用纹理覆盖或与实例化数据混用，都可能破坏预期优化或增加管理复杂度。

## 用途

- 在引擎项目中定位与 MaterialPropertyBlock 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Instance]] | Material Instance 是 Unreal 的实例化材质资产；MaterialPropertyBlock 是 Unity 的渲染器参数覆盖。 |
| [[SRP Batcher]] | SRP Batcher 优化材质常量绑定；MPB 可能改变参数更新路径。 |

## 常见误区

1. 为了改颜色复制材质，造成材质资源膨胀。
2. 每帧频繁 new MaterialPropertyBlock。
3. 使用 MPB 后没有确认批处理是否仍然生效。

## 相关条目

- [[Unity]]：MaterialPropertyBlock 是 Unity 渲染器参数机制。
- [[SRP Batcher]]：参数布局会影响 SRP Batcher 兼容性。
- [[GPU Instancing]]：实例参数和 MPB 常共同用于大量对象差异化。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
