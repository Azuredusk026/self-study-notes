---
title: "FBX 导出规范"
aliases:
  - FBX Export Rules
category: "03_Tools_Pipeline"
tags: [技术美术, Pipeline, DCC]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# FBX 导出规范

## 一句话定义

FBX 导出规范定义 DCC 资产导出到引擎时的单位、坐标轴、层级、骨骼、动画、材质和文件命名规则。

## 为什么需要它

FBX 是美术资产进入 Unity/Unreal 的常见桥梁。导出设置不统一会造成比例错误、朝向错误、动画丢失、骨骼异常、材质丢失和重复劳动。

## 核心原理

规范应明确 DCC 场景准备、导出选项、文件命名、目录结构、版本管理和引擎导入设置。TA 需要把“能导出”提升到“稳定可复现导出”。

## 技术美术中的典型用途

- 角色模型和动画导出。
- 静态场景资产导出。
- LOD、碰撞体、Socket/挂点导出。
- 自动化批量导出工具。

## Unity 中的相关场景

Unity 需要关注 Scale Factor、Rig 类型、Animation Clip 切分、Materials 导入、Normals/Tangents 和 Optimize Mesh 等设置。

## Unreal Engine 中的相关场景

Unreal 需要关注厘米单位、骨骼层级、Skeletal Mesh/Static Mesh、Collision 命名、Socket、LOD 和动画导入。

## 常见误区

1. 只保存场景文件，不保存导出预设。
2. 每个美术手动导出，设置难以一致。
3. 引擎导入错误后在引擎里临时修，不回到 DCC 源头修规范。

## 面试可能怎么问

### FBX 导出最常见的问题有哪些？

回答要点：比例、轴向、Pivot、法线切线、骨骼层级、动画帧率、材质贴图路径和 LOD/碰撞命名。

## 实践建议

做一个 Maya/Blender 批量导出工具，导出前先检查单位、冻结变换、命名和骨骼 Root。

## 相关条目

- [[DCC工具链]]
- [[Maya Python]]
- [[Blender]]
- [[建模规范]]

## 参考来源

- 待补充

