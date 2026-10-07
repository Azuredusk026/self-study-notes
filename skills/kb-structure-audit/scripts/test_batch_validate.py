"""Mutation checks for migration invariants, using an isolated fixture."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path
from batch_validate import batch_validate


def verify(root):
    root = root.resolve()
    fixture_parent = Path(tempfile.mkdtemp(prefix='kb-batch-check-')).resolve()
    fixture = fixture_parent / 'fixture'
    fixture.mkdir()
    for folder in ('知识库', 'skills'):
        shutil.copytree(root / folder, fixture / folder,
                        ignore=shutil.ignore_patterns('build', '__pycache__', 'node_modules'))
    for name in ('README.md', 'AGENTS.md'):
        shutil.copy2(root / name, fixture / name)
    cases = []

    def mutate(name, relative_path, transform, expected):
        path = fixture / relative_path
        saved = path.read_bytes()
        try:
            path.write_text(transform(path.read_text(encoding='utf-8')), encoding='utf-8')
            errors = batch_validate(fixture)['errors']
            assert any(expected in error for error in errors), (name, errors)
            cases.append(name)
        finally:
            path.write_bytes(saved)

    try:
        assert not batch_validate(fixture)['errors']
        article = '知识库/13_渲染架构/Render Graph.md'
        mutate('H1与冻结表', article, lambda s: s.replace('# Render Graph', '# Bad', 1), '冻结H1')
        mutate('失效双链', article, lambda s: s + '\n[[13_渲染架构/缺失页面]]\n', '双链缺失')
        mutate('失效Wiki锚点', article, lambda s: s + '\n[[13_渲染架构/Render Graph#缺失章节]]\n', '双链锚点缺失')
        mutate('失效Markdown锚点', article, lambda s: s + '\n[x](Render%20Graph.md#missing-section)\n', 'Markdown锚点缺失')
        mutate('围栏内目录污染', article,
               lambda s: s + '\n```cpp\n[](../13_旧目录/Bytes b)\n```\n', '代码类型混入历史目录')
        mutate('最终哈希漂移', article, lambda s: s + '\n未登记修改。\n', '最终正文哈希')
        def drop_batch(text):
            obj = json.loads(text)
            if 'completion' in obj:
                obj['completion']['articles'].pop()
            else:
                obj['batches'][0]['articles'].pop()
            return json.dumps(obj, ensure_ascii=False)
        mutate('正文批次遗漏', 'skills/kb-structure-audit/batch-review.json', drop_batch, '正文批次覆盖')
        def title_unreviewed(text):
            obj = json.loads(text)
            obj[0]['title_review'] = None
            return json.dumps(obj, ensure_ascii=False)
        mutate('未审查标题', 'skills/kb-structure-audit/article-quality-matrix.json', title_unreviewed, '审查未完成')
        def pending_split(text):
            obj = json.loads(text)
            obj[0]['pending_split'] = True
            return json.dumps(obj, ensure_ascii=False)
        mutate('最终待拆状态', 'skills/kb-structure-audit/article-quality-matrix.json', pending_split, '最终迁移状态未完成')
        mutate('空H2章节', article, lambda s: s + '\n## 空章节\n\n## 下一节\n\n有内容。\n', '空标题章节')
        def wrong_question(text):
            obj = json.loads(text)
            obj['records'][0]['primary_question'] = '错误主问题'
            return json.dumps(obj, ensure_ascii=False)
        mutate('主问题登记漂移', 'skills/kb-structure-audit/title-review.json', wrong_question, '主要问题登记不一致')
        return {'passed': True, 'checks': len(cases), 'cases': cases,
                'scope': 'isolated malformed-fixture detection; no prose quality scoring'}
    finally:
        assert fixture_parent.parent == Path(tempfile.gettempdir()).resolve()
        assert fixture.parent == fixture_parent
        shutil.rmtree(fixture_parent)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = verify(args.root)
    if args.out:
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
