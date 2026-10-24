"""Compile current article fragments in isolated CPU hosts; no GPU execution.

Run: python -B 知识库/examples/remaining_review/verify.py
Optional --baseline <git revision> reproduces the dynamic-offset failure.
Vulkan API types/calls are explicit stubs; this checks address arithmetic only.
"""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,tempfile

ROOT=Path(__file__).resolve().parents[3]


def verify_migration():
    manifest=ROOT/'skills/kb-structure-audit/references/remaining-memory-split-2026-10-24.json'
    data=json.loads(manifest.read_text(encoding='utf-8'))
    def digest(s):return hashlib.sha256(s.encode()).hexdigest()
    def sections(s):
        parts=re.split(r'^#{1,6} (.+)\n',s,flags=re.M)
        return {parts[i]:parts[i+1].strip() for i in range(1,len(parts),2)}
    source=subprocess.check_output(['git','show',data['source_commit']+':'+data['source_path']],cwd=ROOT).decode('utf-8').replace('\r\n','\n')
    current=(ROOT/data['source_path']).read_text(encoding='utf-8-sig')
    assert digest(current)==data['adopted_source_sha256']
    assert sections(source).keys()<=sections(current).keys()
    combined=current
    for article in data['articles']:
        target=(ROOT/article['path']).read_text(encoding='utf-8-sig')
        assert digest(target)==article['reviewed_sha256']
        assert len(re.findall('[\u4e00-\u9fff]',target))<=6000
        combined+='\n'+target
    assert len(re.findall('[\u4e00-\u9fff]',current))<=6000
    for mapping in data['mappings']:
        before=sections(source)[mapping['source_heading']]
        target=sections((ROOT/mapping['target_path']).read_text(encoding='utf-8-sig'))[mapping['target_heading']]
        assert digest(before)==mapping['source_body_sha256']
        assert digest(target)==mapping['reviewed_body_sha256']
        before=before.replace('C++工程边界#普通销毁与对象借用','插件接口与对象借用#普通销毁与对象借用').replace('C++工程边界#关闭期间的依赖清理调用','插件关闭与卸载#关闭期间的依赖清理调用')
        assert before==target
    urls=lambda s:set(re.findall(r'https?://[^\s)>]+',s))
    assert urls(source)<=urls(combined)
    return {'old_headings_preserved':True,'complete_sections':len(data['mappings']),'missing_source_urls':0}


