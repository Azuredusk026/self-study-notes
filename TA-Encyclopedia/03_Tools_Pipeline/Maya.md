---
title: "Maya"
aliases: []
category: "03_Tools_Pipeline"
confidence: medium
tags: [dcc, maya]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# Maya

## 定义与解释

Maya 是角色、绑定、动画、建模和影视/游戏资产生产中常见的 DCC 软件。TA 常通过它建立角色管线、导出工具和资产检查流程。

## 核心原理

Maya 的管线价值来自可脚本化场景图、节点系统、骨骼、约束、动画曲线和导出接口。角色或动画资产通常需要在 Maya 中完成命名、层级、骨骼、蒙皮、动画段、控制器和导出配置的规范化。

落地时要明确 Maya 与引擎之间的单位、轴向、骨骼命名、Root Motion、动画 Bake、Blend Shape、法线和材质槽规则。TA 需要把重复操作封装为工具，并在导出前给出可读错误。

## 用途

- 把 Maya 纳入资产生产、检查、导出、导入或版本管理流程，减少人工操作和沟通成本。
- 把团队规范转成可执行规则、工具入口或自动化报告，让问题尽早暴露。
- 连接 DCC、引擎、版本库和 CI/CD，让美术资产从制作到落地有可追踪的状态。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Blender]] | 两者都是 DCC；Maya 在角色绑定和动画管线中更常见。 |
| [[Maya Python]] | Maya 是软件环境；Maya Python 是扩展和自动化接口。 |

## 常见误区

1. 只在 Maya 中看表现，不验证引擎导入结果。
2. 角色导出规则依赖口头约定。
3. 工具脚本没有处理场景脏数据和命名冲突。

## 相关条目

- [[Maya Python]]：Maya 管线自动化常依赖 Python。
- [[FBX 导出规范]]：Maya 到引擎交付常使用 FBX。
- [[角色绑定]]：Maya 常用于绑定和动画生产。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
