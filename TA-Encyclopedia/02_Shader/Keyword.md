---
title: "Keyword"
aliases: []
category: "02_Shader"
tags:
  - 技术美术
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---


# Keyword

## 定义与解释

Keyword 是 Shader 或材质系统中用于启用、禁用功能分支的开关。它常用于控制法线、阴影、特效开关、质量等级和平台功能。

## 核心原理

Keyword 的核心是把功能选择前移到编译期或材质状态层。静态 Keyword 通常生成不同 Shader Variant，让运行时避免部分分支；动态或本地开关则在灵活性和变体数量之间折中。

Keyword 管理的风险是组合数量爆炸。每增加一组开关，都可能和其他开关形成乘法关系，增加构建时间、包体、内存和运行时加载成本。TA 需要限制美术可见开关数量，并清理不用的变体。

## 用途

- 在材质或 Shader 调试中定位与 Keyword 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Branch]] | Branch 是逻辑控制；Keyword 是编译或材质层面的开关。 |
| [[Shader Variant]] | Variant 是 Keyword 组合后的编译产物。 |

## 常见误区

1. 随意为每个小功能加全局 Keyword。
2. 不区分全局和本地 Keyword，造成项目级污染。
3. 构建后不统计实际使用变体。

## 相关条目

- [[Shader Variant]]：Keyword 常导致变体生成。
- [[Branch]]：Keyword 可控制静态分支。
- [[Material Graph]]：节点图中的开关可能映射为 Keyword。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
