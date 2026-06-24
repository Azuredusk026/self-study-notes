---
title: "Blender"
aliases: []
category: "03_Tools_Pipeline"
confidence: medium
tags: [dcc, blender]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# Blender

## 定义与解释

Blender 是开源 DCC 软件，可用于建模、UV、绑定、动画、程序化节点和资产导出。对 TA 来说，它既是内容制作工具，也是可脚本化的管线节点。

## 核心原理

Blender 的管线价值在于它把场景数据、网格、材质、骨骼、动画和导出设置集中在可被脚本访问的数据结构中。TA 可以通过插件或 Python 批处理读取对象、集合、命名、Modifier、材质槽和导出参数，把制作约定转成工具行为。

落地时需要明确 Blender 与引擎之间的坐标轴、单位、FBX/GLTF 导出设置、法线和切线、动画帧率、骨骼命名与材质贴图路径。否则 DCC 中看似正确的资产，进入 Unity 或 Unreal 后可能出现比例、朝向、法线、动画或材质丢失问题。

## 用途

- 把 Blender 纳入资产生产、检查、导出、导入或版本管理流程，减少人工操作和沟通成本。
- 把团队规范转成可执行规则、工具入口或自动化报告，让问题尽早暴露。
- 连接 DCC、引擎、版本库和 CI/CD，让美术资产从制作到落地有可追踪的状态。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Maya]] | 两者都是 DCC；Blender 更强调开源生态和 Python 插件扩展。 |
| [[Blender Python]] | Blender 是软件环境；Blender Python 是自动化接口。 |

## 常见误区

1. 只把 Blender 当建模软件，不规划导出和检查流程。
2. 忽略坐标轴和单位设置，导致引擎中比例或朝向错误。
3. 手工导出参数不固定，导致同一资产多次导出结果不一致。

## 相关条目

- [[Blender Python]]：Blender 管线自动化常依赖 Python 插件和脚本。
- [[FBX 导出规范]]：Blender 到引擎的交付通常需要稳定导出规则。
- [[DCC工具链]]：Blender 是 DCC 工具链中的一个制作节点。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
