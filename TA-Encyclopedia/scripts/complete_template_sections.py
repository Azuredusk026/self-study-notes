from pathlib import Path
import re

from expand_core_sections import (
    ROOT,
    ensure_definition,
    ensure_tail_sections,
    ensure_why,
    infer_title,
    profile_for,
    section_block,
    update_frontmatter,
)

TECH_DIRS = {
    "01_Rendering",
    "02_Shader",
    "03_Tools_Pipeline",
    "04_Engine",
    "05_Art_Production",
    "06_AIGC_TA",
    "07_Math_CS",
}

STANDARD_SECTIONS = [
    "核心原理",
    "用途",
    "与其他概念的区别",
    "常见误区",
]


def has_heading(text: str, heading: str) -> bool:
    return re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE) is not None


def generated_sections(title: str, profile: dict) -> dict[str, str]:
    block = section_block(title, profile).strip()
    parts = re.split(r"^## (.+?)\s*$", block, flags=re.MULTILINE)
    sections = {}
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1].strip()
        sections[heading] = f"## {heading}\n\n{body}".rstrip()
    return sections


def insert_before_tail(text: str, blocks: list[str]) -> str:
    if not blocks:
        return text
    tail = re.search(r"^## (相关条目|参考来源)\s*$", text, flags=re.MULTILINE)
    insert = "\n\n".join(blocks).rstrip()
    if not tail:
        return text.rstrip() + "\n\n" + insert + "\n"
    insert_at = tail.start()
    return text[:insert_at].rstrip() + "\n\n" + insert + "\n\n" + text[insert_at:].lstrip("\n")


def main() -> int:
    changed = 0
    checked = 0
    for folder_name in sorted(TECH_DIRS):
        folder = ROOT / folder_name
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.md")):
            if path.name == "README.md":
                continue
            checked += 1
            text = path.read_text(encoding="utf-8")
            title = infer_title(path, text)
            profile = profile_for(path)
            new = ensure_definition(text, title, profile)
            new = ensure_why(new, title, profile)

            sections = generated_sections(title, profile)
            missing_blocks = [
                sections[heading]
                for heading in STANDARD_SECTIONS
                if not has_heading(new, heading)
            ]
            new = insert_before_tail(new, missing_blocks)
            new = ensure_tail_sections(new, path)
            new = update_frontmatter(new)

            if new != text:
                path.write_text(new.rstrip() + "\n", encoding="utf-8")
                changed += 1

    print(f"Completed template sections in {changed} files.")
    print(f"Technical entries checked: {checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
