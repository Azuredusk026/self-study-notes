---
title: "Lerp"
aliases:
  - Linear Interpolation
  - 线性插值
category: "Math_CS"
tags: [技术美术, Math, Interpolation]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Lerp

## 一句话定义

Lerp 是在两个值之间按参数 t 做线性插值。

## 为什么需要它

颜色混合、动画过渡、材质参数渐变、UV 偏移、特效淡入淡出都常用 Lerp。TA 在 Shader Graph 和材质节点中几乎每天都会遇到它。

## 核心原理

- 输入：起点 A、终点 B、插值参数 t。
- 处理过程：`A * (1 - t) + B * t`。
- 输出：A 和 B 之间或延长线上的值。
- 所在层级：Shader、动画、工具脚本。

```csharp
float v = Mathf.Lerp(a, b, t);
```

## 技术美术中的典型用途

- 两张贴图混合。
- 溶解边缘颜色过渡。
- 参数平滑变化。
- 根据高度或遮罩混合材质。

## Unity 中的相关场景

Unity C# 有 `Mathf.Lerp`、`Vector3.Lerp`、`Color.Lerp`。Shader Graph 中 Lerp 节点非常常用。

## Unreal Engine 中的相关场景

Unreal 材质中的 LinearInterpolate 节点使用 A、B、Alpha 进行混合。

## 常见误区

1. 以为 t 必须在 0 到 1：数学上可超出，但很多 API 会 Clamp。
2. 每帧用当前值 Lerp 目标值，以为是固定时间过渡。
3. 用线性插值处理角度或旋转导致不自然。

## 面试可能怎么问

### Lerp 的公式是什么？

回答要点：`A + (B - A) * t`，等价于 `A * (1 - t) + B * t`。

## 实践建议

用 Lerp 和一张噪声图实现两种材质的高度混合。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[线性代数]] | 线性代数提供基础语言；本条目可能是其中一个概念或算法应用。 |
| [[几何算法]] | 几何算法偏空间关系判断；本条目可能偏数据结构、搜索或变换。 |

## 相关条目

- [[Slerp]]
- [[Shader_Graph]]
- [[Texture Sampling]]
- [[四元数]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
