---
title: "Custom Depth"
aliases:
  - CustomDepth
category: "04_Engine"
tags: [技术美术, Unreal, Rendering]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Custom Depth

## 定义与解释

Custom Depth 是 Unreal 中让指定对象写入独立深度缓冲的功能，常用于描边、遮挡高亮、角色透视和后处理选择。

## 核心原理

Custom Depth 的机制是让被标记对象在额外 Pass 中写入专用深度纹理，后处理材质再读取该纹理与 Scene Depth 比较，判断对象轮廓、遮挡关系或屏幕区域。Custom Stencil 可进一步提供分类 ID。

它不是普通深度缓冲的替代品。TA 需要确认对象是否启用写入、透明材质是否参与、Stencil 值是否分配冲突、后处理执行顺序和移动端成本。多个效果共享 Custom Depth 时尤其要规划值域。

## 用途

- 在引擎项目中定位与 Custom Depth 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Depth Buffer]] | Depth Buffer 是主场景深度；Custom Depth 是选择性额外深度。 |
| [[Stencil Buffer]] | Stencil 存分类标记；Custom Depth 存被标记对象深度。 |

## 常见误区

1. 启用了后处理但对象没写 Custom Depth。
2. 多个功能共用 Stencil 值导致分类冲突。
3. 透明材质和 Nanite 等路径是否写入未核验就下结论。

## 相关条目

- [[Post Process Material]]：Custom Depth 常由后处理材质读取。
- [[Stencil Buffer]]：Custom Stencil 与模板分类思路接近。
- [[Unreal_Engine]]：Custom Depth 是 Unreal 渲染扩展功能。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
