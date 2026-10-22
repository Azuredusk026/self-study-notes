"""Compile article excerpts and inspect their declared interface contract."""
from pathlib import Path
import json,os,re,shutil,subprocess,tempfile

ROOT=Path(__file__).resolve().parents[3]
DOMAIN=ROOT/'知识库/03_Shader编程'
DXC=os.environ.get('DXC_PATH') or shutil.which('dxc')
GLSLANG=shutil.which('glslangValidator')

def run(command,expected=0):
    result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if (result.returncode==0)!=(expected==0):
        raise RuntimeError(result.stdout+result.stderr)
    return result

def main():
    if not DXC or not GLSLANG: raise RuntimeError('DXC and glslangValidator required on PATH')
    outputs=[]
    with tempfile.TemporaryDirectory(prefix='kb-shader-') as tmp:
        folder=Path(tmp)
        scan_text=(DOMAIN/'GPU归约与前缀和.md').read_text(encoding='utf-8')
        scan=next(code for code in re.findall(r'```hlsl\n(.*?)```',scan_text,re.S) if 'void ScanGroups' in code)
        source=folder/'scan.hlsl';source.write_text(scan,encoding='utf-8')
        run([DXC,'-T','cs_6_0','-E','ScanGroups',str(source),'-Fo',str(folder/'scan.dxil')])
        outputs.append('ScanGroups cs_6_0 compilation')

        interface_text=(DOMAIN/'Shader接口与数据流.md').read_text(encoding='utf-8')
        per_view=next(code for code in re.findall(r'```hlsl\n(.*?)```',interface_text,re.S) if 'cbuffer PerView' in code)
        source=folder/'layout.hlsl'
        source.write_text(per_view+'\nfloat4 Main(float4 p:POSITION):SV_Position { return mul(ViewProjection,p)+float4(CameraPositionWS,Exposure)+float4(RenderSize,InvRenderSize); }',encoding='utf-8')
        assembly=folder/'layout.txt'
        run([DXC,'-T','vs_6_0','-E','Main',str(source),'-Od','-Fo',str(folder/'layout.dxil'),'-Fc',str(assembly)])
        text=assembly.read_text(encoding='utf-8')
        for field,offset in [('ViewProjection',0),('CameraPositionWS',64),('Exposure',76),('RenderSize',80),('InvRenderSize',88)]:
            assert re.search(r'\b'+field+r'\s*;[^\n]*Offset:\s*'+str(offset)+r'\b',text),field
        assert re.search(r'PerView;[^\n]*Size:\s*96\b',text),'PerView size'
        outputs.append('PerView vs_6_0 compilation; five offsets and 96-byte size')

        glsl=next(code for code in re.findall(r'```glsl\n(.*?)```',interface_text,re.S) if 'out VertexData' in code)
        vs,fs=glsl.split('// Fragment Shader')
        vs='#version 330 core\n'+vs+'\nvoid main(){gl_Position=vec4(positionOS,1);vsOut.uv=positionOS.xy;vsOut.normalWS=vec3(0,0,1);}\n'
        fs='#version 330 core\n'+fs
        vertex=folder/'interface.vert';fragment=folder/'interface.frag'
        vertex.write_text(vs,encoding='utf-8');fragment.write_text(fs,encoding='utf-8')
        run([GLSLANG,'-l',str(vertex),str(fragment)])
        outputs.append('GLSL 330 VertexData matched block links with different instance names')
        fragment.write_text(fs.replace('vec2 uv;', 'vec3 uv;'),encoding='utf-8')
        run([GLSLANG,'-l',str(vertex),str(fragment)],expected=1)
        outputs.append('GLSL mismatched block member type correctly rejected')
    print(json.dumps({'passed':True,'checks':outputs,'scope':'Compilation, reflection and offline linking; no GPU execution'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
