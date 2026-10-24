"""Run extracted arithmetic/control fragments in a C++17 CPU host, without GPU."""
from pathlib import Path
import argparse,json,re,subprocess,tempfile,shutil
ROOT=Path(__file__).resolve().parents[3]
def verify(baseline=None,case='all'):
    def block(name,marker):
        p=next((ROOT/'知识库').glob('*/'+name+'.md'))
        t=subprocess.check_output(['git','show',baseline+':'+p.relative_to(ROOT).as_posix()],cwd=ROOT).decode().replace('\r\n','\n') if baseline else p.read_text(encoding='utf-8-sig')
        return next(b for b in re.findall(r'```hlsl\n(.*?)\n```',t,re.S) if marker in b)
    denoise=block('光追降噪','float2 historyUv');cloth=block('角色布料','float3 BindRenderVertex')
    host=r'''
#include <algorithm>
#include <cmath>
#include <limits>
struct float2 {float x,y;}; struct float3 {float x,y,z;};
float2 operator+(float2 a,float2 b){return {a.x+b.x,a.y+b.y};}
bool operator>=(float2 a,float b){return a.x>=b&&a.y>=b;}
bool operator<=(float2 a,float b){return a.x<=b&&a.y<=b;}
float3 operator+(float3 a,float3 b){return {a.x+b.x,a.y+b.y,a.z+b.z};}
float3 operator-(float3 a,float3 b){return {a.x-b.x,a.y-b.y,a.z-b.z};}
float3 operator*(float3 a,float s){return {a.x*s,a.y*s,a.z*s};}
bool all(bool b){return b;} using std::isfinite;
bool isfinite(float3 v){return isfinite(v.x)&&isfinite(v.y)&&isfinite(v.z);}
float dot(float3 a,float3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
float3 cross(float3 a,float3 b){return {a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x};}
float rsqrt(float x){return 1.f/std::sqrt(x);}
float min(float a,float b){return std::min(a,b);} float max(float a,float b){return std::max(a,b);}
float3 lerp(float3 a,float3 b,float t){return a*(1-t)+b*t;}
float3 ClampHistory(float3 v){return {std::clamp(v.x,-10.f,10.f),std::clamp(v.y,-10.f,10.f),std::clamp(v.z,-10.f,10.f)};}
struct History {float linearDepth=0;float3 normalWS{};unsigned objectId=0;float sampleCount=0;float3 radiance{};};
History fixture;int loads=0;
History ZeroHistory(){return {};}
History LoadHistory(float2){++loads;return fixture;}
float3 gather(float2 uv={.5f,.5f}) {
float2 motionVector{0,0};float currentDepthInPreviousView=5,depthThreshold=.1f,normalThreshold=.8f,maxHistory=.95f;
unsigned objectId=1;float3 normalWS{0,0,1},currentRadiance{6,6,6};
'''+denoise+r'''
return accumulated;}
'''+cloth+r'''
bool close(float a,float b){return std::abs(a-b)<1e-5f;}
int main() {
'''
    if case in ['all','denoise']:
        host+=r'''
fixture={5,{0,0,1},1,3,{2,2,2}};
if(!close(gather().x,3))return 3;
fixture.objectId=2;fixture.radiance.x=std::numeric_limits<float>::quiet_NaN();
if(!close(gather().x,6))return 2;
fixture={5,{0,0,1},1,-1,{2,2,2}};
if(!close(gather().x,6))return 2;
loads=0;if(!close(gather({2,2}).x,6)||loads!=0)return 3;
'''
    if case in ['all','cloth']:
        host+=r'''
float3 p=BindRenderVertex({0,0,0},{.0001f,0,0},{0,.0001f,0},{.2f,.3f,.5f},.01f);
if(!close(p.z,.01f))return 2;
'''
    host+='return 0;}';clang=shutil.which('clang++') or 'C:/Program Files/LLVM/bin/clang++.exe'
    with tempfile.TemporaryDirectory(prefix='kb-denoise-cloth-') as folder:
        p=Path(folder);(p/'host.cpp').write_text(host,encoding='utf-8');r=subprocess.run([clang,'-std=c++17','-O0',str(p/'host.cpp'),'-o',str(p/'host.exe')],capture_output=True,text=True,timeout=60);assert r.returncode==0,r.stderr
        result=subprocess.run([str(p/'host.exe')],timeout=20);assert result.returncode==(2 if baseline else 0),result.returncode
    return {'passed':True,'baseline':baseline,'case':case,'baseline_failure_reproduced':bool(baseline),'scope':'actual HLSL arithmetic/control fragments compiled as equivalent C++17 CPU operations; vector/resource helpers are host implementations, no GPU execution'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline');p.add_argument('--case',choices=['all','denoise','cloth'],default='all');a=p.parse_args();print(json.dumps(verify(a.baseline,a.case),ensure_ascii=False,indent=2))
