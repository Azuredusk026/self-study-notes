---
title: "Early-Z"
aliases:
  - Early Depth Test
category: "Rendering"
tags: [技术美术, Rendering, Optimization]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---



# Early-Z

## 定义与解释

Early-Z 是在片元执行昂贵着色之前，尽早用深度测试剔除不可见片元的 GPU 优化机制。它能减少 Overdraw 带来的片元着色浪费，但会受 Shader 行为和渲染状态影响。

## 核心原理

Early-Z 的关键是 GPU 可以在片元着色前判断该片元是否会被已有深度挡住。如果测试失败，就不需要继续执行纹理采样、光照和复杂分支。

并不是所有材质都能稳定享受 Early-Z。片元中使用 discard/clip、写深度、Alpha Test、某些混合状态或关闭深度写入时，GPU 可能延后深度测试或降低优化效果。TA 在排查性能时要结合 Overdraw 视图、深度预通道和材质复杂度判断。

## 用途

- 在渲染调试中定位与 Early-Z 相关的画面异常、性能成本或资源配置问题。
- 为美术、TA 和图形程序建立统一术语，减少材质、灯光、后处理和管线配置沟通偏差。
- 把概念落到 Unity、Unreal 或 RenderDoc/Frame Debugger 中可观察的状态、缓冲、Pass 或材质参数上。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Z-Test]] | Z-Test 是可见性规则；Early-Z 是可能提前执行的优化。 |
| [[Alpha Test]] | Alpha Test 可能因为裁剪逻辑影响 Early-Z 效果。 |

## 常见误区

1. 认为开启 Z-Test 就一定有 Early-Z。
2. 在复杂透明或裁剪材质上期待和不透明物体一样的提前剔除。
3. 只看三角形数量，不看 Overdraw 和材质复杂度。

## 相关条目

- [[Z-Test]]：Early-Z 是深度测试提前执行的优化形式。
- [[Overdraw]]：Early-Z 可以减少被遮挡片元的着色成本。
- [[Depth Buffer]]：Early-Z 依赖已有深度信息。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
