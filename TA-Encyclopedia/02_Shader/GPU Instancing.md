---
title: "GPU Instancing"
aliases:
  - GPU 实例化
category: "Shader"
tags: [技术美术, Shader, Optimization, Rendering]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# GPU Instancing

## 定义与解释

GPU Instancing 是用一次或少量绘制提交渲染多个共享网格和材质的对象实例。它主要降低 Draw Call 和 CPU 提交成本，同时允许每个实例携带少量差异数据。

## 核心原理

Instancing 的核心是把相同 Mesh/Material 的多个对象合并到一次实例化绘制中。Shader 通过 Instance ID 读取每个实例的矩阵、颜色、参数或其他实例数据，从而在 GPU 上区分对象。

它适合大量重复物体，如草、石头、道具和特效片。限制在于材质状态必须兼容，实例数据带宽有限，透明排序、光照探针、LOD、剔除和材质关键字都可能打断批处理。TA 需要同时检查引擎开关、材质支持和实例属性声明。

## 用途

- 在材质或 Shader 调试中定位与 GPU Instancing 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[SRP Batcher]] | SRP Batcher 优化常量绑定；GPU Instancing 合并重复实例绘制。 |
| [[Draw Call]] | Draw Call 是成本指标；Instancing 是降低该成本的方法之一。 |

## 常见误区

1. 以为开启 Instancing 就一定合批。
2. 每个实例使用不同材质或关键字导致无法实例化。
3. 忽略透明排序和每实例数据带宽限制。

## 相关条目

- [[Draw Call]]：GPU Instancing 主要用于减少提交次数。
- [[MaterialPropertyBlock]]：Unity 中常用来设置实例差异参数。
- [[Shader Variant]]：不同变体会破坏实例批处理。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
