from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "00_Index" / "技术美术百科总目录.md"
EXCLUDED_DIRS = {".git", ".obsidian", "scripts"}


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def main() -> int:
    sections = [
        "---",
        'title: "技术美术百科总目录"',
        "aliases: []",
        'category: "Index"',
        "tags:",
        "  - index",
        "  - 技术美术",
        "status: active",
        'created: "2026-06-24"',
        'updated: "2026-06-24"',
        "confidence: medium",
        "---",
        "",
        "# 技术美术百科总目录",
        "",
        "> 此文件由 `scripts/build_index.py` 生成。需要手动导航说明时，请写入各目录 README。",
        "",
    ]

    for folder in sorted(p for p in ROOT.iterdir() if p.is_dir() and not is_excluded(p)):
        markdown_files = sorted(md for md in folder.glob("*.md") if md.name != "README.md")
        if not markdown_files:
            continue
        sections.append(f"## {folder.name}")
        sections.append("")
        for md in markdown_files:
            rel = md.relative_to(ROOT).with_suffix("").as_posix()
            sections.append(f"- [[{rel}|{md.stem}]]")
        sections.append("")

    OUT.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"Built {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

