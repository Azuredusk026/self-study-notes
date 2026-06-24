---
title: "Addressables"
aliases: []
category: "04_Engine"
confidence: medium
tags: [unity, addressables, resource-management]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# Addressables

## 定义与解释

Addressables 是 Unity 的地址化资源管理框架，用地址、Label、Group 和 Catalog 组织资源加载、打包、远程更新和依赖管理。

## 核心原理

Addressables 的核心是把资源引用从直接对象引用改成可寻址句柄。编辑器中资源被分入 Group，构建时生成 Catalog 和资源包；运行时通过地址或 Label 查找依赖、加载资源、实例化对象并释放句柄。

它解决的是资源生命周期和分发管理问题，不只是换一种加载 API。TA 需要关注 Group 规则、Label 规范、依赖冗余、远程 Catalog、缓存、资源释放和构建报告。错误的分组会造成重复打包、加载峰值过高或热更新粒度失控。

## 用途

- 在引擎项目中定位与 Addressables 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[AssetBundle]] | AssetBundle 是包格式和加载机制；Addressables 是更上层的地址化管理框架。 |
| [[YooAsset]] | 两者都管理 Unity 资源加载和更新，但工作流和 API 不同。 |

## 常见误区

1. 只按文件夹分 Group，不检查依赖重复。
2. 加载后不释放句柄导致内存无法回收。
3. 把 Addressables 当作自动热更新方案，忽略 Catalog 和服务器部署规则。

## 相关条目

- [[AssetBundle]]：Addressables 底层可基于 AssetBundle 构建资源包。
- [[YooAsset]]：YooAsset 是 Unity 资源管理替代方案之一。
- [[Unity_TA管线]]：Addressables 需要纳入 Unity 资产管线规则。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
