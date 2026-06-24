---
title: "ScriptableRendererFeature"
aliases:
  - Renderer Feature
category: "04_Engine"
tags: [技术美术, Unity, URP, Rendering]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# ScriptableRendererFeature

## 定义与解释

ScriptableRendererFeature 是 Unity URP 中向 Renderer 注入自定义渲染 Pass 的扩展点，常用于后处理、描边、深度预处理和特殊对象渲染。

## 核心原理

它的核心是通过 Feature 创建和配置 ScriptableRenderPass，并在指定 RenderPassEvent 插入 URP 渲染流程。Pass 可以设置目标、筛选对象、执行 Blit、绘制 Renderers 或读写临时 RT。

TA 使用它时要理解 URP 的相机堆叠、渲染事件、RTHandle、深度纹理、透明/不透明阶段和 Renderer Data 资产。插入点不对会导致缓冲未准备好或结果被后续 Pass 覆盖。

## 用途

- 在引擎项目中定位与 ScriptableRendererFeature 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[CommandBuffer]] | CommandBuffer 是命令容器；ScriptableRendererFeature 是 URP 管线扩展结构。 |
| [[SRP]] | SRP 是框架；Renderer Feature 是 URP 中的具体扩展点。 |

## 常见误区

1. 不理解 RenderPassEvent，导致效果时序错误。
2. 未处理相机堆叠和 SceneView。
3. 临时 RT 分配释放不规范。

## 相关条目

- [[URP]]：ScriptableRendererFeature 是 URP 扩展机制。
- [[CommandBuffer]]：Pass 内部常使用命令缓冲执行绘制。
- [[RenderTexture]]：自定义 Pass 常读写中间 RT。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
