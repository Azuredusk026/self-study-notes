from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def infer_title(path: Path) -> str:
    return path.parent.name if path.name == "README.md" else path.stem


def infer_category(path: Path) -> str:
    return path.parent.name if path.parent != ROOT else "Root"


def normalize(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    title = infer_title(path)
    category = infer_category(path)

    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end == -1:
            return False
        block = text[4:end]
        lines = block.splitlines()
        keys = {line.split(":", 1)[0].strip() for line in lines if ":" in line}
        insert = []
        if "title" not in keys:
            insert.append(f'title: "{title}"')
        if "aliases" not in keys:
            insert.append("aliases: []")
        if "category" not in keys:
            insert.append(f'category: "{category}"')
        if "confidence" not in keys:
            insert.append("confidence: medium")
        if not insert:
            return False
        new_text = "---\n" + "\n".join(insert + lines) + "\n---" + text[end + 4 :]
        path.write_text(new_text, encoding="utf-8")
        return True

    frontmatter = (
        "---\n"
        f'title: "{title}"\n'
        "aliases: []\n"
        f'category: "{category}"\n'
        "tags: []\n"
        "status: active\n"
        'created: "2026-06-24"\n'
        'updated: "2026-06-24"\n'
        "confidence: medium\n"
        "---\n\n"
    )
    path.write_text(frontmatter + text, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for path in ROOT.rglob("*.md"):
        if normalize(path):
            changed += 1
    print(f"Normalized frontmatter for {changed} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

