"""Run the CPU checks and compile the two canonical HLSL article fragments."""
import json
import platform
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
KB = HERE.parents[1]
BUILD = HERE / 'build'


def verify():
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern='test_reference.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    dxc = shutil.which('dxc')
    if not dxc:
        raise SystemExit('DXC is required for the compilation checks; CPU tests passed.')
    BUILD.mkdir(exist_ok=True)
    specs = [
        ('文字渲染', 'GlyphPS', 'ps_6_0',
         'Texture2D<float> GlyphAtlas; SamplerState LinearClamp; float SdfSoftness;\n',
         '\nfloat4 GlyphPS(float4 p:SV_Position):SV_Target{return GlyphAlpha(p.xy*.01).xxxx;}'),
        ('Unreal RDG Pass实现', 'MainCS', 'cs_6_0', '', ''),
    ]
    probes = []
    for title, entry, profile, prefix, suffix in specs:
        page = next(KB.glob('*/' + title + '.md'))
        block = re.findall(r'```hlsl\n(.*?)\n```', page.read_text(encoding='utf-8'), re.S)[0]
        source = BUILD / (entry + '.hlsl')
        source.write_text(prefix + block + suffix, encoding='utf-8')
        subprocess.run([dxc, '-T', profile, '-E', entry, str(source),
                        '-Fo', str(BUILD / (entry + '.dxil'))], check=True)
        probes.append({'entry': entry, 'profile': profile, 'passed': True,
                       'scope': 'HLSL compilation only'})
    report = {'record_date': '2026-10-22', 'python': platform.python_version(),
              'cpu_tests': result.testsRun, 'cpu_passed': True, 'probes': probes,
              'dxc_version': subprocess.check_output([dxc, '--version'], text=True).strip(),
              'engine_compile': 'UNVERIFIED', 'engine_runtime': 'UNVERIFIED',
              'gpu_capture': 'UNVERIFIED', 'performance': 'UNVERIFIED'}
    (HERE / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))


if __name__ == '__main__':
    verify()
