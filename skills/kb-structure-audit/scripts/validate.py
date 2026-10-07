"""Validate structural invariants and registered assets without prose scoring."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote
from audit import inspect


def validate(root):
    root = root.resolve()
    kb = root / "知识库"
    pages = sorted(p for p in kb.glob("*/*.md") if p.parent.name not in ("assets", "examples"))
    keys = {p.relative_to(kb).as_posix()[:-3]: p for p in pages}
    errors = []
    facts = [inspect(p, root) for p in pages]
    for fact in facts:
        previous = 0
        for h in fact["headings"]:
            if previous and h["level"] > previous + 1:
                errors.append(f"标题跨级 {fact['path']}:{h['line']}")
            previous = h["level"]
        if fact["unclosed_fence"]:
            errors.append(f"围栏未闭合 {fact['path']}")
        for link in fact["wiki_links"]:
            key = link.split("#")[0].removeprefix("知识库/")
            if key not in keys:
                errors.append(f"双链缺失 {fact['path']} -> {link}")
    image_users = {}
    for p in [root / "README.md", root / "AGENTS.md", *pages, *(root / "skills").rglob("*.md")]:
        text = p.read_text(encoding="utf-8-sig")
        # Exclude examples in fences before validating prose links.
        text = re.sub(r"^```.*?^```\s*$", "", text, flags=re.M | re.S)
        for match in re.finditer(r"(!?)\[[^\]]*\]\(([^)]+)\)", text):
            image, raw = match.groups()
            raw = raw.strip("<>")
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", raw):
                continue
            raw = unquote(raw.split("#")[0])
            if not raw:
                continue
            target = (p.parent / raw).resolve()
            if not target.is_file():
                errors.append(f"本地链接缺失 {p.relative_to(root)} -> {raw}")
            if image:
                image_users.setdefault(target, []).append(p)
    registry_path = kb / "assets/registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registered = {}
    ids = set()
    for asset in registry["assets"]:
        key = asset["asset_id"]
        if key in ids:
            errors.append(f"资产ID重复 {key}")
        ids.add(key)
        target = (registry_path.parent / asset["local_path"]).resolve()
        registered[target] = asset
        if registry_path.parent.resolve() not in target.parents:
            errors.append(f"资产路径越界 {key}")
        if not target.is_file():
            errors.append(f"资产缺失 {key}")
        elif hashlib.sha256(target.read_bytes()).hexdigest() != asset["sha256"]:
            errors.append(f"资产哈希不一致 {key}")
        if not asset.get("caption") or not asset.get("license") or not asset.get("author"):
            errors.append(f"资产元数据不足 {key}")
        if target not in image_users:
            errors.append(f"资产未引用 {key}")
        for article in asset.get("article_usage", []):
            if article not in keys or keys[article] not in image_users.get(target, []):
                errors.append(f"资产使用登记不一致 {key} -> {article}")
    for target in image_users:
        if target not in registered:
            errors.append(f"图片未登记 {target}")
    formal = [p for p in pages if p.parent.name != "00_知识库说明"]
    readme = (root / "README.md").read_text(encoding="utf-8-sig")
    count = re.search(r"共 (\d+) 篇", readme)
    if not count or int(count.group(1)) != len(formal):
        errors.append("README计数不一致")
    knowledge_map = (kb / "00_知识库说明/知识地图.md").read_text(encoding="utf-8-sig")
    for p in formal:
        key = p.relative_to(kb).as_posix()[:-3]
        if key not in knowledge_map:
            errors.append(f"地图漏收 {key}")
    return {"formal_articles": len(formal), "support_pages": len(pages)-len(formal),
            "registered_images": len(registered), "errors": errors,
            "writing_candidates": sum(len(r["writing_candidates"]) for r in facts),
            "scope": "静态不变量；写作质量和技术断言需原文复读及证据核验"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    result = validate(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result["errors"]))
