---
title: "Ray"
aliases:
  - 射线
category: "Math_CS"
tags: [技术美术, Math, Geometry]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Ray

## 一句话定义

Ray 是由起点和方向定义的半无限直线。

## 为什么需要它

鼠标拾取、点击选择、碰撞检测、视线检测、射击判定、屏幕到世界转换和几何算法都常用射线。TA 做编辑器工具、关卡工具和 Debug 可视化时经常会用到。

## 核心原理

- 输入：起点 O、归一化方向 D、参数 t。
- 处理过程：射线上任一点可表示为 `P = O + D * t`，其中 t >= 0。
- 输出：射线位置、相交点、距离或命中信息。
- 所在层级：数学、物理、编辑器工具、渲染算法。

```csharp
Vector3 p = origin + direction.normalized * t;
```

## 技术美术中的典型用途

- 选择场景物体。
- 烘焙工具中的投射。
- 检查角色脚底与地面。
- 生成程序化贴花或命中特效位置。

## Unity 中的相关场景

Unity 中 Camera.ScreenPointToRay 和 Physics.Raycast 常用于鼠标选择与碰撞检测。

## Unreal Engine 中的相关场景

Unreal 中 Line Trace by Channel 是常用射线查询入口，可用于蓝图和工具。

## 常见误区

1. 方向没有归一化，导致 t 不等于真实距离。
2. 把 Ray 和线段混淆，忘记限制最大距离。
3. 屏幕坐标转射线时相机或坐标系用错。

## 面试可能怎么问

### 射线方程怎么写？

回答要点：`P = O + D * t`，O 是起点，D 是方向，t 是非负距离参数。

## 实践建议

写一个鼠标点击场景物体并显示命中点法线的小工具。

## 相关条目

- [[Raycast]]
- [[几何算法]]
- [[AABB_OBB]]
- [[点积]]

## 参考来源

- 待补充

