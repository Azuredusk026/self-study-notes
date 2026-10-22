"""Compile article fragments and run the independent CPU checks; no GPU execution."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent


def excerpt(title, marker):
    article = next((ROOT / '知识库').glob('*/' + title + '.md'))
    code = next(x for x in re.findall(r'```hlsl\n(.*?)\n```', article.read_text(encoding='utf-8'), re.S)
                if marker in x)
    return article, code


def verify():
    dxc = os.environ.get('DXC_PATH') or shutil.which('dxc')
    if not dxc:
        raise RuntimeError('DXC must be on PATH or specified by DXC_PATH')
    cpu = subprocess.run([sys.executable, str(HERE / 'test_reference.py')], capture_output=True, text=True)
    if cpu.returncode:
        raise RuntimeError(cpu.stdout + cpu.stderr)
    git_checks = subprocess.run([sys.executable, str(HERE / 'test_ci_excerpt.py')], capture_output=True, text=True)
    if git_checks.returncode:
        raise RuntimeError(git_checks.stdout + git_checks.stderr)
    probes = [
        ('Deferred Rendering', 'float outerRadius',
         'float axialLength=10, outerHalfAngle=.5, PI=3.14159265359; uint sideCount=8; float3 positionOS=float3(1,0,1);',
         'return float4(positionOS,1);', False),
        ('光线求交与BVH', 'bool IntersectAabb', '',
         'float4 Main(float4 p:SV_Position):SV_Target { float a,b; bool hit=IntersectAabb(float3(p.xy,0),float3(0,0,1),float3(-1,-1,-1),float3(1,1,1),a,b); return float4(a,b,hit,1); }', True),
        ('风格化眼睛', 'bool IrisUV', '',
         'float4 Main(float4 p:SV_Position):SV_Target { float2 uv; bool valid=IrisUV(p.xy*.01,float3(.3,.2,1),.1,1,uv); return float4(uv,valid,1); }', True),
        ('风格化眼睛', 'float facing',
         'float3 corneaNormalWS=float3(0,0,1), viewWS=normalize(float3(.3,.2,1)); float F0=.02; float3 irisLit=1, corneaReflection=.5; float eyelidVisibility=.8;',
         'return float4(color,1);', False),
        ('Face SDF', 'float3 lightHead',
         'float3x3 worldToHeadRotation=float3x3(1,0,0,0,1,0,0,0,1); float3 lightDirWS=float3(.5,.4,.1); float verticalThreshold=.25, userSoftness=.01; float2 faceSdf=p.xy*.01;',
         'return faceLit.xxxx;', False),
        ('角色布料', 'float3 BindRenderVertex', '',
         'float4 Main(float4 p:SV_Position):SV_Target { return float4(BindRenderVertex(0,float3(1,0,0),float3(0,1,0),float3(.2,.3,.5),.01),1); }', True),
        ('风格化头发高光', 'float3 shiftedT',
         'float3 T=float3(1,0,0), N=float3(0,0,1), H=normalize(float3(.5,.2,1)); float shift=.2, exponent=16, artistMask=1;',
         'return highlight.xxxx;', False),
        ('NPR材质与分层光照', 'float level',
         'float toonLightOffset=.1, smoothness=.2, ndotl=p.x*.01;',
         'return toonNoL.xxxx;', False),
        ('NPR材质与分层光照', 'float3 ramp',
         'float3 normalWS=float3(0,0,1), lightDirWS=normalize(float3(1,0,1)); float materialRowUv=.5, visibility=.5; float3 shadowTint=float3(.2,.3,.4), baseColor=1;',
         'return float4(litColor,1);', False),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix='kb-review-0915-') as temp:
        folder = Path(temp)
        for index, (title, marker, setup, output, function) in enumerate(probes):
            article, code = excerpt(title, marker)
            source = code + '\n' + output if function else 'float4 Main(float4 p:SV_Position):SV_Target {\n' + setup + '\n' + code + '\n' + output + '\n}'
            if title == 'NPR材质与分层光照' and marker == 'float3 ramp':
                source = 'Texture2D<float4> LightRamp; SamplerState PointClamp;\n' + source
            path = folder / (str(index) + '.hlsl')
            path.write_text(source, encoding='utf-8')
            args = [dxc, '-T', 'ps_6_0', '-E', 'Main', str(path), '-Fo', str(folder / (str(index) + '.dxil'))]
            result = subprocess.run(args, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(title + '\n' + result.stdout + result.stderr)
            results.append({'article': article.relative_to(ROOT).as_posix(), 'marker': marker,
                            'excerpt_sha256': hashlib.sha256(code.encode()).hexdigest(),
                            'target': 'ps_6_0', 'entry': 'Main', 'exit_code': result.returncode,
                            'diagnostics': result.stdout + result.stderr})
    version = subprocess.run([dxc, '--version'], capture_output=True, text=True)
    count = int(re.search(r'Ran (\d+) tests?', cpu.stdout + cpu.stderr).group(1))
    return {'date': '2026-10-22', 'passed': True, 'cpu_tests': count,
            'git_index_tests': int(re.search(r'Ran (\d+) tests?', git_checks.stdout + git_checks.stderr).group(1)),
            'git_index_output': git_checks.stdout + git_checks.stderr,
            'cpu_output': cpu.stdout + cpu.stderr, 'compiler': dxc,
            'compiler_version': version.stdout + version.stderr, 'shader_probes': results,
            'scope': 'CPU algebra tests and extracted HLSL fragment compilation; engine, GPU execution, capture and performance UNVERIFIED'}


if __name__ == '__main__':
    result = verify()
    (HERE / 'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'cpu_tests': result['cpu_tests'],
                      'git_index_tests': result['git_index_tests'],
                      'shader_probes': len(result['shader_probes']), 'scope': result['scope']}))
