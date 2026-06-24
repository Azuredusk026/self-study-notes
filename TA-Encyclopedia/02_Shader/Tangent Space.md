---
title: "Tangent Space"
aliases:
  - 切线空间
category: "Shader"
tags: [技术美术, Shader, Math]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Tangent Space

## 一句话定义

Tangent Space 是由法线、切线和副切线组成的局部表面坐标系。

## 为什么需要它

法线贴图中的 RGB 方向通常不是世界方向，而是相对于模型表面的局部方向。切线空间让同一张法线贴图可以贴在不同位置、朝向和变形后的模型上。

## 核心原理

- 输入：顶点 Normal、Tangent、UV 方向和 handedness。
- 处理过程：构建 TBN 矩阵，将切线空间方向转换到世界或视图空间。
- 输出：用于光照计算的法线方向。
- 所在层级：Vertex/Fragment Shader。

## 技术美术中的典型用途

- 法线贴图解码。
- 角色变形后的稳定光照。
- DCC 与引擎切线基准一致性检查。
- 排查镜像 UV、接缝和烘焙不匹配。

## Unity 中的相关场景

Unity Mesh 导入可选择导入或计算 Tangents。不同法线烘焙工具和 Unity 切线计算方式不一致时，可能出现接缝。

## Unreal Engine 中的相关场景

Unreal 常使用 MikkTSpace 作为切线空间标准。资产导入时可选择导入法线/切线或由引擎计算。

## 常见误区

1. 认为法线贴图方向天然是世界空间方向。
2. 镜像 UV 后没有处理切线符号，导致一侧光照反。
3. DCC 烘焙和引擎显示使用不同切线基准。

## 面试可能怎么问

### TBN 矩阵的作用是什么？

回答要点：TBN 由 Tangent、Bitangent、Normal 构成，用于在切线空间和世界/视图空间之间转换方向。

## 实践建议

导入一个带镜像 UV 的模型，分别使用导入切线和引擎重算法线，观察法线贴图接缝。

## 相关条目

- [[Normal Map]]
- [[矩阵变换]]
- [[World Space]]
- [[UV]]

## 参考来源

- 待补充

