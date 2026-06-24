---
title: "Raycast"
aliases:
  - 射线检测
category: "Math_CS"
tags: [技术美术, Math, Physics, Tools]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Raycast

## 一句话定义

Raycast 是沿射线查询与场景几何、碰撞体或加速结构的相交结果。

## 为什么需要它

TA 做工具时常需要从屏幕点选模型、拾取地面位置、放置特效、检测遮挡和生成贴花。Raycast 把用户输入或程序逻辑转换成空间命中信息。

## 核心原理

- 输入：Ray、最大距离、碰撞层或目标几何。
- 处理过程：与碰撞体、三角形、AABB 或 BVH 做相交测试。
- 输出：是否命中、命中点、法线、距离、对象。
- 所在层级：物理系统、编辑器工具、几何算法。

## 技术美术中的典型用途

- 场景编辑工具拾取。
- 自动贴地和资产摆放。
- 命中特效位置和法线方向。
- 烘焙投射和高低模匹配。

## Unity 中的相关场景

Unity 中 `Physics.Raycast`、`RaycastHit`、LayerMask 是常见组合。Editor Tool 中也常从 SceneView 相机生成射线。

## Unreal Engine 中的相关场景

Unreal 中 Line Trace、Multi Trace 可按 Channel 或 Object Type 查询，适合蓝图工具和运行时逻辑。

## 常见误区

1. 没有限制 Layer/Channel，命中不该命中的物体。
2. 忘记碰撞体和渲染网格可能不一致。
3. 用每帧大量 Raycast 替代更合适的空间查询。

## 面试可能怎么问

### Raycast 返回的法线可以用来做什么？

回答要点：可以对齐贴花、放置特效、计算反射方向、判断表面朝向或做工具可视化。

## 实践建议

写一个点击地面生成贴花的工具，让贴花方向与命中法线对齐。

## 相关条目

- [[Ray]]
- [[AABB_OBB]]
- [[BVH]]
- [[几何算法]]

## 参考来源

- 待补充

