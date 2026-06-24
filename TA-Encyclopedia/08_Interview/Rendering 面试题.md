---
title: "Rendering 面试题"
aliases: []
category: "08_Interview"
tags: [技术美术, Interview, Rendering]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: high
---

# Rendering 面试题

## 问题 1：Forward Rendering 和 Deferred Rendering 有什么区别？

### 考察点

- 渲染路径
- 多光源场景
- 透明和 MSAA

### 推荐回答

Forward Rendering 在绘制物体时直接计算光照，透明和 MSAA 通常更自然，适合移动端、VR、角色或光源数量较少的场景。Deferred Rendering 先把几何信息写入 G-Buffer，再在屏幕空间计算光照，适合大量动态光源，但 G-Buffer 带宽和显存压力更高，透明处理也更复杂。

### 追问方向

- 为什么 Deferred 不擅长透明？
- G-Buffer 一般存什么？

### 相关条目

- [[Forward_Rendering|Forward Rendering]]
- [[Deferred_Rendering|Deferred Rendering]]
- [[G-Buffer]]

## 问题 2：Early-Z 为什么能优化性能？

### 考察点

- Depth Buffer
- 片元着色成本
- 透明和 Alpha Test 的影响

### 推荐回答

Early-Z 会在 Fragment Shader 执行前尽早做深度测试，被遮挡的片元可以直接丢弃，从而避免纹理采样和光照计算。它对复杂材质、遮挡关系明确的场景很有价值，但透明、discard/clip、深度写入策略可能影响它的收益。

### 相关条目

- [[Early-Z]]
- [[Depth Buffer]]
- [[Z-Test]]
- [[Alpha Test]]

## 问题 3：Bloom 的基本流程是什么？

### 考察点

- 后处理流程
- Render Target
- HDR 和 Tone Mapping

### 推荐回答

Bloom 通常从 HDR 场景颜色中提取高亮区域，经过多级降采样和模糊，再上采样合成回原图。它只模拟亮部扩散，不会真正照亮周围物体，所以不能替代灯光和 GI。

### 相关条目

- [[Bloom]]
- [[RenderTexture]]
- [[Tone Mapping]]

