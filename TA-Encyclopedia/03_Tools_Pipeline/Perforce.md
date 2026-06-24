---
title: "Perforce"
aliases:
  - Helix Core
category: "03_Tools_Pipeline"
tags: [技术美术, Pipeline, VersionControl]
status: active
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---


# Perforce

## 定义与解释

Perforce 是大型游戏项目中常见的集中式版本管理系统，适合管理大量二进制资产、锁文件和大规模团队协作。

## 核心原理

Perforce 的核心是中心服务器、Workspace、Changelist、文件类型和锁定机制。美术可以 checkout 独占编辑二进制文件，提交时保留变更列表和文件状态。

它适合大型资产库，但需要清晰的 Depot 结构、权限、文件类型、Ignore 规则、锁定策略和自动化同步。TA 需要考虑 DCC/引擎临时文件、生成文件、构建机器和资源检查流程如何与 Perforce 协作。

## 用途

- 把 Perforce 纳入资产生产、检查、导出、导入或版本管理流程，减少人工操作和沟通成本。
- 把团队规范转成可执行规则、工具入口或自动化报告，让问题尽早暴露。
- 连接 DCC、引擎、版本库和 CI/CD，让美术资产从制作到落地有可追踪的状态。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Git LFS]] | Git LFS 基于 Git 扩展；Perforce 原生支持大规模二进制和锁定工作流。 |
| [[CI_CD for Game Assets]] | Perforce 管版本；CI/CD 管自动检查和构建反馈。 |

## 常见误区

1. 没有文件锁策略导致二进制资产互相覆盖。
2. Depot 中混入缓存和临时文件。
3. 构建机器同步规则不稳定，导致资源版本不可复现。

## 相关条目

- [[Git LFS]]：Git LFS 是另一种大文件管理方案。
- [[目录规范]]：Perforce Depot 结构需要目录规范支撑。
- [[CI_CD for Game Assets]]：CI 需要从 Perforce 同步资产。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
