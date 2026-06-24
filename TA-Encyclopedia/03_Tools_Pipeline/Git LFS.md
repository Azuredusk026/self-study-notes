---
title: "Git LFS"
aliases:
  - Git Large File Storage
category: "03_Tools_Pipeline"
tags: [技术美术, Pipeline, VersionControl]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Git LFS

## 定义与解释

Git LFS 是 Git 的大文件扩展，用指针文件替代仓库中的大型二进制内容，并把真实文件存储在 LFS 服务中。它常用于贴图、模型、音频和二进制资产版本管理。

## 核心原理

Git LFS 的核心是把指定模式的文件通过 `.gitattributes` 交给 LFS 管理。Git 仓库保存轻量指针，checkout 或 pull 时再按需下载真实文件。

对游戏资产来说，Git LFS 能减轻仓库膨胀，但不能解决二进制合并冲突、锁文件流程、存储配额和下载速度问题。TA 或工具链维护者需要明确哪些格式进 LFS、哪些文件需要锁定、CI 如何拉取 LFS，以及美术误提交普通 Git 后如何修复。

## 用途

- 把 Git LFS 纳入资产生产、检查、导出、导入或版本管理流程，减少人工操作和沟通成本。
- 把团队规范转成可执行规则、工具入口或自动化报告，让问题尽早暴露。
- 连接 DCC、引擎、版本库和 CI/CD，让美术资产从制作到落地有可追踪的状态。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Perforce]] | Git LFS 扩展 Git 管理大文件；Perforce 原生面向大规模二进制和锁文件工作流。 |
| [[Git LFS]] | 本条目关注 LFS 机制，不等同于完整版本管理策略。 |

## 常见误区

1. 以为用了 LFS 就能解决二进制合并问题。
2. 忘记配置 `.gitattributes`，大文件已经进入普通 Git 历史。
3. CI 没有拉取 LFS 内容导致构建缺资源。

## 相关条目

- [[Perforce]]：Perforce 是大型二进制资产管理的常见替代方案。
- [[CI_CD for Game Assets]]：CI 拉取资产时需要处理 LFS 文件。
- [[目录规范]]：目录规范常配合 LFS 追踪规则。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
