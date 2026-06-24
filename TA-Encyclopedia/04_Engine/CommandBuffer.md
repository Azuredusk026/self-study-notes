---
title: "CommandBuffer"
aliases:
  - Command Buffer
category: "04_Engine"
tags: [技术美术, Unity, Rendering]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# CommandBuffer

## 定义与解释

CommandBuffer 是记录一组渲染命令并在指定时机提交执行的对象，常用于自定义渲染、后处理、抓取缓冲和调试可视化。

## 核心原理

CommandBuffer 的核心是把渲染命令从立即执行改成可插入管线的命令序列。它可以设置 Render Target、清屏、绘制 Mesh、Blit、设置全局纹理或执行计算，在相机、Light 或 SRP 的特定阶段运行。

TA 使用 CommandBuffer 时要确认插入点、目标缓冲、资源生命周期和多相机行为。错误的时机或 Render Target 会导致画面覆盖、深度不一致、移动端带宽增加或与管线内置 Pass 冲突。

## 用途

- 在引擎项目中定位与 CommandBuffer 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[ScriptableRendererFeature]] | Renderer Feature 是 URP 的结构化扩展点；CommandBuffer 是更底层的命令记录方式。 |
| [[RenderTexture]] | RenderTexture 是目标资源；CommandBuffer 是操作资源的命令序列。 |

## 常见误区

1. 不确认执行时机就插入命令，导致结果被后续 Pass 覆盖。
2. 临时 RT 未释放或重复分配造成内存波动。
3. 多相机或 SceneView 下命令重复执行。

## 相关条目

- [[Render Pass]]：CommandBuffer 通常用于插入或组织渲染阶段。
- [[RenderTexture]]：命令常读写 RenderTexture。
- [[ScriptableRendererFeature]]：URP 中更常用 Renderer Feature 封装自定义 Pass。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
