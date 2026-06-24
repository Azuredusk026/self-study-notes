---
title: "GPU Instancing"
aliases:
  - GPU 实例化
category: "Shader"
tags: [技术美术, Shader, Optimization, Rendering]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# GPU Instancing

## 一句话定义

GPU Instancing 是用一次或少量 Draw Call 绘制多个共享网格和材质、但实例数据不同的对象。

## 为什么需要它

草、石头、子弹、建筑模块、装饰物等常有大量重复对象。逐个提交会增加 CPU Draw Call 成本，Instancing 可以把差异数据如矩阵、颜色、风动参数传给 GPU，批量绘制。

## 核心原理

- 输入：共享 Mesh、共享 Material、每实例变换和自定义属性。
- 处理过程：GPU 根据 instance id 读取实例数据并在 Vertex Shader 中应用。
- 输出：多个实例的渲染结果。
- 所在层级：CPU 提交优化和 GPU 顶点处理。

## 技术美术中的典型用途

- 植被、碎石、场景小物件。
- 同材质大量特效网格。
- 材质参数差异化而不打断批处理。
- Draw Call 优化。

## Unity 中的相关场景

Unity 支持 GPU Instancing、MaterialPropertyBlock、SRP Batcher 等。TA 需要理解它们的兼容关系和材质属性设置。

## Unreal Engine 中的相关场景

Unreal 常用 Instanced Static Mesh、Hierarchical Instanced Static Mesh、Foliage 系统批量绘制重复对象。

## 常见误区

1. 每个实例使用不同材质会破坏实例化条件。
2. 以为 Instancing 能降低片元成本：它主要降低提交和部分顶点组织成本。
3. 实例数量少或材质复杂时收益不明显。

## 面试可能怎么问

### GPU Instancing 解决的是 CPU 还是 GPU 问题？

回答要点：主要解决大量相似对象导致的 CPU 提交和 Draw Call 问题，但顶点和片元仍需要 GPU 实际处理。

## 实践建议

在 Unity 或 Unreal 中摆放上千个同网格草丛，对比独立对象、合批和 Instancing 的性能差异。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Graph]] | Material Graph 偏节点化编辑；本条目可能涉及更底层的代码、编译和采样细节。 |
| [[Texture Sampling]] | Texture Sampling 是常见操作；本条目可能覆盖更完整的 Shader 结构或控制策略。 |

## 相关条目

- [[Vertex Shader]]
- [[MaterialPropertyBlock]]
- [[SRP Batcher]]
- [[Draw Call]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
