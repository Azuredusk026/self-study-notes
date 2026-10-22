"""从正文提取插值、投影、面积光和阴影机制函数，检查 HLSL 编译。"""
from pathlib import Path
import json,os,re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[3]
DOMAIN=ROOT/'知识库/05_光照阴影与GI'
def snippet(name):
    return re.findall(r'```hlsl\n(.*?)```',(DOMAIN/(name+'.md')).read_text(encoding='utf-8'),re.S)[0]
def main():
    dxc=os.environ.get('DXC_PATH') or shutil.which('dxc')
    if not dxc:raise RuntimeError('需要 DXC')
    cases={
        'probe':snippet('Light Probe')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { SH9 sh=InterpolateProbes(p.xyz,0.0.xxx,1.0.xxx,uint3(8,8,8)); return float4(sh.c[0]+sh.c[8],1); }',
        'reflection':snippet('Reflection Probe')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { float3 d; bool valid=BoxProjectedDirection(frac(p.xyz),float3(0,0,1),-1.0.xxx,1.0.xxx,0.0.xxx,d); return float4(d,valid?1:0); }',
        'ltc':snippet('直接光照')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { float3 v[4]={float3(-1,-1,1),float3(1,-1,1),float3(1,1,1),float3(-1,1,1)}; v[0].z+=p.x*.001; return IntegrateLTCCosine(v).xxxx; }',
        'pcf':'Texture2D<float> ShadowMap:register(t0); SamplerComparisonState ShadowSampler:register(s0);\n'+snippet('Shadow Map')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { return SampleShadowPCF(frac(p.xyz),.001).xxxx; }'
    }
    with tempfile.TemporaryDirectory(prefix='kb-gi-') as temporary:
        folder=Path(temporary)
        for name,code in cases.items():
            source=folder/(name+'.hlsl');source.write_text(code,encoding='utf-8')
            result=subprocess.run([dxc,'-T','ps_6_0','-E','Main',str(source),'-Fo',str(folder/(name+'.dxil'))],capture_output=True,text=True,encoding='utf-8',errors='replace')
            if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    print(json.dumps({'passed':True,'dxc_entries':list(cases),'scope':'HLSL离线编译；无GPU执行'},ensure_ascii=False))
if __name__=='__main__':main()
