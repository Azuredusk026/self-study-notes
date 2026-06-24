---
title: "GLSL"
aliases: []
category: "02_Shader"
confidence: medium
tags: [shader, glsl]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# GLSL

## 定义与解释

GLSL 是 OpenGL 和部分 Vulkan 生态中使用的 Shader 语言。它用于描述顶点、片元、计算等 GPU 阶段的程序逻辑。

## 核心原理

GLSL 的机制与图形管线阶段绑定：不同 Shader 阶段声明输入输出变量，编译后由驱动或工具链转换为 GPU 可执行代码。它强调类型、向量矩阵运算、采样器和内建变量。

在游戏引擎中，TA 很少直接维护纯 GLSL，但移动端、WebGL、工具插件、Shader 跨编译和 RenderDoc 调试中会遇到它。需要注意 GLSL 版本、精度限定、坐标约定和与 HLSL 交叉编译时的语义差异。

## 用途

- 在材质或 Shader 调试中定位与 GLSL 相关的画面异常、编译问题、性能成本或资源配置错误。
- 把概念落到 Unity ShaderLab/Shader Graph、Unreal Material Editor、RenderDoc 或引擎材质面板中可观察的参数和状态。
- 为美术暴露稳定的材质控制项，同时限制采样次数、变体数量、精度和平台差异带来的风险。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[HLSL]] | 两者语法和生态不同，但都表达 GPU 阶段逻辑。 |
| [[Shader基础]] | Shader基础讲概念；GLSL 是具体语言。 |

## 常见误区

1. 把 HLSL 语义直接照搬到 GLSL 而不检查坐标和矩阵约定。
2. 忽略 GLSL ES 精度限定导致移动端异常。
3. 未确认引擎是否通过跨编译生成 GLSL。

## 相关条目

- [[HLSL]]：HLSL 是 Unity/DirectX/Unreal 中更常见的 Shader 语言。
- [[Precision]]：GLSL ES 中精度限定会直接影响移动端结果。
- [[Shader基础]]：GLSL 是 Shader 编写语言之一。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
