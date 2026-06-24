from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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
created: "2026-06-24"
updated: "2026-06-24"
confidence: low
---

# {title}

## 一句话定义

{title} 是后续需要扩充的技术美术相关主题。本页当前用于补全知识库双链，避免核心条目引用到不存在的页面。

## 为什么需要它

该主题已经在第一轮核心条目中被引用，说明它与渲染、Shader、引擎、资产生产或算法基础存在直接关系。

## 待补充

- 概念定义
- 核心原理
- TA 使用场景
- Unity / Unreal 相关场景
- 常见误区
- 面试问题
- 实践建议

## 相关条目

- [[技术美术百科总目录]]
- [[待扩充条目]]

## 参考来源

- 待补充
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

