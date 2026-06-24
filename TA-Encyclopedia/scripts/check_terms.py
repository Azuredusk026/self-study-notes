from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".obsidian", "scripts"}

BANNED_PHRASES = [
    "非常重要",
    "不可替代",
    "广泛应用于各个领域",
    "先进的算法",
    "极大地提高",
    "显著提升了用户体验",
]

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)

def main() -> int:
    warnings = []

    for path in ROOT.rglob("*.md"):
        if is_excluded(path):
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")

        for phrase in BANNED_PHRASES:
            if phrase in text:
                warnings.append((path.relative_to(ROOT), phrase))

    if warnings:
        print("Potential vague phrases found:")
        for rel, phrase in warnings:
            print(f"- {rel}: {phrase}")
        return 1

    print("Term style check passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())