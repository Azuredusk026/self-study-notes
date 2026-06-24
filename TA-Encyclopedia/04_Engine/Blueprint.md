---
title: "Blueprint"
aliases:
  - 蓝图
category: "04_Engine"
tags: [技术美术, Unreal, Tool]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Blueprint

## 一句话定义

Blueprint 是 Unreal 的可视化脚本系统，用于快速构建玩法逻辑、工具、材质参数驱动和关卡交互。

## 为什么需要它

TA 不一定负责完整 gameplay，但经常需要用蓝图连接材质、Niagara、动画、编辑器工具和关卡事件。蓝图让非纯程序人员也能搭建可验证原型。

## 核心原理

蓝图通过节点图表达事件、变量、函数、组件和对象引用，最终由引擎执行。工程上要注意依赖关系、Tick 成本、可维护性和调试。

## 技术美术中的典型用途

- 驱动材质参数和 Niagara 参数。
- 做编辑器工具原型。
- 关卡交互和演出控制。
- 快速验证 Shader/VFX 效果。

## Unity 中的相关场景

Unity 中相近角色通常由 C# 脚本、Visual Scripting 或编辑器工具承担。

## Unreal Engine 中的相关场景

TA 常用 Actor Blueprint、Editor Utility Blueprint、Widget Blueprint 和 Material Parameter Collection 配合制作工具和效果。

## 常见误区

1. 所有逻辑都堆在 Event Graph。
2. Tick 中做大量查找或动态创建。
3. 蓝图变量命名和分类不清晰，交接困难。

## 面试可能怎么问

### TA 用 Blueprint 通常做什么？

回答要点：驱动材质/VFX 参数、搭建工具原型、连接关卡事件和演出逻辑，并与程序协作把高频或复杂逻辑下沉。

## 实践建议

做一个交互物高亮蓝图：靠近时修改材质实例参数并触发 Niagara 提示特效。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Unity]] | Unity 是引擎平台；本条目可能是其中某个系统或工作流。 |
| [[Unreal_Engine]] | Unreal 是引擎平台；本条目可能与其对应系统形成实现差异。 |

## 相关条目

- [[Niagara]]
- [[Material Instance]]
- [[Custom Depth]]
- [[Editor Utility Widget]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
