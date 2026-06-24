---
title: "Blender Python"
aliases: []
category: "03_Tools_Pipeline"
tags: [技术美术, Blender, Python, Pipeline]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Blender Python

## 一句话定义

Blender Python 是通过 Python 扩展 Blender、批处理资产和开发 DCC 工具的方式。

## 为什么需要它

Blender 在个人项目、独立团队和部分商业管线中很常见。TA 可以用 Python 自动化导入导出、命名检查、批量处理、Geometry Nodes 参数管理和资产规范检查。

## 核心原理

Blender Python 通过 `bpy` 访问场景、对象、Mesh、材质、动画和 UI。工具可以是一次性脚本，也可以打包成 Add-on。

## 技术美术中的典型用途

- 批量重命名和导出 FBX/GLTF。
- 检查模型比例、Pivot、材质槽和 UV。
- 生成碰撞体、LOD 或辅助节点。
- 与 Unity/Unreal 导入规范对接。

## Unity 中的相关场景

Blender 工具可以在导出前规范 FBX、贴图命名和模型层级，减少 Unity 导入后修复。

## Unreal Engine 中的相关场景

Unreal 项目中可用 Blender Python 预处理 Static Mesh、碰撞命名、LOD 和材质槽。

## 常见误区

1. 只写临时脚本，不考虑 Add-on 配置和团队使用。
2. 导出工具不记录日志。
3. Blender 单位和引擎单位没有统一。

## 面试可能怎么问

### Blender Python 对 TA 有什么价值？

回答要点：它能把 Blender 资产生产中的重复步骤自动化，并在导出前执行规范检查，降低引擎侧返工。

## 实践建议

做一个 Blender Add-on：检查选中模型命名、面数、UV、材质槽，并一键导出到项目目录。

## 相关条目

- [[Blender]]
- [[FBX 导出规范]]
- [[资源检查工具]]
- [[Unity Editor Tool]]

## 参考来源

- 待补充

