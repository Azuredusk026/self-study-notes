---
title: "Texel Density"
aliases:
  - 纹素密度
category: "05_Art_Production"
tags: [技术美术, ArtProduction, UV, Texture]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Texel Density

## 一句话定义

Texel Density 表示模型表面单位长度对应多少贴图像素，用于控制不同资产的贴图清晰度一致性。

## 为什么需要它

同一个场景中，如果桌子清晰、墙面模糊、角色局部过密，视觉会不统一，也会浪费贴图预算。TA 需要制定纹素密度标准，帮助美术在画质和内存之间平衡。

## 核心原理

纹素密度由模型实际尺寸、UV 占用面积和贴图分辨率共同决定。规范通常按“像素/米”或“像素/厘米”描述。

## 技术美术中的典型用途

- 场景资产清晰度统一。
- 角色不同部位贴图预算分配。
- Trim Sheet 和 Texture Atlas 规划。
- 移动端贴图内存控制。

## Unity 中的相关场景

Unity 中需要结合平台压缩格式、Mipmap、Streaming Mipmaps 和相机距离判断实际贴图质量。

## Unreal Engine 中的相关场景

Unreal 中可结合 Texture Streaming、Material Instance、Virtual Texture 等系统管理贴图显示和内存。

## 常见误区

1. 所有资产用同一贴图分辨率，不看实际尺寸和屏幕占比。
2. UV 岛缩放不一致，导致同一资产局部清晰度差异大。
3. 只追求高清，不考虑内存和加载。

## 面试可能怎么问

### Texel Density 为什么重要？

回答要点：它保证资产之间贴图清晰度一致，并帮助团队在画质、内存和生产成本之间制定标准。

## 实践建议

为一组场景道具制定统一纹素密度，并在 DCC 中检查 UV 岛比例。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[建模规范]] | 建模规范偏输入资产质量；本条目可能关注某个具体制作或优化环节。 |
| [[贴图规范]] | 贴图规范偏纹理侧约束；本条目可能覆盖几何、绑定、动画或特效。 |

## 相关条目

- [[UV]]
- [[贴图规范]]
- [[Mipmap]]
- [[Texture Compression]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
