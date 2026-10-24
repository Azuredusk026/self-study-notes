"""Verify source preservation and reviewed snapshots for the third full-read batch."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'知识库/examples/longpage_review'));from verify import headings,sha
def verify():
    d=json.loads((R/'skills/kb-structure-audit/references/fullread-batch-03-split-2026-10-24.json').read_text(encoding='utf-8'));sources={}
    for group in d['groups']:
        p=group['source_path'];source=(R/p).read_text(encoding='utf-8-sig');target=(R/group['target_path']).read_text(encoding='utf-8-sig')
        original=subprocess.check_output(['git','show',group['source_commit']+':'+p],cwd=R).decode().replace('\r\n','\n')
        assert sha(source)==group['source_sha256'];assert sha(target)==group['target_sha256']
        assert headings(original).keys()<=headings(source).keys(),p
        assert len(re.findall('[\u4e00-\u9fff]',source))<=6000,p
        assert len(re.findall('[\u4e00-\u9fff]',target))<=6000,group['target_path']
        sources.setdefault(p,[original,source]);sources[p][1]+='\n'+target
        for mapping in group['mappings']:
            before=headings(original)[mapping['source_heading']];after=headings(target)[mapping['target_heading']]
            assert sha(before)==mapping['source_body_sha256'];assert sha(after)==mapping['reviewed_body_sha256']
            if '/examples/' in group['target_path']:before=before.replace('../examples/outline/','')
            before=before.replace('初始RIS由前文证明满足这条关系','[[12_光线追踪/ReSTIR#单像素的重要性重采样]]证明初始RIS满足这条关系').replace('动态面光源按前文统一的','动态面光源按[[12_光线追踪/ReSTIR#面积测度与参数测度的交接]]统一的').replace('本页采用以下可实现的调度规则。','本页用B表示时域输出、C表示空间输出，K为当前像素的候选预算。采用以下可实现的调度规则。').replace('单个光删除仍采用前文目标置零而保留来源的规则','单个光删除仍采用[[12_光线追踪/ReSTIR#面积测度与参数测度的交接]]中的目标置零与保留来源规则')
            assert before==after,(p,mapping['source_heading'])
    urls=lambda s:set(re.findall(r'https?://[^\s)>]+',s))
    for path,(before,after) in sources.items():assert urls(before)<=urls(after),path
    return {'passed':True,'groups':len(d['groups']),'moved_sections':sum(len(g['mappings']) for g in d['groups']),'old_headings_preserved':True,'source_urls_missing':0,'scope':'exact source mechanism bodies with explicit cross-page context/path adjustments; semantic decisions recorded separately'}
if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
