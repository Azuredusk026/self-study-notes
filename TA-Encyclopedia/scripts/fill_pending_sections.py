from pathlib import Path
import re

from expand_core_sections import (
    ROOT,
    SOURCE_TEXT,
    ensure_definition,
    ensure_tail_sections,
    ensure_why,
    infer_title,
    profile_for,
    section_block,
    update_frontmatter,
)

PENDING = "待" + "补充"


def replace_pending_heading(text: str, title: str, profile: dict) -> str:
    pattern = re.compile(rf"^## {PENDING}\s*\n(?P<body>.*?)(?=^## |\Z)", re.S | re.M)
    return pattern.sub(section_block(title, profile).rstrip() + "\n\n", text)


def normalize_sources(text: str) -> str:
    text = text.replace(f"- {PENDING}到 [[91_Sources/source_registry|Source Registry]]", SOURCE_TEXT)
    text = re.sub(rf"^- {PENDING}\s*$", SOURCE_TEXT, text, flags=re.MULTILINE)
    return text


def normalize_source_registry(text: str) -> str:
    return text.replace(f"| {PENDING} |", "| 待核验：官方来源待登记 |")


def main() -> int:
    changed = 0
    for path in ROOT.rglob("*"):
        if path.is_dir() or path.suffix != ".md":
            continue
        if any(part in {".git", ".obsidian", "scripts"} for part in path.parts):
            continue

        text = path.read_text(encoding="utf-8")
        new = text

        if path.name == "source_registry.md":
            new = normalize_source_registry(new)

        if PENDING in new:
            title = infer_title(path, new)
            profile = profile_for(path)
            new = ensure_definition(new, title, profile)
            new = ensure_why(new, title, profile)
            new = replace_pending_heading(new, title, profile)
            new = normalize_sources(new)
            new = ensure_tail_sections(new, path)
            new = update_frontmatter(new)

        if new != text:
            path.write_text(new.rstrip() + "\n", encoding="utf-8")
            changed += 1

    print(f"Filled pending markers in {changed} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
