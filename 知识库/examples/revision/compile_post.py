"""颜色与后处理正文函数的 HLSL 编译宿主。"""
from pathlib import Path
import json,os,re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[3];DOMAIN=ROOT/'知识库/07_颜色与后处理'
def snippets(name):
    return '\n'.join(re.findall(r'```hlsl\n(.*?)```',(DOMAIN/(name+'.md')).read_text(encoding='utf-8'),re.S))
def main():
    dxc=os.environ.get('DXC_PATH') or shutil.which('dxc')
    if not dxc:raise RuntimeError('需要DXC')
    declarations='Texture2D<float4> Source:register(t0); SamplerState LinearClamp:register(s0);\n'
    ao_declarations='''Texture2D<float4> NoiseTexture:register(t0),PositionTexture:register(t1);
SamplerState NoiseSampler:register(s0),PointSampler:register(s1);
cbuffer Parameters:register(b0) { float4x4 Projection; float3 Kernel[64]; float2 NoiseScale; uint KernelSize; float Radius; float Bias; };
'''
    cases={
        'srgb':snippets('颜色空间')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { return float4(DecodeSRGB(frac(p.x)),EncodeSRGB(frac(p.y)),0,1); }',
        'exposure':snippets('HDR与曝光')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { return float4(ExposureForDisplay(HistoryInCurrentScale(p.xyz,.5,2),2,.25),1); }',
        'bloom':declarations+snippets('Bloom')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { return float4(ExtractBloom(DownsampleBloom(p.xy/1024.0,1.0/2048.0),1,.5),1); }',
        'ssao':ao_declarations+snippets('屏幕空间AO')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { return ComputeSSAO(p.xy/1024.0,float3(0,0,-2),float3(0,0,1)).xxxx; }',
        'coc':snippets('景深与运动模糊')+'\nfloat4 Main(float4 p:SV_Position):SV_Target { return CoCRadiusPixels(max(p.x,.1),2,.05,2,.036,1920).xxxx; }'
    }
    with tempfile.TemporaryDirectory(prefix='kb-post-') as temporary:
        folder=Path(temporary)
        for name,code in cases.items():
            source=folder/(name+'.hlsl');source.write_text(code,encoding='utf-8')
            result=subprocess.run([dxc,'-T','ps_6_0','-E','Main',str(source),'-Fo',str(folder/(name+'.dxil'))],capture_output=True,text=True,encoding='utf-8',errors='replace')
            if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    print(json.dumps({'passed':True,'dxc_entries':list(cases),'scope':'仅离线编译，未执行GPU'},ensure_ascii=False))
if __name__=='__main__':main()
