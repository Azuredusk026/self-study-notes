---
title: "Git LFS"
aliases:
  - Git Large File Storage
category: "03_Tools_Pipeline"
tags: [技术美术, Pipeline, VersionControl]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# Git LFS

## 一句话定义

Git LFS 是 Git 的大文件管理扩展，用指针文件替代直接把大型二进制资源写入普通 Git 历史。

## 为什么需要它

游戏项目里贴图、模型、音频、视频和工程二进制文件很大。普通 Git 管理这些文件会让仓库迅速膨胀，拉取和切分支变慢。Git LFS 能缓解大文件历史压力，但需要团队正确配置。

## 核心原理

Git 仓库中保存 LFS 指针，真实大文件保存在 LFS 存储中。检出时客户端根据指针下载对应文件。

> 待核验：不同 Git 托管平台的 LFS 配额、锁文件能力和计费策略不同，需要按实际平台确认。

## 技术美术中的典型用途

- 管理 PSD、FBX、PNG、TGA、WAV、视频等大文件。
- 避免二进制资源撑爆 Git 历史。
- 与 CI 构建、资产下载和版本回滚配合。

## Unity 中的相关场景

Unity 项目常将大贴图、模型、音频加入 LFS，同时保留 `.meta` 文件在普通 Git 中，保证 GUID 稳定。

## Unreal Engine 中的相关场景

Unreal 的 `.uasset`、`.umap` 是二进制资产，团队通常需要 LFS 或 Perforce 管理，并考虑锁定策略。

## 常见误区

1. 项目中途才加 LFS，旧历史已经变大。
2. 忘记提交 `.gitattributes`，导致团队规则不一致。
3. 二进制文件多人同时改，没有锁定或协作流程。

## 面试可能怎么问

### Git LFS 解决什么问题？

回答要点：它把大文件内容移出普通 Git 对象库，用指针跟踪版本，降低仓库历史膨胀和克隆压力。

## 实践建议

为贴图、模型、音频建立 `.gitattributes`，并写一份“哪些文件必须走 LFS”的团队规范。

## 相关条目

- [[DCC工具链]]
- [[资源检查工具]]
- [[Unity_TA管线]]
- [[Unreal_TA管线]]

## 参考来源

- 待补充

