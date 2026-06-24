---
title: "Clip Space"
aliases:
  - 裁剪空间
category: "Shader"
tags: [技术美术, Shader, Space]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Clip Space

## 定义与解释

Clip Space 是顶点经过投影矩阵变换后、透视除法之前所处的裁剪空间。它用于决定几何是否在视锥内，并为后续 NDC 和屏幕坐标转换做准备。

## 核心原理

Clip Space 中的位置通常是齐次坐标 `(x, y, z, w)`。GPU 会用这个空间进行视锥裁剪，再通过透视除法把坐标转为标准化设备坐标。`w` 分量保留了透视投影所需的信息，因此不能把 Clip Space 简单当作普通三维坐标。

Unity、Unreal、OpenGL、DirectX、Vulkan 在深度范围、Y 方向、反向 Z 和矩阵约定上可能有差异。TA 写屏幕空间效果、顶点偏移或自定义投影时，需要确认当前引擎宏和平台约定。

## 用途

- 在材质或 Shader 调试中定位与 Clip Space 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[View Space]] | View Space 以相机为参考；Clip Space 加入投影和齐次裁剪。 |
| [[Screen Space]] | Screen Space 是屏幕像素或归一化坐标；Clip Space 仍处在透视除法之前。 |

## 常见误区

1. 把 Clip Space 当成线性世界距离使用。
2. 忽略不同图形 API 的深度范围差异。
3. 手写全屏效果时忘记处理 Y 翻转或反向 Z。

## 相关条目

- [[View Space]]：Clip Space 通常由 View Space 经投影矩阵得到。
- [[Screen Space]]：Clip Space 透视除法和视口映射后进入屏幕空间。
- [[Vertex Shader]]：顶点着色器通常输出 Clip Space 位置。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
