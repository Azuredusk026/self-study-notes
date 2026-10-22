"""从正文提取插值、投影、面积光和阴影机制函数，检查离线编译。"""
from pathlib import Path
import json,os,re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[3]
DOMAIN=ROOT/'知识库/05_光照阴影与GI'
def snippet(name):
    return re.findall(r'```hlsl\n(.*?)```',(DOMAIN/(name+'.md')).read_text(encoding='utf-8'),re.S)[0]
def main():
    dxc=os.environ.get('DXC_PATH') or shutil.which('dxc')
    glslang=shutil.which('glslangValidator')
    if not dxc or not glslang:raise RuntimeError('需要 DXC 与 glslangValidator')
    cases={
        'probe':snippet('Light Probe')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { SH9 sh=InterpolateProbes(p.xyz,0.0.xxx,1.0.xxx,uint3(8,8,8)); return float4(sh.c[0]+sh.c[8],1); }',
        'reflection':snippet('Reflection Probe')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { float3 d; bool valid=BoxProjectedDirection(frac(p.xyz),float3(0,0,1),-1.0.xxx,1.0.xxx,0.0.xxx,d); return float4(d,valid?1:0); }',
        'ltc':snippet('直接光照')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { float3 v[4]={float3(-1,-1,1),float3(1,-1,1),float3(1,1,1),float3(-1,1,1)}; for(uint i=0;i<4;++i)v[i].z+=abs(p.x)*.001; return IntegrateLTCCosine(v).xxxx; }',
        'pcf':'Texture2D<float> ShadowMap:register(t0); SamplerComparisonState ShadowSampler:register(s0);\n'+snippet('Shadow Map')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { return SampleShadowPCF(frac(p.xyz),.001).xxxx; }'
    }
    cascade,point=re.findall(r'```glsl\n(.*?)```',(DOMAIN/'Shadow Map.md').read_text(encoding='utf-8'),re.S)
    glsl_cases={
        'cascade':'#version 330 core\nuniform mat4 view; uniform int cascadeCount; uniform float cascadeSplits[4]; out vec4 color;\n'+cascade+'\nvoid main(){ color=vec4(float(SelectCascade(vec3(0,0,-1)))); }',
        'point':'#version 330 core\nuniform vec3 lightPositionWS; uniform samplerCube pointShadowMap; uniform float shadowFar,shadowBias; out vec4 color;\n'+point+'\nvoid main(){ color=vec4(PointShadow(vec3(0,0,1))); }'
    }
    with tempfile.TemporaryDirectory(prefix='kb-gi-') as temporary:
        folder=Path(temporary)
        for name,code in cases.items():
            source=folder/(name+'.hlsl');source.write_text(code,encoding='utf-8')
            result=subprocess.run([dxc,'-T','ps_6_0','-E','Main',str(source),'-Fo',str(folder/(name+'.dxil'))],capture_output=True,text=True,encoding='utf-8',errors='replace')
            if result.returncode:raise RuntimeError(result.stdout+result.stderr)
        for name,code in glsl_cases.items():
            source=folder/(name+'.frag');source.write_text(code,encoding='utf-8')
            result=subprocess.run([glslang,str(source)],capture_output=True,text=True,encoding='utf-8',errors='replace')
            if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    print(json.dumps({'passed':True,'dxc_entries':list(cases),'glsl_entries':list(glsl_cases),'scope':'离线编译；无GPU执行'},ensure_ascii=False))
if __name__=='__main__':main()
