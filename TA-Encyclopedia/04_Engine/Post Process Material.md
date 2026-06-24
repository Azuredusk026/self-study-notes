---
title: "Post Process Material"
aliases:
  - 后处理材质
category: "04_Engine"
tags: [技术美术, Unreal, PostProcessing]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Post Process Material

## 定义与解释

Post Process Material 是 Unreal 中用于在后处理阶段读取场景缓冲并修改最终画面的材质类型。

## 核心原理

它的核心是材质不再服务单个物体表面，而是在屏幕空间处理 Scene Color、Scene Depth、Custom Depth、GBuffer 或自定义输入。材质输出会插入后处理链的指定位置，影响整屏或局部区域。

TA 需要确认 Blendable Location、输入缓冲、颜色空间、深度重建、分辨率、透明物体参与和性能成本。描边、色彩风格化、局部高亮和屏幕特效都容易因为执行顺序或缓冲缺失产生错误。

## 用途

- 在引擎项目中定位与 Post Process Material 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Material Instance]] | Material Instance 覆盖材质参数；Post Process Material 定义后处理材质用途。 |
| [[后处理]] | 后处理是阶段；Post Process Material 是 Unreal 中的实现载体。 |

## 常见误区

1. 不知道材质插入后处理链的位置。
2. 读取了未启用的 Custom Depth 或 GBuffer 数据。
3. 全屏效果叠加过多导致带宽和采样成本过高。

## 相关条目

- [[Custom Depth]]：后处理材质常读取 Custom Depth 做描边或高亮。
- [[Screen Space]]：Post Process Material 多在屏幕空间工作。
- [[Material Editor]]：后处理材质也通过材质编辑器创建。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
