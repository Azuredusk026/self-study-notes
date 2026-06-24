---
title: "Normal Map"
aliases:
  - 法线贴图
category: "Shader"
tags: [技术美术, Shader, Texture, Lighting]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Normal Map

## 定义与解释

Normal Map 用纹理存储表面法线扰动，让低模在光照中呈现高频细节。它改变的是光照响应，不改变模型轮廓。

## 核心原理

法线贴图通常把方向向量编码到 RGB 通道，再在 Shader 中解码为切线空间法线。片元阶段会用 TBN 基底把它转换到世界或视图空间，参与 PBR 或其他光照计算。

核心风险来自切线空间一致性。DCC、烘焙工具、Unity、Unreal、DirectX/OpenGL 法线方向和压缩格式可能不同。TA 需要检查绿通道方向、sRGB、压缩、切线生成方式、UV 接缝和镜像 UV。

## 用途

- 在材质或 Shader 调试中定位与 Normal Map 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Tangent Space]] | Tangent Space 提供法线贴图解码后的方向基底。 |
| [[PBR]] | PBR 使用 Normal Map 改变局部光照响应。 |

## 常见误区

1. 认为法线贴图会改变模型剪影。
2. 把 Normal Map 当 sRGB 颜色贴图导入。
3. 忽略切线空间不一致导致接缝和高光断裂。

## 相关条目

- [[Tangent Space]]：切线空间法线贴图依赖 TBN 基底。
- [[Texture Sampling]]：Normal Map 需要按线性数据采样。
- [[Baking]]：高模细节常通过 Baking 写入法线贴图。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
