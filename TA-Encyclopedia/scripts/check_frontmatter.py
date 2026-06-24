from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".obsidian", "scripts"}

REQUIRED_KEYS = ["title:", "category:", "tags:", "status:", "created:", "updated:", "confidence:"]

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)

def has_frontmatter(text: str) -> bool:
    return text.startswith("---\n") and "\n---\n" in text[4:]

def main() -> int:
    failed = []

    for path in ROOT.rglob("*.md"):
        if is_excluded(path):
            continue

        rel = path.relative_to(ROOT)

        if str(rel).startswith("90_Templates") or str(rel).startswith("92_Codex"):
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")

        if not has_frontmatter(text):
            failed.append((rel, "missing frontmatter"))
            continue

        header = text.split("\n---\n", 1)[0]

        for key in REQUIRED_KEYS:
            if key not in header:
                failed.append((rel, f"missing key: {key}"))

    if failed:
        print("Frontmatter check failed:")
        for rel, reason in failed:
            print(f"- {rel}: {reason}")
        return 1

    print("Frontmatter check passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())