"""Exercise the published Bash check against an isolated Git index."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
ARTICLE = ROOT / '知识库/15_资产与工具管线/资产构建CI.md'
POINTER = ('version https://git-lfs.github.com/spec/v1\n'
           'oid sha256:' + '0' * 64 + '\nsize 7\n')


class StagedAssetCheck(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kb-ci-excerpt-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        git = shutil.which('git')
        if not git:
            raise RuntimeError('git is required')
        self.bash = os.environ.get('KB_BASH_PATH')
        if not self.bash and os.name == 'nt':
            self.bash = str(Path(git).resolve().parents[1] / 'bin/bash.exe')
        if not self.bash:
            self.bash = shutil.which('bash')
        if not self.bash or not Path(self.bash).is_file():
            raise RuntimeError('set KB_BASH_PATH to a Bash executable')
        self.git('init', '--quiet')
        self.git('config', 'core.quotePath', 'true')
        self.git('config', 'core.autocrlf', 'false')
        self.script = re.search(r'```bash\n(.*?)\n```', ARTICLE.read_text(encoding='utf-8'), re.S).group(1)

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True,
                              capture_output=True)

    def stage(self, name, content):
        path = self.root / name
        path.write_text(content, encoding='utf-8')
        self.git('add', '--', name)
        return path

    def check(self):
        return subprocess.run([self.bash, '-c', self.script], cwd=self.root,
                              capture_output=True).returncode

    def test_chinese_and_spaces_keep_exact_path(self):
        self.stage('角色 模型.fbx', POINTER)
        self.assertEqual(self.check(), 0)

    def test_raw_binary_rejected(self):
        self.stage('raw.fbx', 'not an LFS pointer\n')
        self.assertNotEqual(self.check(), 0)

    def test_chinese_raw_binary_rejected(self):
        self.stage('角色 模型.fbx', 'not an LFS pointer\n')
        self.assertNotEqual(self.check(), 0)

    def test_unstaged_edits_do_not_replace_index(self):
        path = self.stage('staged.fbx', POINTER)
        path.write_text('worktree edit\n', encoding='utf-8')
        self.assertEqual(self.check(), 0)

    def test_valid_worktree_does_not_hide_bad_index(self):
        path = self.stage('staged.fbx', 'raw asset\n')
        path.write_text(POINTER, encoding='utf-8')
        self.assertNotEqual(self.check(), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
