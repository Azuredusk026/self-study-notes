---
title: "Unity Editor Tool"
aliases:
  - Unity 编辑器工具
category: "03_Tools_Pipeline"
tags: [技术美术, Unity, Tool, Pipeline]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Unity Editor Tool

## 一句话定义

Unity Editor Tool 是在 Unity 编辑器中扩展菜单、窗口、导入流程和资产处理逻辑的工具。

## 为什么需要它

项目越大，靠人工点选和口头规范越不可靠。TA 通过编辑器工具把资源检查、批量设置、Prefab 生成、材质替换、贴图压缩和打包配置固化下来，让美术、策划和程序使用同一套生产规则。

## 核心原理

Unity 编辑器工具通常基于 EditorWindow、MenuItem、AssetPostprocessor、ScriptableObject、SerializedObject 和自定义 Inspector。它们运行在编辑器环境，不进入玩家包体。

## 技术美术中的典型用途

- 批量设置贴图压缩和导入格式。
- 检查 Prefab、材质、Mesh、动画资源。
- 自动创建材质实例或 Addressables 分组。
- 生成场景报告和性能预算表。

## Unity 中的相关场景

常见入口是顶部菜单、右键菜单、自定义窗口、Inspector 扩展和导入回调。复杂工具建议把规则、UI 和执行逻辑分离。

## Unreal Engine 中的相关场景

Unreal 对应方向包括 Editor Utility Widget、Blutility、Python 工具和内容浏览器扩展。

## 常见误区

1. 工具只服务作者本人，缺少错误提示和撤销机制。
2. 直接修改大量资产但不生成报告。
3. 把项目规则写死在 UI 代码里，后期难以维护。

## 面试可能怎么问

### 你会如何设计一个 Unity 资源检查工具？

回答要点：先定义检查规则和输出报告，再做批量扫描、问题定位、可选自动修复和日志记录，避免直接静默修改资产。

## 实践建议

做一个 Texture Import 批量检查器，按平台列出尺寸、格式、sRGB、Mipmap 和压缩设置。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[DCC工具链]] | DCC 工具链偏制作软件侧；Pipeline 更强调跨软件、跨引擎和团队流程。 |
| [[资源检查工具]] | 资源检查工具是管线中的一个执行节点，不等同于完整管线设计。 |

## 相关条目

- [[Unity]]
- [[资源检查工具]]
- [[Texture Compression]]
- [[Addressables]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
