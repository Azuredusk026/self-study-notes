---
title: "Maya Python"
aliases: []
category: "03_Tools_Pipeline"
tags: [技术美术, Maya, Python, Pipeline]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Maya Python

## 一句话定义

Maya Python 是在 Maya 中编写工具、批处理资产和自动化生产流程的主要脚本方式之一。

## 为什么需要它

TA 经常要处理重复性美术流程：命名检查、冻结变换、清理历史、批量导出 FBX、绑定辅助、骨骼检查和资产验收。Maya Python 能把这些流程变成可复用工具，减少人工失误。

## 核心原理

Maya Python 通过 `cmds`、OpenMaya API 或 PySide UI 操作场景节点、属性、选择集、文件导入导出和界面。简单工具通常用 `maya.cmds` 足够，性能敏感或底层数据访问再考虑 OpenMaya。

## 技术美术中的典型用途

- 模型命名和层级检查。
- 批量 FBX 导出。
- 骨骼、蒙皮、控制器检查。
- 自动生成碰撞体或挂点。
- 美术交付前的资产体检。

## Unity 中的相关场景

Maya 工具常输出符合 Unity 导入规范的 FBX、贴图命名、Prefab 目录和骨骼结构，减少 Unity 侧 AssetPostprocessor 的纠错压力。

## Unreal Engine 中的相关场景

Unreal 项目常要求骨骼命名、Root、单位比例、Socket、LOD 和碰撞命名符合导入规范，Maya Python 可以在导出前预检查。

## 常见误区

1. 所有逻辑写在一个脚本里，后期无法维护。
2. 只做导出，不做导出前检查和错误报告。
3. 工具没有记录版本和运行日志，出问题难以追溯。

## 面试可能怎么问

### TA 用 Maya Python 通常解决什么问题？

回答要点：批量处理资产、自动化导出、规范检查、绑定辅助和减少美术生产中的重复操作。

## 实践建议

做一个模型交付检查工具：检查命名、冻结变换、历史、材质数量、面数、UV 和 FBX 导出路径。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[DCC工具链]] | DCC 工具链偏制作软件侧；Pipeline 更强调跨软件、跨引擎和团队流程。 |
| [[资源检查工具]] | 资源检查工具是管线中的一个执行节点，不等同于完整管线设计。 |

## 相关条目

- [[Maya]]
- [[FBX 导出规范]]
- [[资源检查工具]]
- [[建模规范]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
