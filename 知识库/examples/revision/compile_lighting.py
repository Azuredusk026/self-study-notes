"""提取文章中的函数编译；资源上传、绘制状态和 GPU 结果另行验证。"""
from pathlib import Path
import json, os, re, shutil, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[3]
DOMAIN = ROOT/'知识库/04_光照模型与PBR'

def blocks(name, language):
    return re.findall(r'```'+language+r'\n(.*?)```', (DOMAIN/(name+'.md')).read_text(encoding='utf-8'), re.S)

def run(command):
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stdout+result.stderr)

def main():
    dxc = os.environ.get('DXC_PATH') or shutil.which('dxc')
    glslang = shutil.which('glslangValidator')
    if not dxc or not glslang:
        raise RuntimeError('需要 PATH 中的 DXC 与 glslangValidator')
    cases = {
        'brdf': blocks('BRDF与微表面模型','hlsl')[0] + '\nfloat4 Main(float4 p:SV_Position):SV_Target { return float4(EvaluateDirectResponse(float3(0,0,1), normalize(float3(p.xy,1)), float3(0,0,1), .5.xxx, 0, .5, .04.xxx),1); }',
        'normal': '\n'.join(blocks('法线贴图','hlsl')) + '\nfloat4 Main(float4 p:SV_Position):SV_Target { float3 n=DecodeNormalWS(frac(p.xy),float3(0,0,1),float4(1,0,0,1)); return float4(BlendNormalRNM(n,normalize(float3(.2,.1,1))),1); }',
        'ibl': 'TextureCube<float4> Prefiltered:register(t0); Texture2D<float2> BrdfLut:register(t1); SamplerState LinearClamp:register(s0);\nfloat4 Main(float4 p:SV_Position):SV_Target { float3 N=float3(0,0,1), V=normalize(float3(p.xy,1)), F0=.04.xxx; float roughness=.5,maxMip=7; float2 lutSize=float2(128,128);\n' + blocks('IBL','hlsl')[0] + '\nreturn float4(specular,1); }'
    }
    with tempfile.TemporaryDirectory(prefix='kb-lighting-') as temporary:
        folder = Path(temporary)
        for name, code in cases.items():
            source = folder/(name+'.hlsl'); source.write_text(code, encoding='utf-8')
            run([dxc,'-T','ps_6_0','-E','Main',str(source),'-Fo',str(folder/(name+'.dxil'))])
        sky, refraction = blocks('Cubemap环境采样','glsl')
        vs = folder/'sky.vert'; fs = folder/'sky.frag'
        vs.write_text('#version 330 core\nlayout(location=0) in vec3 positionOS; uniform mat4 view,projection; uniform samplerCube environmentMap;\n'+sky+'\nvoid main(){gl_Position=SkyboxPosition(positionOS);}',encoding='utf-8')
        fs.write_text('#version 330 core\nuniform samplerCube environmentMap; uniform vec3 positionWS,cameraPositionWS,normalWS; uniform float etaIncident,etaTransmitted; out vec4 color; void main(){\n'+refraction+'\ncolor=vec4(environment,1);}',encoding='utf-8')
        run([glslang,'-l',str(vs),str(fs)])
    print(json.dumps({'passed':True,'dxc_entries':list(cases),'glsl_link':'sky/refraction','scope':'离线编译与链接，未执行GPU'},ensure_ascii=False))

if __name__ == '__main__':
    main()
