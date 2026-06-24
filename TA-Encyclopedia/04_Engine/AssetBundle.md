---
title: "AssetBundle"
aliases: []
category: "04_Engine"
confidence: medium
tags: [unity, assetbundle, resource-management]
status: active
created: 2026-06-24
updated: "2026-06-24"
---


# AssetBundle

## 定义与解释

AssetBundle 是 Unity 用于打包、分发和运行时加载资源的资源包机制。它可以把 Prefab、材质、贴图、场景等资产从主包中拆分出来管理。

## 核心原理

AssetBundle 的核心是构建时把资产和依赖序列化成独立包，运行时再从本地或远程加载包和其中的对象。包之间可能存在依赖，加载顺序、引用关系和卸载策略会直接影响内存和资源可用性。

TA 需要理解 AssetBundle 名称、变体、依赖分析、冗余资源、压缩格式、Manifest 和卸载行为。错误的依赖组织会导致包体膨胀、重复资源、加载失败或卸载后引用丢失。

## 用途

- 在引擎项目中定位与 AssetBundle 相关的资源导入、渲染表现、运行时加载、编辑器工具或构建问题。
- 把引擎功能转化为团队可执行的资产规范、材质模板、工具入口和调试流程。
- 与程序协作确认运行时成本、平台限制、版本差异和可维护边界。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Addressables]] | Addressables 提供地址和 Catalog 层；AssetBundle 更接近底层包和依赖。 |
| [[RenderTexture]] | AssetBundle 管资源分发；RenderTexture 是运行时渲染资源。 |

## 常见误区

1. 只看包数量，不检查依赖重复。
2. 卸载 Bundle 时误以为已实例化对象一定安全。
3. 不同平台使用同一 Bundle 产物，忽略平台构建差异。

## 相关条目

- [[Addressables]]：Addressables 常封装 AssetBundle 构建和加载。
- [[YooAsset]]：YooAsset 也围绕资源包和清单管理。
- [[Unity]]：AssetBundle 是 Unity 资源系统的一部分。

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
