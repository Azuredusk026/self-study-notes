from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "00_Index" / "术语索引.md"
INCLUDED_DIRS = {f"{i:02d}_" for i in range(1, 8)}


def included_folder(path: Path) -> bool:
    return any(path.name.startswith(prefix) for prefix in INCLUDED_DIRS)


def read_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip().strip('"')
            return title or path.stem
    return path.stem


def group_key(label: str) -> str:
    first = label.strip()[0].upper() if label.strip() else "#"
    return first if "A" <= first <= "Z" else "中文"


def main() -> int:
    entries = []
    for folder in sorted(p for p in ROOT.iterdir() if p.is_dir() and included_folder(p)):
        for path in sorted(folder.glob("*.md")):
            if path.name == "README.md":
                continue
            label = read_title(path).replace("_", " ")
            rel = "../" + path.relative_to(ROOT).as_posix()
            entries.append((label, rel))

    groups = {}
    for label, rel in entries:
        groups.setdefault(group_key(label), []).append((label, rel))

    lines = [
        "---",
        'title: "术语索引"',
        "aliases: []",
        'category: "Index"',
        "tags:",
        "  - index",
        "  - terms",
        "  - 技术美术",
        "status: active",
        'created: "2026-06-24"',
        'updated: "2026-06-24"',
        "confidence: medium",
        "---",
        "",
        "# 术语索引",
        "",
        "> 本索引覆盖 01-08 目录下的技术条目和工具条目；具体导航以各目录 README 和 [[技术美术百科总目录]] 为准。",
        "",
    ]

    for key in [chr(c) for c in range(ord("A"), ord("Z") + 1)] + ["中文"]:
        values = groups.get(key, [])
        if not values:
            continue
        lines.append(f"## {key}")
        lines.append("")
        for label, rel in sorted(values, key=lambda item: item[0].lower()):
            lines.append(f"- {label}: [{label}]({rel})")
        lines.append("")

    OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Updated {OUT.relative_to(ROOT)} with {len(entries)} entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
