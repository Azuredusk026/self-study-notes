"""Regression guards for stale or incomplete editorial acceptance records."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from revision_validate import validate_rows


class RevisionRecords(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.path = self.root / '知识库/01_数学/采样.md'
        self.path.parent.mkdir(parents=True)
        self.path.write_text('# 采样\n\n正文。\n', encoding='utf-8')
        sha = hashlib.sha256(self.path.read_text(encoding='utf-8').encode()).hexdigest()
        self.row = {'path': '知识库/01_数学/采样.md', 'final_sha256': sha,
                    'quality_matrix': {k: {'status': '通过', 'basis': '本页实际复读依据'} for k in
                    ('Scope', 'Structure', 'Depth', 'Implementation', 'Evidence', 'Writing Style',
                     'Title', 'Information Architecture', 'Visuals')},
                    'revision_review': {'status': 'REVIEWED', 'independent_review': 'PASS',
                                        'content_sha256': sha}}

    def tearDown(self):
        self.temp.cleanup()

    def test_accepted_snapshot_and_line_endings(self):
        self.assertEqual(validate_rows(self.root, [self.row]), [])
        self.path.write_bytes(self.path.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
        self.assertEqual(validate_rows(self.root, [self.row]), [])

    def test_rejects_unreviewed_content_and_unsupported_pass(self):
        cases = [
            ('正文漂移', lambda r: self.path.write_text('# 采样\n\n另一份正文。\n', encoding='utf-8')),
            ('复读未完成', lambda r: r['revision_review'].update(status='PENDING')),
            ('独立复核未完成', lambda r: r['revision_review'].pop('independent_review')),
            ('维度依据缺失', lambda r: r['quality_matrix']['Evidence'].update(basis='')),
            ('维度未通过', lambda r: r['quality_matrix']['Depth'].update(status='待复读')),
            ('复读哈希不一致', lambda r: r['revision_review'].update(content_sha256='old')),
        ]
        original = self.path.read_bytes()
        for name, mutate in cases:
            with self.subTest(name=name):
                row = copy.deepcopy(self.row)
                mutate(row)
                self.assertTrue(validate_rows(self.root, [row]), name)
                self.path.write_bytes(original)


if __name__ == '__main__':
    unittest.main()
