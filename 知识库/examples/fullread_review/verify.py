"""Extract article C++/HLSL fragments: CPU CDF checks and offline DXC only."""
from pathlib import Path
import argparse,json,re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[3]
def verify(baseline=None):
    def article(name):
        p=next((ROOT/'知识库').glob('*/'+name+'.md'))
        if baseline:return subprocess.check_output(['git','show',baseline+':'+p.relative_to(ROOT).as_posix()],cwd=ROOT).decode('utf-8').replace('\r\n','\n')
        return p.read_text(encoding='utf-8-sig')
    block=next(b for b in re.findall(r'```cpp\n(.*?)\n```',article('Monte Carlo采样'),re.S) if 'DrawFromCdf' in b)
    cpp='''#include <algorithm>
#include <cassert>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <vector>
template<class T> using Span=std::vector<T>&;
struct Sample { int index=-1; float probability=0; };
template<class A,class B> auto Min(A a,B b) { return a<b?a:b; }
int UpperBound(const std::vector<float>& a,float x) { return int(std::upper_bound(a.begin(),a.end(),x)-a.begin()); }
'''+block+'''
Sample draw(std::vector<float> w,float u=0) { std::vector<float> c(w.size());return DrawFromCdf(w,c,u); }
template<class F> void reject(F f) { try { f(); } catch(const std::range_error&) {return;} throw std::runtime_error("unrepresentable positive mass accepted"); }
int main() { try {
 reject([]{draw({16777216.f,1.f});});
 reject([]{draw({1e-30f,1e30f});});
 reject([]{draw({std::numeric_limits<float>::max(),std::numeric_limits<float>::max()});});
 assert(draw({0,1,0,3,0},0).index==1);
 assert(draw({0,1,0,3,0},.25f).index==3);
 assert(draw({0,1,0,3,0},std::nextafter(1.f,0.f)).index==3);
 auto uniform=draw({0,0},.5f);assert(uniform.index==1 && uniform.probability==.5f);
 assert(draw({}).index==-1);
 return 0;
 } catch(const std::exception&) {return 2;} }
'''
    clang=shutil.which('clang++') or 'C:/Program Files/LLVM/bin/clang++.exe'
    with tempfile.TemporaryDirectory(prefix='kb-fullread-') as directory:
        root=Path(directory);source=root/'cdf.cpp';exe=root/'cdf.exe';source.write_text(cpp,encoding='utf-8')
        build=subprocess.run([clang,'-std=c++17','-O0',str(source),'-o',str(exe)],capture_output=True,text=True,timeout=60)
        assert build.returncode==0,build.stderr
        run=subprocess.run([str(exe)],timeout=20)
        assert run.returncode==(2 if baseline else 0),run.returncode
        if not baseline:
            peel=next(b for b in re.findall(r'```hlsl\n(.*?)\n```',article('透明合成'),re.S) if 'PreviousDepth' in b)
            hlsl='''Texture2D<float> PreviousDepth:register(t0);
Texture2D<float> OpaqueDepth:register(t1);
SamplerState PointClamp:register(s0);
cbuffer Settings:register(b0) {uint peelIndex;float depthTolerance;float2 padding;};
struct In {float4 position:SV_Position;float2 screenUV:TEXCOORD0;float deviceDepth:TEXCOORD1;};
struct Out {float depthTarget:SV_Target0;float4 colorTarget:SV_Target1;};
Out PeelPS(In input) {Out output;float4 shadedColor=float4(1,0,0,0.5);
'''+peel+'\nreturn output;}'
            shader=root/'peel.hlsl';shader.write_text(hlsl,encoding='utf-8')
            compiler=shutil.which('dxc') or 'C:/VulkanSDK/1.4.350.0/Bin/dxc.exe'
            result=subprocess.run([compiler,'-T','ps_6_0','-E','PeelPS',str(shader),'-Fo',str(root/'peel.dxil')],capture_output=True,text=True,timeout=60)
            assert result.returncode==0,result.stderr
    return {'passed':True,'baseline':baseline,'expected_baseline_failure':bool(baseline),'cdf_cases_passed':0 if baseline else 8,'baseline_failure_case':'positive interval 16777216+1 collapsed' if baseline else None,'depth_peel_offline_compiled':not bool(baseline),'scope':'actual article fragments; C++17 CPU checks and offline HLSL compilation, no GPU output'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline');a=p.parse_args();print(json.dumps(verify(a.baseline),ensure_ascii=False,indent=2))
