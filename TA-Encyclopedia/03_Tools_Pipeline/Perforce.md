---
title: "Perforce"
aliases:
  - Helix Core
category: "03_Tools_Pipeline"
tags: [技术美术, Pipeline, VersionControl]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Perforce

## 一句话定义

Perforce 是游戏行业常用的集中式版本控制系统，适合管理大量二进制资产和大项目内容。

## 为什么需要它

大型游戏项目有大量 `.uasset`、贴图、模型、音频和关卡文件。Perforce 的锁文件、流、权限和大文件处理能力适合美术和关卡团队协作。

## 核心原理

Perforce 使用集中式服务器保存版本，客户端同步工作区。二进制文件可通过 checkout/lock 控制编辑权，减少多人同时修改冲突。

> 待核验：Perforce 具体部署、许可和工作流策略依团队和版本而定。

## 技术美术中的典型用途

- 管理 Unreal 大型内容库。
- 锁定二进制资源。
- 版本回退和分支流管理。
- 与自动构建和资产检查集成。

## Unity 中的相关场景

Unity 项目也可使用 Perforce，尤其是大量美术二进制资源和多人协作项目。

## Unreal Engine 中的相关场景

Unreal 与 Perforce 集成常见，Content Browser 可显示 checkout 状态，适合 `.uasset` 和 `.umap` 协作。

## 常见误区

1. 以为 Perforce 能自动解决所有二进制冲突。
2. 没有锁文件规范，仍会出现覆盖。
3. 工作区映射过大，导致同步成本高。

## 面试可能怎么问

### Perforce 相比 Git LFS 的常见优势是什么？

回答要点：Perforce 对大规模二进制资产、文件锁、集中式权限和游戏内容库协作更成熟，但部署和管理成本也更高。

## 实践建议

设计一套内容目录锁定策略：关卡、角色、材质、贴图分别由谁 checkout，如何提交说明。

## 相关条目

- [[Git LFS]]
- [[Unreal_TA管线]]
- [[资源检查工具]]
- [[CI_CD for Game Assets]]

## 参考来源

- 待补充

