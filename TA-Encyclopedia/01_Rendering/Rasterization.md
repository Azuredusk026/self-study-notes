---
title: "Rasterization"
aliases:
  - 光栅化
category: "Rendering"
tags: [技术美术, Rendering, GPU]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Rasterization

## 一句话定义

Rasterization 是把三角形等几何图元转换成屏幕像素或采样点覆盖结果的过程。

## 为什么需要它

实时游戏通常用三角网格描述角色、场景和特效模型，但屏幕最终需要的是像素。光栅化负责判断每个图元覆盖哪些屏幕位置，并把插值后的顶点属性交给 [[Fragment Shader]] 或 Pixel Shader。TA 在排查锯齿、Overdraw、深度冲突、透明排序和移动端性能时，经常需要理解这一阶段。

## 核心原理

- 输入：裁剪空间或屏幕空间图元、顶点属性、深度信息。
- 处理过程：图元装配、裁剪、屏幕映射、覆盖测试、属性插值。
- 输出：片元候选数据，包括屏幕坐标、深度、UV、法线、颜色等插值结果。
- 所在层级：GPU 固定功能阶段，位于 [[Vertex Shader]] 之后、[[Fragment Shader]] 之前。

## 技术美术中的典型用途

- 解释为什么三角面过密会增加片元压力。
- 判断 Alpha Blend 粒子、毛发、草地造成的 Overdraw。
- 分析描边、卡通渲染、深度预通道和 Early-Z 的关系。
- 配合 RenderDoc 或 Frame Debugger 查看 Draw Call 的实际覆盖区域。

## Unity 中的相关场景

Unity 中无论 Built-in、URP 还是 HDRP，普通 Mesh 渲染都会经过光栅化。TA 常在 Scene View Overdraw、Frame Debugger、RenderDoc 中观察一个材质或特效是否产生过多片元。

## Unreal Engine 中的相关场景

Unreal 的 Base Pass、Depth Prepass、Shadow Pass 都依赖光栅化。Nanite 改变了几何处理方式，但最终仍需要生成可用于屏幕着色或深度测试的覆盖结果。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| Rasterization | 把几何覆盖转换为片元 |
| Ray Tracing | 按光线查询场景交点 |
| Fragment Shader | 对光栅化产生的片元执行着色 |

## 常见误区

1. 以为顶点少就一定性能好：大面积透明片元可能比高模更贵。
2. 以为光栅化等于最终像素：片元还可能被深度、模板或裁剪丢弃。
3. 以为所有片元都会写入颜色：Depth Only、Shadow Pass 可能只写深度。

## 面试可能怎么问

### 光栅化在渲染管线中的位置是什么？

回答要点：它位于顶点处理和片元着色之间，负责把图元覆盖转成片元，并插值顶点属性。

### 为什么透明粒子容易造成性能问题？

回答要点：透明物体通常不能充分利用 Early-Z，同一屏幕区域可能被多层片元重复着色。

## 实践建议

做一个简单场景：用一张大透明面片叠加几十层粒子，然后在 Unity Scene View 或 RenderDoc 中观察 Overdraw。

## 相关条目

- [[Vertex Shader]]
- [[Fragment Shader]]
- [[Overdraw]]
- [[Z-Test]]

## 参考来源

- 待补充

