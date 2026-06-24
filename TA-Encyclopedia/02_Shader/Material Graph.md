---
title: "Material Graph"
aliases:
  - 材质图
category: "02_Shader"
tags: [技术美术, Shader, Material]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---


# Material Graph

## 定义与解释

Material Graph 是用节点网络组织材质逻辑的编辑方式。它让美术和 TA 通过连接纹理、参数、数学节点和材质输出构建 Shader 行为。

## 核心原理

Material Graph 的核心是把材质计算表达成有向数据流。节点代表采样、数学、空间变换、分支或函数，连线代表数据依赖，最终由引擎生成或组合成 Shader 代码。

节点化提高可视化和复用性，但不自动保证性能。每个采样、分支、函数和关键字仍会进入实际 Shader。TA 需要把节点图拆解成采样次数、指令复杂度、变体数量和参数暴露规则来评估。

## 用途

- 在材质或 Shader 调试中定位与 Material Graph 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[HLSL]] | HLSL 是代码表达；Material Graph 是节点表达。 |
| [[Shader基础]] | Shader基础解释底层阶段；Material Graph 是引擎封装的创作界面。 |

## 常见误区

1. 认为节点图比手写 Shader 一定更便宜。
2. 节点复用不当导致隐藏采样和重复计算。
3. 暴露过多参数让材质规范失控。

## 相关条目

- [[Shader_Graph]]：Shader_Graph 是具体节点化 Shader 工具条目。
- [[Texture Sampling]]：材质图中纹理采样是常见节点。
- [[Keyword]]：材质图开关可能生成 Keyword。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
