from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".obsidian", "scripts"}
CONTROL_PATHS = ("90_Templates", "92_Codex", "AGENTS.md", "README.md")

BANNED_PHRASES = [
    "非常重要",
    "不可替代",
    "广泛应用于各个领域",
    "先进的算法",
    "极大地提高",
    "显著提升了用户体验",
]

INTERVIEW_HEADING = "## " + "面" + "试可能怎么问"
WHY_HEADING = "## " + "为什么" + "需要它"
TYPICAL_USES_HEADING = "## " + "技术美术中的典型" + "用途"
UNITY_SCENE_HEADING = "## Unity 中的" + "相关场景"
UNREAL_SCENE_HEADING = "## Unreal Engine 中的" + "相关场景"
PRACTICE_HEADING = "## " + "实践" + "建议"

LEGACY_ENTRY_HEADINGS = [
    "## 一句话定义",
    WHY_HEADING,
    TYPICAL_USES_HEADING,
    UNITY_SCENE_HEADING,
    UNREAL_SCENE_HEADING,
    INTERVIEW_HEADING,
    PRACTICE_HEADING,
]

FIXED_CORE_FIELD_RE = re.compile(r"^\s*-\s*(输入|处理过程|输出|所在层级|关键约束|常见实现差异)：", re.MULTILINE)

LOW_VALUE_RELATED = {
    "技术美术百科总目录",
    "术语索引",
    "待扩充条目",
}

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)

def is_control_file(rel: Path) -> bool:
    rel_text = rel.as_posix()
    return rel_text.startswith(CONTROL_PATHS) or rel_text in CONTROL_PATHS

def section_body(text: str, heading: str) -> str | None:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*\n(?P<body>.*?)(?=^## |\Z)", re.S | re.M)
    match = pattern.search(text)
    return match.group("body").strip() if match else None

def normalize_link(link: str) -> str:
    return link.split("|", 1)[0].split("#", 1)[0].strip()

def check_related_entries(rel: Path, text: str, failures: list[tuple[Path, str]]) -> None:
    if "## 定义与解释" not in text:
        return

    body = section_body(text, "相关条目")
    if body is None:
        failures.append((rel, "missing related entries section"))
        return

    item_lines = [line.strip() for line in body.splitlines() if line.strip().startswith("- ")]
    linked_items = []
    for line in item_lines:
        links = [normalize_link(link) for link in WIKILINK_RE.findall(line)]
        if not links:
            failures.append((rel, f"related entry item has no wikilink: {line}"))
            continue
        for link in links:
            if not link:
                failures.append((rel, "related entry contains empty wikilink"))
            if link in LOW_VALUE_RELATED or link.endswith("/README"):
                failures.append((rel, f"low-value related entry: [[{link}]]"))
        if "：" not in line and ":" not in line:
            failures.append((rel, f"related entry lacks relationship note: {line}"))
        linked_items.extend(links)

    if len(set(linked_items)) < 2:
        failures.append((rel, "related entries need at least two distinct linked concepts"))

def main() -> int:
    warnings = []
    failures = []

    for path in ROOT.rglob("*.md"):
        if is_excluded(path):
            continue

        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8", errors="ignore")

        for phrase in BANNED_PHRASES:
            if phrase in text:
                warnings.append((rel, phrase))

        if is_control_file(rel):
            for heading in LEGACY_ENTRY_HEADINGS:
                if heading in text:
                    failures.append((rel, f"legacy entry heading requirement: {heading}"))
            if FIXED_CORE_FIELD_RE.search(text):
                failures.append((rel, "core principle uses fixed field checklist"))

        check_related_entries(rel, text, failures)

    if warnings or failures:
        if failures:
            print("Term structure check failed:")
            for rel, reason in failures:
                print(f"- {rel}: {reason}")
        print("Potential vague phrases found:")
        for rel, phrase in warnings:
            print(f"- {rel}: {phrase}")
        return 1

    print("Term style check passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
