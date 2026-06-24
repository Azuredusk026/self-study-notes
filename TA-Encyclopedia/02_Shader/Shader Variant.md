---
title: "Shader Variant"
aliases:
  - Shader 变体
category: "Shader"
tags: [技术美术, Shader, Optimization]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Shader Variant

## 一句话定义

Shader Variant 是由关键字、渲染路径、光照模式和平台选项组合生成的 Shader 编译版本。

## 为什么需要它

同一个 Shader 可能需要支持阴影、雾、实例化、不同光源、不同质量级别。变体让运行时直接选择已编译分支，但过多变体会导致包体、构建时间、内存和首次加载卡顿问题。

## 核心原理

- 输入：Shader 代码、Keyword、Pass、平台宏、渲染管线选项。
- 处理过程：编译器生成多个静态组合版本。
- 输出：运行时可选择的 GPU 程序集合。
- 所在层级：Shader 构建和运行时加载。

## 技术美术中的典型用途

- 控制材质功能开关。
- 优化构建包体和加载。
- 排查某平台 Shader 缺失或粉色材质。
- 管理 URP/HDRP 和项目级 keyword。

## Unity 中的相关场景

Unity 中 `shader_feature`、`multi_compile`、SRP keywords 都会生成变体。TA 需要配合 Shader Variant Collection、剔除规则和项目设置管理数量。

## Unreal Engine 中的相关场景

Unreal 材质静态开关、Quality Switch、Feature Level 和平台编译会生成不同 permutation。大型项目需要控制材质复杂度和 permutation 数量。

## 常见误区

1. 滥用 `multi_compile`，导致无用变体暴涨。
2. 把运行时参数做成静态 Keyword，导致构建膨胀。
3. 只看单个材质，不看项目级组合爆炸。

## 面试可能怎么问

### Unity 中 shader_feature 和 multi_compile 有什么区别？

回答要点：一般 `shader_feature` 可被未使用变体剔除，`multi_compile` 更偏必须保留的全局组合；具体行为要结合 Unity 版本和构建设置验证。

## 实践建议

创建一个包含 5 个二值 keyword 的 Shader，统计变体数量，再移除无用 keyword 观察构建变化。

## 相关条目

- [[Keyword]]
- [[Branch]]
- [[SRP Batcher]]
- [[Unity]]

## 参考来源

- 待核验：需要后续查阅 Unity / Unreal 官方文档确认不同版本的变体剔除细节。

