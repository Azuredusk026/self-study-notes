"""Compile canonical article fragments with DXC; no shader execution."""
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BUILD=Path(__file__).parent/'build/completion-dxc'
DXC=Path(r'C:\VulkanSDK\1.4.357.0\Bin\dxc.exe')


def verify():
    BUILD.mkdir(parents=True,exist_ok=True)
    def block(name,marker):
        path=next((ROOT/'知识库').glob('*/'+name+'.md'))
        for code in re.findall(r'```hlsl\n(.*?)\n```',path.read_text(encoding='utf-8'),re.S):
            if marker in code:return code
        raise ValueError(name)
    specs=[
        ('CopyKernel','cs_6_0',block('Compute Shader','void CopyKernel')),
        ('StripePS','ps_6_0',block('采样与混叠','BandLimitedStripe')+
         '\nfloat4 StripePS(float4 p:SV_Position):SV_Target { return BandLimitedStripe(p.xy*.01,8).xxxx; }'),
        ('GlyphPS','ps_6_0','Texture2D<float> GlyphAtlas; SamplerState LinearClamp; float SdfSoftness;\n'+block('文字渲染','GlyphAlpha')+
         '\nfloat4 GlyphPS(float4 p:SV_Position):SV_Target { return GlyphAlpha(p.xy*.01).xxxx; }'),
        ('MorphPS','ps_6_0',block('角色布料','BindRenderVertex')+
         '\nfloat4 MorphPS(float4 p:SV_Position):SV_Target { return float4(BindRenderVertex(0,float3(1,0,0),float3(0,0,1),float3(.2,.3,.5),.1),1); }')]
    results=[]
    for entry,target,code in specs:
        src=BUILD/(entry+'.hlsl');dest=BUILD/(entry+'.dxil');src.write_text(code,encoding='utf-8')
        args=[str(DXC),'-T',target,'-E',entry,str(src),'-Fo',str(dest)]
        result=subprocess.run(args,capture_output=True,text=True)
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
        results.append({'entry':entry,'target':target,'passed':True,'scope':'DXC fragment compile only'})
    return {'passed':True,'probes':results,'total':len(results),'runtime':'UNVERIFIED'}


if __name__=='__main__':
    result=verify();(BUILD/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
