---
title: "Maya Python"
aliases: []
category: "03_Tools_Pipeline"
tags: [技术美术, Maya, Python, Pipeline]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Maya Python

## 定义与解释

Maya Python 是 Maya 的脚本接口，用于创建工具、检查场景、批量处理模型和动画、封装导出流程。

## 核心原理

Maya Python 通常通过 `cmds`、OpenMaya API 或 PySide UI 操作场景。TA 可以读取 DAG、节点属性、SkinCluster、动画曲线和文件路径，执行检查、修复、导出和报告生成。

可靠的 Maya 工具要减少 UI 上下文依赖，明确选择集、命名、撤销、单位、引用文件、命名空间和错误恢复策略。角色和动画管线尤其要关注引用、约束、Bake 和导出前清理。

## 用途

- 把 Maya Python 纳入资产生产、检查、导出、导入或版本管理流程，减少人工操作和沟通成本。
- 把团队规范转成可执行规则、工具入口或自动化报告，让问题尽早暴露。
- 连接 DCC、引擎、版本库和 CI/CD，让美术资产从制作到落地有可追踪的状态。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Blender Python]] | 两者都是 DCC 脚本接口，但数据模型和 API 习惯不同。 |
| [[Unity Editor Tool]] | Maya Python 处理制作源文件；Unity Editor Tool 处理引擎资产。 |

## 常见误区

1. 直接录制命令而不理解场景上下文。
2. 没有处理引用、命名空间和文件路径。
3. 工具失败时只抛异常，不告诉美术修复位置。

## 相关条目

- [[Maya]]：Maya Python 运行在 Maya 环境内。
- [[自动化导出工具]]：Maya Python 常用于封装 FBX 导出。
- [[资源检查工具]]：Maya 场景检查可提前发现资产问题。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
