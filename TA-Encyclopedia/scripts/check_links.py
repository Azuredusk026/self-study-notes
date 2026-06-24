import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".obsidian", "scripts"}

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)

def normalize_link(link: str) -> str:
    link = link.split("|", 1)[0]
    link = link.split("#", 1)[0]
    return link.strip()

def build_note_names() -> set[str]:
    names = set()

    for path in ROOT.rglob("*.md"):
        if is_excluded(path):
            continue

        names.add(path.stem)
        rel_no_suffix = str(path.relative_to(ROOT).with_suffix(""))
        names.add(rel_no_suffix.replace("\\", "/"))

    return names

def main() -> int:
    note_names = build_note_names()
    broken = []

    for path in ROOT.rglob("*.md"):
        if is_excluded(path):
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")

        for match in WIKILINK_RE.findall(text):
            target = normalize_link(match)
            if not target:
                continue

            if target not in note_names:
                broken.append((path.relative_to(ROOT), target))

    if broken:
        print("Broken wikilinks:")
        for rel, target in broken:
            print(f"- {rel}: [[{target}]]")
        return 1

    print("Wikilink check passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())