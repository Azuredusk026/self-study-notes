---
title: "IBL"
aliases:
  - Image Based Lighting
  - 图像基光照
category: "Rendering"
tags: [技术美术, Rendering, PBR, Lighting]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# IBL

## 一句话定义

IBL 使用环境贴图或预计算环境信息为物体提供间接光照和反射。

## 为什么需要它

真实场景中的物体不只受直接灯光影响，也会反射天空、房间和周围环境。IBL 让 PBR 材质在没有大量真实光源时仍能表现合理的金属反射、粗糙反射和环境漫反射。

## 核心原理

- 输入：环境 Cubemap、法线、视线方向、Roughness、Metallic。
- 处理过程：根据材质属性采样预过滤环境贴图和 BRDF LUT。
- 输出：环境漫反射和环境镜面反射。
- 所在层级：PBR Shader 和引擎光照系统。

## 技术美术中的典型用途

- 设置 Reflection Probe / Sky Light。
- 调整角色在不同场景中的材质一致性。
- 解决金属材质发黑或反射不合理。
- 管理移动端环境反射质量和性能。

## Unity 中的相关场景

Unity 使用 Reflection Probe、Skybox、Light Probe 等提供环境光照。URP/HDRP 的 Lit 材质会根据 Smoothness 和 Probe 数据显示反射。

## Unreal Engine 中的相关场景

Unreal 中 Sky Light、Reflection Capture、Lumen 反射等都会影响环境光照。不同项目设置会显著改变 PBR 材质观感。

## 常见误区

1. 只调材质不调环境，导致 PBR 看起来错误。
2. 金属材质缺少环境反射时发黑，以为贴图坏了。
3. Probe 分辨率、范围和更新策略不合理。

## 面试可能怎么问

### 为什么 PBR 材质需要 IBL？

回答要点：PBR 需要环境间接光和反射来表达真实材质，尤其金属和高光表面对环境非常敏感。

## 实践建议

同一个金属材质球分别放在无环境、室内 HDRI、室外 HDRI 中，观察反射和亮度差异。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[PBR]] | 更偏材质和光照模型；本条目更关注具体渲染环节或画面效果。 |
| [[Shader基础]] | Shader 是实现手段；本条目通常还涉及管线状态、缓冲读写和引擎配置。 |

## 相关条目

- [[PBR]]
- [[BRDF]]
- [[Reflection Probe]]
- [[Light Probe]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
