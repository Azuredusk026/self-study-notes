from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_FILE = ROOT / "00_Index" / "术语索引.md"

EXCLUDED_DIRS = {".git", ".obsidian", "scripts", "90_Templates", "91_Sources", "92_Codex"}

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)

def main() -> int:
    notes = []

    for path in ROOT.rglob("*.md"):
        if is_excluded(path):
            continue

        if path.name == "README.md":
            continue

        notes.append(path)

    notes = sorted(notes, key=lambda p: p.stem.lower())

    lines = [
        "---",
        'title: "术语索引"',
        "category: index",
        "tags:",
        "  - index",
        "status: auto-generated",
        "created: auto",
        "updated: auto",
        "confidence: high",
        "---",
        "",
        "# 术语索引",
        "",
        "> 此文件由 `scripts/build_index.py` 生成。手动修改可能会被覆盖。",
        "",
    ]

    for path in notes:
        rel = path.relative_to(ROOT).with_suffix("")
        rel_link = str(rel).replace("\\", "/")
        lines.append(f"- [[{rel_link}|{path.stem}]]")

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Generated {INDEX_FILE.relative_to(ROOT)} with {len(notes)} entries.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())