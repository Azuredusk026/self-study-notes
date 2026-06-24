---
title: "Z-Test"
aliases:
  - Depth Test
  - 深度测试
category: "Rendering"
tags: [技术美术, Rendering, Depth]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Z-Test

## 定义与解释

Z-Test 是根据片元深度和 Depth Buffer 中已有深度比较，决定片元是否通过的深度测试规则。它是解决物体前后遮挡和减少无效绘制的基础机制。

## 核心原理

Z-Test 的核心是比较函数，例如 Less、LessEqual、Greater、Always 等。片元深度与缓冲中的深度比较后，只有通过的片元才可能继续写颜色；如果开启深度写入，还会更新 Depth Buffer。

Z-Test 和 ZWrite 是不同概念：前者决定能不能通过，后者决定是否写入深度。透明、描边、特效、UI 和特殊遮罩经常需要调整这两个状态。TA 排查穿插、消失、透视错误和排序问题时必须同时看渲染队列、深度测试、深度写入和混合状态。

## 用途

- 在渲染调试中定位与 Z-Test 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Early-Z]] | Z-Test 是规则；Early-Z 是提前执行该规则的优化。 |
| [[Stencil Buffer]] | Z-Test 比较深度；Stencil Test 比较模板值。 |

## 常见误区

1. 混淆 Z-Test 和 ZWrite。
2. 透明材质关闭深度写入后，仍期待完全正确的遮挡排序。
3. 特殊效果使用 Always 测试后忘记恢复遮挡关系。

## 相关条目

- [[Depth Buffer]]：Z-Test 读取并可能更新深度缓冲。
- [[Early-Z]]：Z-Test 可能提前执行形成 Early-Z 优化。
- [[Alpha Blend]]：透明材质常保留 Z-Test 但关闭 ZWrite。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
