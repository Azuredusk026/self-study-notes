---
title: "Houdini"
aliases: []
category: "03_Tools_Pipeline"
confidence: medium
tags: [dcc, houdini, procedural]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# Houdini

## 定义与解释

Houdini 是以程序化节点和数据流为核心的 DCC 软件，常用于地形、建筑、散布、破碎、VFX 和批量资产生成。

## 核心原理

Houdini 的核心是节点网络和属性驱动。几何、点、面、体积和属性在 SOP、DOP、VOP 等上下文中流转，工具通过参数和节点组合生成可复用流程。

TA 关注的是如何把 Houdini 结果接入项目：命名、分层、LOD、碰撞、材质槽、实例化数据、烘焙缓存、导出格式和引擎插件边界。程序化并不自动等于可用资产，必须通过规范和检查控制输出。

## 用途

- 把 Houdini 纳入资产生产、检查、导出、导入或版本管理流程，减少人工操作和沟通成本。
- 把团队规范转成可执行规则、工具入口或自动化报告，让问题尽早暴露。
- 连接 DCC、引擎、版本库和 CI/CD，让美术资产从制作到落地有可追踪的状态。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Blender]] | Blender 更通用制作；Houdini 更强调程序化节点和批量生成。 |
| [[Substance]] | Substance 偏材质纹理程序化；Houdini 偏几何和特效程序化。 |

## 常见误区

1. 把程序化结果直接当最终资产，不做规范检查。
2. 节点网络只服务个人操作，缺少参数封装和版本控制。
3. 生成资产数量过多但没有 LOD、碰撞和实例化策略。

## 相关条目

- [[DCC工具链]]：Houdini 是程序化 DCC 节点。
- [[自动化导出工具]]：Houdini 生成结果需要稳定导出。
- [[资源检查工具]]：程序化资产同样需要检查。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
