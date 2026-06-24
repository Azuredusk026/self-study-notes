---
title: "Inpainting"
aliases:
  - 局部重绘
category: "06_AIGC_TA"
tags: [技术美术, AIGC, Workflow]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Inpainting

## 定义与解释

Inpainting 是对图像局部区域进行重绘的生成流程，常用于修复错误、替换局部、补全遮挡或迭代资产细节。

## 核心原理

Inpainting 的核心是用 Mask 指定需要重绘的区域，模型在保留未遮罩区域的基础上重新生成局部内容。Mask 边缘、羽化、Denoise、上下文范围和 Prompt 会决定新旧区域是否自然融合。

TA 使用 Inpainting 时要关注边界一致性、光照透视、材质连续性和可追溯记录。局部修复不能替代 DCC 精修，尤其是正式贴图、UI 或角色素材仍需要人工检查。

## 用途

- 在 AIGC 资产流程中定位与 Inpainting 相关的可复现性、质量、风格一致性或审核风险。
- 把生成过程转成可记录、可复跑、可比较的工作流，而不是只保存单张结果图。
- 连接概念探索、参考生成、DCC 精修、引擎导入和来源审核，避免临时素材直接混入正式资产。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Img2Img]] | Img2Img 通常影响整图；Inpainting 只重绘 Mask 区域。 |
| [[Dissolve]] | Dissolve 使用遮罩做渲染效果；Inpainting 使用遮罩控制生成区域。 |

## 常见误区

1. Mask 边缘过硬导致修复痕迹明显。
2. 只看局部细节，不检查整体透视和光照。
3. 覆盖原图但不保留修复记录。

## 相关条目

- [[Img2Img]]：Inpainting 是局部重绘形式。
- [[贴图规范]]：遮罩图的通道、边缘和格式需要符合贴图规范。
- [[AIGC 资产审核规范]]：修复后的资产仍需审核。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
