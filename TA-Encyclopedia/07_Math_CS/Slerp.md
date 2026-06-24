---
title: "Slerp"
aliases:
  - Spherical Linear Interpolation
  - 球面线性插值
category: "Math_CS"
tags: [技术美术, Math, Quaternion, Interpolation]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Slerp

## 一句话定义

Slerp 是在球面上沿最短弧线插值方向或旋转的方法。

## 为什么需要它

旋转不是普通位置，直接线性插值欧拉角容易出现速度不均、绕路或万向节问题。Slerp 常用于相机旋转、角色朝向、骨骼过渡和四元数插值。

## 核心原理

- 输入：两个单位方向或单位四元数、参数 t。
- 处理过程：沿球面弧线插值，保持旋转路径平滑。
- 输出：插值后的方向或四元数。
- 所在层级：动画、相机、角色控制、工具脚本。

```csharp
Quaternion q = Quaternion.Slerp(a, b, t);
```

## 技术美术中的典型用途

- 相机 LookAt 平滑。
- IK 控制器旋转过渡。
- 动画混合和骨骼调试。
- 程序化朝向控制。

## Unity 中的相关场景

Unity 提供 `Quaternion.Slerp`。TA 做编辑器工具、角色展示器和镜头工具时常用。

## Unreal Engine 中的相关场景

Unreal 中 Rotator、Quat 和插值节点可用于蓝图或 C++ 旋转平滑。

## 常见误区

1. 用 Lerp 欧拉角处理大角度旋转。
2. 忽略四元数需要归一化。
3. 每帧 Slerp 当前值到目标值时，把 t 当作固定持续时间。

## 面试可能怎么问

### 为什么旋转插值常用 Slerp 而不是普通 Lerp？

回答要点：Slerp 沿球面插值，能保持更稳定的角速度和旋转路径，适合方向和四元数。

## 实践建议

做一个相机从 A 方向转向 B 方向的 Demo，对比 Euler Lerp 和 Quaternion Slerp。

## 相关条目

- [[Lerp]]
- [[四元数]]
- [[矩阵变换]]
- [[动画技术]]

## 参考来源

- 待补充

