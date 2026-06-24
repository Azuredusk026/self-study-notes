---
title: "Unreal Render Target"
aliases:
  - Unreal Render Target
category: "04_Engine"
tags: [技术美术, Unreal, Rendering]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Unreal Render Target

## 定义与解释

Unreal Render Target 是 Unreal 中可被相机、Scene Capture、材质或蓝图写入和读取的渲染目标资源。

## 核心原理

它的核心是把某次渲染或绘制结果保存到 Texture Render Target，再供材质、UI、后处理或工具逻辑采样。常见来源包括 SceneCapture2D、Canvas 绘制、Niagara 或自定义渲染流程。

TA 需要关注 Render Target 格式、分辨率、更新频率、Mip、HDR、清理方式和读回成本。实时 Scene Capture 或高分辨率 RT 很容易造成性能和显存压力，尤其在 UI 预览、镜面、监控屏和特效中。

## 用途

- 在引擎项目中定位与 Unreal Render Target 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[RenderTexture]] | 两者分别是 Unreal 和 Unity 的渲染目标资源。 |
| [[Framebuffer]] | Framebuffer 是底层附件集合；Render Target 是引擎暴露的纹理资源。 |

## 常见误区

1. 每帧更新多个高分辨率 Scene Capture。
2. RT 格式和颜色空间选择错误。
3. 把 GPU RT 频繁读回 CPU 造成卡顿。

## 相关条目

- [[RenderTexture]]：Unity 中类似的渲染目标资源。
- [[Render Target]]：通用渲染目标概念。
- [[Post Process Material]]：后处理材质可读取 RT 或屏幕缓冲。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
