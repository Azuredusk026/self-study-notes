---
tags: [rendering, deferred-rendering]
status: draft
created: 2026-06-24
updated: 2026-06-24
---

# Deferred Rendering

## 一句话总结

延迟渲染把几何信息写入 G-Buffer，再在屏幕空间集中计算光照。

## 优点

- 适合大量动态光源
- 光照计算和几何复杂度解耦

## 局限

- 透明物体处理复杂
- G-Buffer 带宽和显存压力较高
- MSAA 支持成本更高