def verify(baseline=None):
    def text(name):
        p=next((ROOT/'知识库').glob('*/'+name+'.md'))
        if baseline:
            return subprocess.check_output(['git','show',baseline+':'+p.relative_to(ROOT).as_posix()],cwd=ROOT).decode('utf-8').replace('\r\n','\n')
        return p.read_text(encoding='utf-8-sig')
    blocks=re.findall(r'```cpp\n(.*?)\n```',text('线程同步'),re.S)
    queue=next(b for b in blocks if 'class Queue' in b)
    pub=next(b for b in blocks if 'memory_order_release' in b)
    global_data,rest=pub.split('// 生产者\n')
    producer,consumer=rest.split('// 消费者\n')
    binding=next(b for b in re.findall(r'```cpp\n(.*?)\n```',text('GPU资源绑定'),re.S) if 'dynamicOffset' in b)
    host=r'''
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <thread>
#include <vector>
''' + queue + '\n' + global_data + r'''
using VkDeviceSize=uint64_t;
struct Limits { VkDeviceSize minUniformBufferOffsetAlignment; };
struct MaterialConstants { unsigned char bytes[80]; };
uint32_t capturedOffset=0;
const int VK_PIPELINE_BIND_POINT_GRAPHICS=0;
void vkCmdBindDescriptorSets(int,int,int,int,int,int*,int,uint32_t* value) { capturedOffset=*value; }
uint32_t address(VkDeviceSize frameBase,VkDeviceSize materialIndex,VkDeviceSize bufferSize,VkDeviceSize align=256) {
    Limits limits{align};
    int commandBuffer=0,pipelineLayout=0,materialSetIndex=1,materialSet=0;
''' + binding + r'''
    return capturedOffset;
}
template<class F> void reject(F run) {
    try { run(); } catch(const std::exception&) { return; }
    throw std::runtime_error("overflow or invalid material range was accepted");
}
int main() { try {
    // First case reproduces wraparound in the baseline without hitting assert.
    reject([]{ address(UINT64_MAX-255,1,UINT64_MAX); });
    assert(address(4096,3,8192)==4864);
    assert(address(0,0,80)==0);
    reject([]{ address(0,0,79); });
    reject([]{ address(1,0,8192); });
    reject([]{ address(0,UINT64_MAX,UINT64_MAX); });
    reject([]{ address(uint64_t(UINT32_MAX)+1,0,UINT64_MAX); });
    reject([]{ address(0,0,8192,0); });
    std::cout << "8 dynamic-offset cases passed\n";
    {
        Queue q; q.push(7); assert(q.pop()==7); q.close();
        assert(!q.pop()); assert(!q.push(8)); q.close();
    }
    {
        Queue q; std::atomic<int> finished{0}; std::vector<std::thread> ts;
        for(int i=0;i<4;++i) ts.emplace_back([&]{ assert(!q.pop()); ++finished; });
        q.close(); for(auto& t:ts)t.join(); assert(finished==4);
    }
    {
        Queue q; constexpr int count=1000; std::array<std::atomic<int>,count> seen{};
        for(int i=0;i<count;++i)q.push(i);
        std::vector<std::thread> ts;
        for(int i=0;i<4;++i) ts.emplace_back([&]{ while(auto id=q.pop())++seen[*id]; });
        q.close(); for(auto& t:ts)t.join(); for(auto& n:seen)assert(n==1);
    }
    {
        Queue q; std::atomic<int> accepted{0},consumed{0};
        std::thread c([&]{while(q.pop())++consumed;});
        std::thread p([&]{for(int i=0;i<1000;++i)if(q.push(i))++accepted;});
        q.close(); p.join(); c.join(); assert(accepted==consumed);
    }
    for(int i=0;i<100;++i) {
        payload=0; ready.store(false,std::memory_order_relaxed);
        std::thread p([]{
''' + producer + r'''
        });
        std::thread c([]{
''' + consumer + r'''
            assert(value==42);
        }); p.join(); c.join();
    }
    std::cout << "4 queue scenarios and 100 release/acquire handoffs passed\n";
    return 0;
} catch(const std::exception& e) { std::cerr<<e.what()<<"\n"; return 2; } }
'''
    compiler=shutil.which('clang++') or 'C:/Program Files/LLVM/bin/clang++.exe'
    with tempfile.TemporaryDirectory(prefix='kb-remaining-review-') as folder:
        source=Path(folder)/'host.cpp';exe=Path(folder)/'host.exe';source.write_text(host,encoding='utf-8')
        build=subprocess.run([compiler,'-std=c++17','-O0',str(source),'-o',str(exe)],capture_output=True,text=True,timeout=60)
        assert build.returncode==0,build.stdout+build.stderr
        run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
        if baseline:
            assert run.returncode==2 and 'was accepted' in run.stderr,(run.returncode,run.stdout,run.stderr)
        else:assert run.returncode==0,(run.returncode,run.stdout,run.stderr)
    return {'passed':True,'baseline':baseline,'expected_failure_reproduced':bool(baseline),'compiler':compiler,'stdout':run.stdout,'stderr':run.stderr,'migration':None if baseline else verify_migration(),'scope':'current C++17 queue and one-shot publication in real threads; stubbed Vulkan address arithmetic, no GPU/device/runtime integration or race-detector proof'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--baseline');args=p.parse_args()
    print(json.dumps(verify(args.baseline),ensure_ascii=False,indent=2))
