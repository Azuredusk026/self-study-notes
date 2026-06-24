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

## 定义与解释

{title} 是技术美术知识库中的一个待精修主题，用来补齐渲染、Shader、引擎、资产生产或算法基础中的双链引用。

精修时需要说明它处理的对象、所在管线阶段、对资源或运行时结果的影响，以及它和相邻概念的边界。

## 核心原理

精修时根据 `{title}` 自身机制展开，不套用固定字段。可以按算法步骤、管线阶段、缓冲关系、资源规则、工具工作流、引擎系统或数学推导来组织。

需要说明它内部真正起作用的机制、依赖的上下文或约定、影响结果的关键细节，以及 Unity、Unreal、DCC 工具或第三方插件之间可能存在的实现差异。

## 用途

- 建立可检索的概念入口。
- 记录项目落地时的机制、约束和检查方法。
- 串联相关条目，减少知识库中的断链。

## 与其他概念的区别

| 概念 | 区别 |
|---|---|
| [[Shader基础]] | 如果本条目涉及材质或 GPU 计算，需要说明它和 Shader 执行阶段的关系。 |
| [[资源检查工具]] | 如果本条目涉及资产规范，需要说明它是否会进入自动化检查流程。 |

## 常见误区

1. 只建立空页面，不补充核心机制和项目用途。
2. 把工具名、概念名和实际工作流混在一起。
3. 没有标记待核验内容，导致版本差异或 API 行为被误写成定论。

## 相关条目

- [[Shader基础]]：用于判断本条目是否涉及 GPU 执行、材质参数或渲染状态。
- [[资源检查工具]]：用于判断本条目是否需要转化为可执行的资产检查规则。
- [[DCC工具链]]：用于判断本条目是否属于制作软件侧的流程节点。

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
