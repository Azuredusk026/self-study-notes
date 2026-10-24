"""Compile the current jump fragment and verify reviewed migration snapshots.

Run from the repository root with Python 3.11, Git and a C++17 compiler.
This verifies an isolated host; it does not run a game engine or an RL policy.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]


def heading_body(text, title):
    headings = list(re.finditer(r'^(#{1,6}) (.+)$', text, re.M))
    index = next(i for i, heading in enumerate(headings) if heading[2] == title)
    end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
    return text[headings[index].end():end].strip()


def verify_migration():
    manifest = json.loads((ROOT / 'skills/kb-structure-audit/references/navigation-split-2026-10-24.json').read_text(encoding='utf-8'))
    source = subprocess.check_output(['git', 'show', manifest['source_commit'] + ':' + manifest['source_path']], cwd=ROOT).decode('utf-8').replace('\r\n', '\n')
    original_headings = re.findall(r'^#{1,6} (.+)$', source, re.M)
    overview = (ROOT / manifest['source_path']).read_text(encoding='utf-8-sig')
    assert original_headings == re.findall(r'^#{1,6} (.+)$', overview, re.M), 'old heading entry drift'
    for record in manifest['records']:
        before = heading_body(source, record['source_heading'])
        after = heading_body((ROOT / record['target']).read_text(encoding='utf-8-sig'), record['target_heading'])
        assert hashlib.sha256(before.encode()).hexdigest() == record['source_body_sha256']
        assert hashlib.sha256(after.encode()).hexdigest() == record['reviewed_body_sha256'], record['target_heading']
    for name in manifest['new_pages']:
        text = (ROOT / '知识库/20_游戏AI' / (name + '.md')).read_text(encoding='utf-8-sig')
        assert len(re.findall(r'[\u4e00-\u9fff]', text)) <= 6000, name
    return {'reviewed_heading_bodies': len(manifest['records']), 'old_heading_entries': len(original_headings), 'new_pages': len(manifest['new_pages']),
            'scope': 'source and adopted body hashes plus old headings; semantic preservation was independently read'}


def verify_jump():
    article = (ROOT / '知识库/19_Gameplay与游戏框架/输入与动作状态.md').read_text(encoding='utf-8-sig')
    fragment = re.search(r'```cpp\n(bool TryJump.*?)\n```', article, re.S).group(1)
    compiler = os.environ.get('CXX') or shutil.which('clang++') or shutil.which('g++')
    if not compiler:
        candidate = Path('C:/Program Files/LLVM/bin/clang++.exe')
        if candidate.is_file():
            compiler = str(candidate)
    if not compiler:
        raise RuntimeError('Set CXX to a C++17 compiler; the fragment has not been compiled.')
    host = r'''
#include <cassert>
#include <optional>
#include <vector>
enum class Action { Jump };
constexpr float jumpBufferTime = .1f, coyoteTime = .1f;
struct Event { float time; bool consumed = false; };
struct InputBuffer {
    std::vector<Event> events;
    std::optional<size_t> FindPress(Action, float begin, float end) {
        std::optional<size_t> selected;
        for (size_t i = 0; i < events.size(); ++i) {
            const auto &event = events[i];
            if (!event.consumed && event.time >= begin && event.time <= end &&
                (!selected || event.time < events[*selected].time)) selected = i;
        }
        return selected;
    }
    void Consume(size_t id) { assert(!events.at(id).consumed); events[id].consumed = true; }
};
struct Character {
    bool hasGroundedHistory = true, jumpUsedSinceGrounded = false;
    float lastGroundedTime = 0;
    int starts = 0;
    void StartJump() { ++starts; }
};
'''
    checks = r'''
int main() {
    { Character c; c.lastGroundedTime = 2.f; InputBuffer b{{{1.98f}}};
      assert(TryJump(c,b,2.f)); assert(c.starts==1); } // current contact after long standing
    { Character c; c.hasGroundedHistory=false; InputBuffer b{{{.02f}}};
      assert(!TryJump(c,b,.05f)); assert(!b.events[0].consumed); } // air spawn
    { Character c; c.lastGroundedTime=.1f; InputBuffer b{{{.2f}}};
      assert(!TryJump(c,b,.1f)); } // future input
    { Character c; c.lastGroundedTime=.2f; InputBuffer b{{{.1f}}};
      assert(!TryJump(c,b,.1f)); } // future contact
    { Character c; InputBuffer b{{{.05f},{.07f}}};
      assert(TryJump(c,b,.05f)); assert(!TryJump(c,b,.07f)); assert(c.starts==1); } // permit consumed
    { Character c; c.lastGroundedTime=1.f; InputBuffer b{{{.8f}}};
      assert(!TryJump(c,b,1.f)); } // stale press
    { Character c; c.lastGroundedTime=.9f; InputBuffer b{{{1.f}}};
      assert(TryJump(c,b,1.f)); } // inclusive coyote boundary
    { Character c; c.lastGroundedTime=1.f; InputBuffer b{{{.95f},{1.05f}}};
      assert(TryJump(c,b,1.f)); assert(b.events[0].consumed && !b.events[1].consumed);
      c.jumpUsedSinceGrounded=false; c.lastGroundedTime=1.06f; // new landing
      assert(TryJump(c,b,1.06f)); assert(b.events[1].consumed && c.starts==2); }
}
'''
    version = subprocess.check_output([compiler, '--version'], text=True, encoding='utf-8', errors='replace').splitlines()[0]
    with tempfile.TemporaryDirectory(prefix='kb-jump-review-') as folder:
        source, binary = Path(folder) / 'jump.cpp', Path(folder) / 'jump.exe'
        source.write_text(host + fragment + checks, encoding='utf-8')
        compile_result = subprocess.run([compiler, '-std=c++17', str(source), '-o', str(binary)], capture_output=True, text=True, encoding='utf-8', errors='replace')
        if compile_result.returncode:
            raise RuntimeError(compile_result.stdout + compile_result.stderr)
        subprocess.run([str(binary)], check=True)
    return {'cases': 8, 'compiler': version, 'scope': 'current article fragment, isolated event buffer and character host; no engine contact generation'}


if __name__ == '__main__':
    result = {'passed': True, 'jump_fragment': verify_jump(), 'navigation_migration': verify_migration()}
    print(json.dumps(result, ensure_ascii=False, indent=2))
