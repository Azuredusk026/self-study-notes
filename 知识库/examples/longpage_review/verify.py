"""Verify reviewed long-article destinations against the fixed source revision.

Run from the repository root: python -B 知识库/examples/longpage_review/verify.py
Hashes establish the reviewed snapshot; semantic completeness requires the
independent reading recorded in each manifest, not a hash comparison alone.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[3]


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def headings(text):
    fence = None
    result = []
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            if fence is None:
                fence = marker[1][0]
            elif marker[1][0] == fence:
                fence = None
        if fence is None:
            match = re.match(r'^(#{1,6}) (.+?)\s*$', line)
            if match:
                result.append((match[2], []))
                continue
        if result:
            result[-1][1].append(line)
    return {title: ''.join(lines).strip() for title, lines in result}


def verify():
    groups = []
    for path in sorted((ROOT / 'skills/kb-structure-audit/references').glob('longpage-*-2026-10-24.json')):
        data = json.loads(path.read_text(encoding='utf-8'))
        source = subprocess.check_output(['git', 'show', data['source_commit'] + ':' + data['source_path']], cwd=ROOT).decode('utf-8').replace('\r\n', '\n')
        before = headings(source)
        current_text = (ROOT / data['source_path']).read_text(encoding='utf-8-sig')
        current = headings(current_text)
        assert sha(current_text) == data['adopted_source_sha256'], (path.name, 'retained article drift')
        assert set(before) <= set(current), (path.name, 'old heading entry lost', set(before)-set(current))
        assert data.get('independent_review'), (path.name, 'independent reading missing')
        mapped = {m['source_heading'] for m in data['mappings']}
        meta = {'验证方法', '验证路径', '实现与证据', '相关主题', '参考资料'}
        assert set(before) - mapped - meta - {Path(data['source_path']).stem} == set(), (path.name, 'source heading not assigned')
        for m in data['mappings']:
            assert sha(before[m['source_heading']]) == m['source_body_sha256'], (path.name, 'source drift', m['source_heading'])
            adopted = headings((ROOT / m['target_path']).read_text(encoding='utf-8-sig'))[m['target_heading']]
            assert sha(adopted) == m['reviewed_body_sha256'], (path.name, 'adopted body drift', m['target_heading'])
        for article in data['articles']:
            text = (ROOT / article['path']).read_text(encoding='utf-8-sig')
            assert sha(text) == article['reviewed_sha256'], article['path']
            assert len(re.findall(r'[\u4e00-\u9fff]', text)) <= 6000, (article['path'], 'review reading budget exceeded')
        groups.append({'source': data['source_path'], 'heading_destinations': len(data['mappings']), 'new_articles': len(data['articles'])})
    return {'passed': True, 'groups': groups, 'scope': 'fixed source, reviewed adopted bodies, old heading entries, independent reading records and article reading budget; no engine/model/service runtime claim'}


def compile_aa():
    """Compile adopted HLSL in an explicit isolated host, without GPU execution."""
    base = ROOT / '知识库/02_GPU与光栅化管线'
    def block(name, marker):
        text = (base / (name + '.md')).read_text(encoding='utf-8-sig')
        return next(code for code in re.findall(r'```hlsl\n(.*?)\n```', text, re.S) if marker in code)
    cases = {
        'resolve': block('抗锯齿与时域重建', 'Resolve4x') + '\nfloat4 Main(float4 p:SV_Position):SV_Target { return Resolve4x(uint2(p.xy)); }',
        'jitter': 'cbuffer C { float2 jitterNdc; };\nfloat4 Main(float4 positionCS:POSITION):SV_Position {\n' + block('时域采样与重投影', 'positionCS.xy') + '\nreturn positionCS; }',
        'nearest': 'Texture2D<float> Depth; SamplerState PointClamp; cbuffer C { float4 _CameraDepthTexture_TexelSize; };\nfloat SampleDepth(float2 uv) { return Depth.SampleLevel(PointClamp,uv,0); }\nfloat CompareDepth(float a,float b) { return a<b?1.0:0.0; }\n' + block('时域采样与重投影', 'GetClosestFragment') + '\nfloat4 Main(float4 p:SV_Position):SV_Target { return float4(GetClosestFragment(p.xy/1024),0,1); }',
        'clip': 'cbuffer C { float3 AABBMin; float3 AABBMax; float3 History; };\nfloat4 Main(float4 p:SV_Position):SV_Target {\n' + block('时域历史校验', 'float3 center') + '\nreturn float4(Result,1); }',
        'blend': 'cbuffer C { float2 motion; float3 historyColor; float3 currentColor; };\nfloat3 Blend() {\n' + block('时域历史校验', 'blendFactor') + '\n}\nfloat4 Main(float4 p:SV_Position):SV_Target { return float4(Blend(),1); }'
    }
    dxc = shutil.which('dxc')
    if not dxc:
        raise RuntimeError('DXC required; adopted HLSL has not been compiled')
    with tempfile.TemporaryDirectory(prefix='kb-longpage-hlsl-') as folder:
        for name, code in cases.items():
            source = Path(folder) / (name + '.hlsl')
            source.write_text(code, encoding='utf-8')
            run = subprocess.run([dxc, '-T', 'vs_6_0' if name == 'jitter' else 'ps_6_0', '-E', 'Main', str(source), '-Fo', str(source.with_suffix('.dxil'))], capture_output=True, text=True)
            assert run.returncode == 0, (name, run.stdout, run.stderr)
    return {'compiled_adopted_hlsl': list(cases), 'host': 'point-clamp normal-Z depth helpers and explicit uniforms; isolated offline shader compilation, no GPU execution'}


if __name__ == '__main__':
    result = verify()
    result.update(compile_aa())
    print(json.dumps(result, ensure_ascii=False, indent=2))
