"""Check frozen migration, references, and per-page execution coverage."""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote
from validate import validate


def prose(text):
    return re.sub(r'^(`{3,}|~{3,}).*?^\1\s*$', '', text, flags=re.M | re.S)


def anchors(text):
    titles = re.findall(r'^#{1,6}\s+(.+?)\s*#*$', prose(text), re.M)
    result = set(titles)
    counts = Counter()
    for title in titles:
        plain = re.sub(r'[`*_]', '', title).lower()
        plain = re.sub(r'[^\w\s\-\u0080-\uffff]', '', plain).replace(' ', '-')
        suffix = '' if counts[plain] == 0 else '-' + str(counts[plain])
        counts[plain] += 1
        result.add(plain + suffix)
    result.update(re.findall(r'^.*\s\^([\w-]+)\s*$', prose(text), re.M))
    return result


def batch_validate(root):
    root = root.resolve()
    result = validate(root)
    errors = result['errors']
    audit = root / 'skills/kb-structure-audit'
    def read(name):
        return json.loads((audit / name).read_text(encoding='utf-8'))
    frozen = read('final-path-map.json')['records']
    matrix = read('article-quality-matrix.json')
    reviews = read('title-review.json')['records']
    journal = read('batch-review.json')['batches']
    expected = {r['final_path'] for r in frozen}
    paths = [r['final_path'] for r in frozen]
    if len(paths) != 113 or len({p.casefold() for p in paths}) != 113:
        errors.append('冻结表数量或大小写唯一性错误')
    if {r['path'] for r in reviews} != expected:
        errors.append('全库标题审查覆盖不一致')
    seen = Counter()
    for batch in journal:
        if not 15 <= batch['pages'] <= 25 or batch['pages'] != len(batch['articles']):
            errors.append('批次规模不一致 ' + batch['id'])
        if '0 error' not in batch.get('static_validation', ''):
            errors.append('批次缺少静态验收 ' + batch['id'])
        for record in batch['articles']:
            seen[record['path']] += 1
            if not record['actions'] or not record.get('review_scope'):
                errors.append('逐页动作缺失 ' + record['path'])
    if set(seen) != expected or any(v != 1 for v in seen.values()):
        errors.append('正文批次覆盖缺失或重复')
    page_text = {}
    for entry in frozen:
        path = root / entry['final_path']
        text = path.read_text(encoding='utf-8-sig')
        page_text[path.resolve()] = text
        h1 = re.findall(r'^# (.+)$', prose(text), re.M)
        if h1 != [entry['final_h1']]:
            errors.append('冻结H1不一致 ' + entry['final_path'])
        if path.parent.name != entry['final_category'] or path.name != entry['final_filename']:
            errors.append('冻结路径字段不一致 ' + entry['final_path'])
        row = next(r for r in matrix if r['path'] == entry['final_path'])
        if not row.get('modernization_batch') or not row.get('executed_content_actions'):
            errors.append('正文状态缺失 ' + entry['final_path'])
        if row.get('final_sha256') != hashlib.sha256(text.encode()).hexdigest():
            errors.append('最终正文哈希不一致 ' + entry['final_path'])
        if row['title_review'] is None or row['category_review'] is None:
            errors.append('审查未完成 ' + entry['final_path'])
        if entry['deferred_title'] != row['deferred_title'] or entry['pending_split'] != row['pending_split']:
            errors.append('延后状态丢失 ' + entry['final_path'])
        if entry['deferred_title'] and row['title_review'] not in ('SPLIT', 'OVERVIEW'):
            errors.append('延后边界被标为通过 ' + entry['final_path'])
        if path.parent.name != '00_知识库说明':
            for required in ('相关主题', '参考资料'):
                if required not in re.findall(r'^## (.+)$', prose(text), re.M):
                    errors.append('专题必要章节缺失 ' + entry['final_path'] + ' ' + required)
        for language, body in re.findall(r'^```([^\n]*)\n(.*?)^```\s*$', text, re.M | re.S):
            if not language.strip():
                errors.append('代码围栏语言缺失 ' + entry['final_path'])
            if re.search(r'\.\./\d{2}_[^\n]*/(?:Location|Bytes|DecodedAsset|GpuAsset)', body):
                errors.append('代码类型混入历史目录 ' + entry['final_path'])
    keys = {p.relative_to(root/'知识库').as_posix()[:-3]: p for p in page_text}
    backlinks = defaultdict(set)
    all_docs = [root/'README.md', root/'AGENTS.md', *page_text, *(root/'skills').rglob('*.md')]
    wiki_count = markdown_count = anchor_count = 0
    for path in all_docs:
        text = prose(path.read_text(encoding='utf-8-sig'))
        for raw in re.findall(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', text):
            base, separator, anchor = raw.partition('#')
            base = base.removeprefix('知识库/').removesuffix('.md')
            target = path.resolve() if not base else keys.get(base)
            wiki_count += 1
            if target not in page_text:
                errors.append('工作入口双链缺失 ' + str(path.relative_to(root)) + ' -> ' + raw)
                continue
            backlinks[target].add(path)
            if separator:
                anchor_count += 1
                if anchor.removeprefix('^') not in anchors(page_text[target]):
                    errors.append('双链锚点缺失 ' + raw)
        for raw in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', text):
            raw = raw.strip('<>')
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', raw):
                continue
            base, separator, anchor = unquote(raw).partition('#')
            target = (path.parent / base).resolve() if base else path.resolve()
            markdown_count += 1
            if not target.is_file():
                errors.append('本地引用缺失 ' + str(path.relative_to(root)) + ' -> ' + raw)
            elif separator and target.suffix == '.md':
                anchor_count += 1
                if anchor not in anchors(target.read_text(encoding='utf-8-sig')):
                    errors.append('Markdown锚点缺失 ' + raw)
    orphans = [str(p.relative_to(root)) for p in page_text if not backlinks[p]]
    if orphans:
        errors.append('无入口页面 ' + ', '.join(orphans))
    glossary = root/'知识库/00_知识库说明/术语表.md'
    terms = re.findall(r'^\| ([^|]+) \|', glossary.read_text(encoding='utf-8'), re.M)
    duplicates = [term for term, count in Counter(terms).items() if count > 1]
    if duplicates:
        errors.append('术语重复 ' + ', '.join(duplicates))
    sections = read('current-section-map.json')['sections']
    historical_count = len(sections)
    for entry in sections:
        target = keys.get(entry['target'])
        if not target:
            errors.append('历史映射目标缺失 ' + entry['target'])
        elif entry['current_heading'] not in anchors(page_text[target]):
            errors.append('历史章节标题缺失 ' + entry['target'] + '#' + entry['historical_heading'])
    result.update(frozen_pages=len(frozen), reviewed_pages=len(seen),
                  batches=[{'id': b['id'], 'pages': b['pages']} for b in journal],
                  title_statuses=dict(Counter(r['title_review'] for r in matrix)),
                  deferred_titles=sum(r['deferred_title'] for r in matrix),
                  pending_splits=sum(r['pending_split'] for r in matrix),
                  wiki_references=wiki_count, local_markdown_references=markdown_count,
                  checked_anchors=anchor_count, orphan_pages=orphans,
                  historical_sections=historical_count,
                  article_hashes={str(p.relative_to(root)): hashlib.sha256(t.encode()).hexdigest()
                                  for p, t in page_text.items()})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = batch_validate(args.root)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    compact = {k: v for k, v in result.items() if k != 'article_hashes'}
    print(json.dumps(compact, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['errors']))
