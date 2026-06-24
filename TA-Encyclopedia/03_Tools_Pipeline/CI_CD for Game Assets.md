---
title: "CI/CD for Game Assets"
aliases:
  - 游戏资产 CI/CD
  - CI_CD for Game Assets
category: "03_Tools_Pipeline"
tags: [技术美术, Pipeline, Automation]
status: draft
created: "2026-06-24"
updated: "2026-06-24"
confidence: medium
---

# CI/CD for Game Assets

## 一句话定义

CI/CD for Game Assets 是把资源检查、构建、报告和发布流程自动化的资产管线实践。

## 为什么需要它

游戏资产错误如果靠人工发现，往往太晚。CI 可以在提交后自动检查命名、格式、依赖、包体、构建和性能预算，把问题提前暴露。

## 核心原理

自动化系统监听提交或定时任务，拉取资源，运行检查脚本或引擎命令行，生成报告，并按规则阻塞或提醒。

> 待核验：具体 CI 系统、Unity/Unreal 命令行参数和认证方式需要按项目环境确认。

## 技术美术中的典型用途

- 自动跑资源检查。
- 生成贴图、模型、动画问题报告。
- 检查 Addressables/AssetBundle 依赖。
- 构建每日包和资产预算报表。

## Unity 中的相关场景

Unity 可通过 batchmode 运行编辑器检查脚本，输出 JSON、HTML 或控制台报告。

## Unreal Engine 中的相关场景

Unreal 可用命令行、Data Validation、Cook 和自动化测试生成内容检查结果。

## 常见误区

1. 一开始就阻塞所有警告，团队无法推进。
2. 报告不可读，没人修。
3. 检查规则没有版本管理。

## 面试可能怎么问

### 如何把资源检查接入 CI？

回答要点：把检查逻辑做成可命令行运行的脚本，CI 拉取项目后执行，输出报告，并按错误级别决定提醒或阻塞。

## 实践建议

先把 Texture 和 Mesh 检查接入 CI，每天生成一份新增问题报告，不要一开始就阻塞全部历史问题。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[DCC工具链]] | DCC 工具链偏制作软件侧；Pipeline 更强调跨软件、跨引擎和团队流程。 |
| [[资源检查工具]] | 资源检查工具是管线中的一个执行节点，不等同于完整管线设计。 |

## 相关条目

- [[资源检查工具]]
- [[Unity Editor Tool]]
- [[Unreal Python]]
- [[AIGC 资产审核规范]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
