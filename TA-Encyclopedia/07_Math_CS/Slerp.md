---
title: "Slerp"
aliases:
  - Spherical Linear Interpolation
  - 球面线性插值
category: "Math_CS"
tags: [技术美术, Math, Quaternion, Interpolation]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Slerp

## 定义与解释

Slerp 是球面线性插值，常用于在两个方向或四元数旋转之间沿球面最短路径平滑过渡。

## 核心原理

Slerp 保持插值结果在单位球面上，并按角度比例变化。对于方向向量或单位四元数，它比普通 Lerp 更能保持旋转速度和长度稳定。

在实际工程中，Slerp 常用于相机旋转、角色朝向、骨骼姿态和方向混合。TA 需要注意输入是否归一化、四元数符号是否选择最短路径，以及小角度时是否可退化为 Lerp 优化。

## 用途

- 在图形、动画、碰撞、寻路、编辑器工具或调试可视化中解释与 Slerp 相关的结果。
- 把数学概念转成可验证的代码、Gizmos、Shader 计算或资源检查规则。
- 帮助 TA 与程序沟通空间关系、复杂度、数值稳定性和运行时限制。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Lerp]] | Lerp 直线插值，Slerp 球面角度插值。 |
| [[四元数]] | 四元数是旋转表示，Slerp 是旋转插值方法。 |

## 常见误区

1. 对未归一化向量使用 Slerp。
2. 四元数符号没处理导致绕远路。
3. 所有插值都用 Slerp，忽略成本和需求。

## 相关条目

- [[四元数]]：四元数旋转常用 Slerp 插值。
- [[Lerp]]：Lerp 是线性插值对照。
- [[向量]]：单位方向向量也可做球面插值。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
