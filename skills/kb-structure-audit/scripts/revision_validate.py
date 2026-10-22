"""Check acceptance record integrity; prose and factual quality require reading."""
import argparse
import hashlib
import json
from pathlib import Path

DIMENSIONS = ('Scope', 'Structure', 'Depth', 'Implementation', 'Evidence',
              'Writing Style', 'Title', 'Information Architecture', 'Visuals')


def validate_rows(root, rows):
    errors = []
    for row in rows:
        path = row['path']
        file = root / path
        if not file.is_file():
            errors.append('正文缺失 ' + path)
            continue
        actual = hashlib.sha256(file.read_text(encoding='utf-8-sig').encode()).hexdigest()
        review = row.get('revision_review', {})
        if row.get('final_sha256') != actual:
            errors.append('正文漂移 ' + path)
        if review.get('status') != 'REVIEWED':
            errors.append('复读未完成 ' + path)
        if review.get('independent_review') != 'PASS':
            errors.append('独立复核未完成 ' + path)
        if review.get('content_sha256') != actual:
            errors.append('复读哈希不一致 ' + path)
        for key in DIMENSIONS:
            dimension = row.get('quality_matrix', {}).get(key, {})
            if not isinstance(dimension, dict):
                errors.append('维度记录缺失 ' + path + ' ' + key)
                continue
            if dimension.get('status') not in ('通过', '不适用'):
                errors.append('维度未通过 ' + path + ' ' + key)
            if not str(dimension.get('basis', '')).strip():
                errors.append('维度依据缺失 ' + path + ' ' + key)
    return errors


def validate(root):
    root = root.resolve()
    rows = json.loads((root / 'skills/kb-structure-audit/article-quality-matrix.json').read_text(encoding='utf-8'))
    errors = validate_rows(root, rows)
    actual = {p.relative_to(root).as_posix() for p in (root / '知识库').glob('*/*.md')
              if p.parent.name not in ('assets', 'examples')}
    recorded = [r['path'] for r in rows]
    if actual != set(recorded) or len(recorded) != len(set(recorded)):
        errors.append('正文与复读登记覆盖不一致')
    return {'passed': not errors, 'pages': len(rows), 'dimensions': len(rows) * len(DIMENSIONS),
            'errors': errors,
            'scope': '复读登记完整性和当前正文快照；不替代全文判断、来源核读或目标环境实验'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    result = validate(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
