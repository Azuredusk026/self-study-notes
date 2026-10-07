"""Read-only structural facts and prose candidates; editorial decisions stay separate."""
import argparse
import json
import re
from pathlib import Path


def inspect(path, root):
    text = path.read_text(encoding="utf-8-sig")
    fence = None
    size = 0
    headings, prose, candidates, codes = [], [], [], []
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence, size = marker[0], len(marker)
                codes.append({"line": number, "language": match.group(2).strip()})
            elif marker[0] == fence and len(marker) >= size and not match.group(2).strip():
                fence = None
            continue
        if fence:
            continue
        prose.append(line)
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            headings.append({"line": number, "level": len(heading.group(1)), "title": heading.group(2)})
        if re.search(r"本文(?:将|主要)|在现代.*中|综上所述|我们可以看到|需要注意的是|为了更好地理解", line):
            candidates.append({"line": number, "text": line, "reason": "复读主语、信息量与过渡用途"})
    body = "\n".join(prose)
    titles = [heading["title"] for heading in headings if heading["level"] == 1]
    title = titles[0] if titles else None
    title_candidates = []
    if title and len(re.split(r"、|与", title)) >= 3:
        title_candidates.append("并列结构需复读主问题与独立机制；不是自动拆分结论")
    return {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size,
            "current_title": title, "title_review": None, "title_review_status": "待审查",
            "title_candidates": title_candidates,
            "headings": headings, "code_blocks": codes, "unclosed_fence": fence is not None,
            "wiki_links": re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", body),
            "images": re.findall(r"!\[[^\]]*\]\(([^)]+)\)|!\[\[([^\]]+)\]\]", body),
            "writing_candidates": candidates, "writing_review": "待复读",
            "boundary_action": None, "content_actions": [],
            "quality_matrix": {key: "待复读" for key in
                               ("Scope", "Structure", "Depth", "Implementation", "Evidence", "Writing Style", "Title", "Visuals")}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    paths = sorted(p for p in (root / "知识库").glob("*/*.md") if p.parent.name != "assets")
    rows = [inspect(p, root) for p in paths]
    output = json.dumps(rows, ensure_ascii=False, indent=2)
    if args.out:
        target = args.out.resolve()
        if target == root or root in target.parents:
            raise SystemExit("只读扫描输出应保存在仓库外")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output, encoding="utf-8")
        print(json.dumps({"pages": len(rows), "writing_candidates": sum(len(r["writing_candidates"]) for r in rows)}, ensure_ascii=False))
    else:
        print(output)


if __name__ == "__main__":
    main()
