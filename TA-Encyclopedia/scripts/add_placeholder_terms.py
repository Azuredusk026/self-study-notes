from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-06-24"

TERMS = {
    "01_Rendering": [
        "Tone Mapping",
        "Roughness",
        "Metallic",
        "Fresnel",
        "SSAO",
        "Depth of Field",
        "Stencil Buffer",
        "Reflection Probe",
        "Light Probe",
        "Lambert",
    ],
    "02_Shader": [
        "Screen Space",
        "Mipmap",
        "Dissolve",
        "Keyword",
        "Branch",
    ],
    "04_Engine": [
        "MaterialPropertyBlock",
        "SRP Batcher",
    ],
    "05_Art_Production": [
        "Draw Call",
        "Baking",
        "Pivot",
    ],
    "07_Math_CS": [
        "Graph",
        "Dijkstra",
        "游戏AI",
    ],
}


def content(title: str, category: str) -> str:
    return f"""---
title: "{title}"
aliases: []
category: "{category}"
tags:
  - 技术美术
status: draft
created: "{TODAY}"
updated: "{TODAY}"
confidence: low
---

# {title}

## 一句话定义

{title} 是技术美术知识库中的一个待精修主题，用来补齐渲染、Shader、引擎、资产生产或算法基础中的双链引用。

## 为什么需要它

该主题已经被其他条目引用，说明它和项目中的资源制作、引擎落地、画面表现、工具链或面试知识存在关联。先建立标准结构，可以保证后续扩写时不遗漏工程视角。

## 核心原理

- 输入：相关资源、参数、引擎配置或算法数据。
- 处理过程：根据所在管线阶段完成计算、转换、检查、生成或调试。
- 输出：可观察的画面结果、资产状态、工具报告、运行时数据或面试表达要点。
- 所在层级：GPU / 引擎 / DCC / Pipeline / AIGC 工作流，需在精修时确认。

## 技术美术中的典型用途

- 建立可检索的概念入口。
- 记录项目落地时的输入、输出和检查方法。
- 串联相关条目，减少知识库中的断链。

## Unity 中的相关场景

精修时补充 Unity 中对应的工具入口、导入设置、渲染管线、Profiler/Frame Debugger 排查方式或项目案例。

## Unreal Engine 中的相关场景

精修时补充 Unreal Engine 中对应的编辑器系统、材质/渲染工具、内容管线、调试方式或项目案例。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[技术美术百科总目录]] | 总目录用于导航，本条目用于解释具体概念。 |
| [[术语索引]] | 术语索引用于检索，本条目用于沉淀定义、原理和实践。 |

## 常见误区

1. 只建立空页面，不补充输入、输出和项目用途。
2. 把工具名、概念名和实际工作流混在一起。
3. 没有标记待核验内容，导致版本差异或 API 行为被误写成定论。

## 面试可能怎么问

### 问题 1

这个概念在 TA 工作中解决什么问题？

回答要点：说明它影响的资源、画面、工具或性能环节。

### 问题 2

它在 Unity 和 Unreal 中有什么落地差异？

回答要点：比较工具入口、数据流、调试方式和项目约束。

### 问题 3

项目里遇到相关问题时如何排查？

回答要点：从输入资产、引擎配置、运行时表现和最小复现场景逐层定位。

## 实践建议

- 后续精修时优先补充项目中真实可复现的案例。
- 涉及具体版本、API 或工具行为时，先登记来源再下结论。
- 保持相关条目双链准确，不为近义词重复创建新文件。

## 相关条目

- [[技术美术百科总目录]]
- [[术语索引]]
- [[待扩充条目]]

## 参考来源

- 见 [[91_Sources/source_registry|Source Registry]]；未核验的外部资料按 `待核验` 处理，不编造链接。
"""


def main() -> int:
    created = 0
    for folder, names in TERMS.items():
        target_dir = ROOT / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        for name in names:
            path = target_dir / f"{name}.md"
            if path.exists():
                continue
            path.write_text(content(name, folder), encoding="utf-8")
            created += 1
    print(f"Created {created} placeholder terms.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
