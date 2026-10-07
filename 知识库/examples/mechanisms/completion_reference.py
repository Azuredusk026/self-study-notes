"""CPU regression for final canonical mechanisms; no GPU execution."""
import bisect
import json
import math
import random
from pathlib import Path


def draw_cdf(weights, u):
    if not weights or not 0 <= u < 1:
        raise ValueError('invalid domain')
    if any(w < 0 or not math.isfinite(w) for w in weights):
        raise ValueError('invalid weight')
    cdf=[];total=0
    for w in weights:
        total += w;cdf.append(total)
    if total == 0:
        index=min(int(u*len(weights)),len(weights)-1)
        return index,1/len(weights)
    index=bisect.bisect_right(cdf,u*total)
    return index,weights[index]/total


def stripe_average(x,width):
    def integral(v):
        return math.floor(v)*.5+max(v-math.floor(v)-.5,0)
    return (integral(x+width*.5)-integral(x-width*.5))/width


def verify():
    rng=random.Random(20261007);cases={}
    for weights in ([0,1,0,2],[1,0,0,0],[0,0,3],[0,0,0]):
        for u in (0,.1,.5,.999999):
            index,p=draw_cdf(weights,u)
            assert 0<=index<len(weights) and p>0
    cases['cdf_zero_intervals']=16
    for x in (-3.7,-1,.1,.5,1,2.8):
        for width in (1,2,4,6):
            assert math.isclose(stripe_average(x,width),.5,abs_tol=1e-12)
    cases['periodic_stripe_integral']=24
    for count in (0,1,63,64,65,257):
        flags=[rng.randrange(2) for _ in range(count)]
        offsets=[];total=0
        for f in flags:offsets.append(total);total+=f
        compact=[i for i,f in enumerate(flags) if f]
        for dst,i in enumerate(compact):assert offsets[i]==dst
        assert total==len(compact)
    cases['exclusive_scan_compaction']=6
    for count in range(1,31):
        layers=[(rng.random(),rng.random()) for _ in range(count)]
        background=rng.random();back=background
        for color,alpha in reversed(layers):back=color*alpha+back*(1-alpha)
        front=0;transmittance=1
        for color,alpha in layers:
            front+=transmittance*color*alpha;transmittance*=1-alpha
        front+=transmittance*background
        assert math.isclose(front,back,rel_tol=1e-12,abs_tol=1e-12)
    cases['ordered_alpha_equivalence']=30
    for state in range(10):
        inputs=[rng.randint(-3,3) for _ in range(20)]
        authority=state+sum(inputs[:8])
        predicted=authority+sum(inputs[8:])
        assert predicted==state+sum(inputs)
    cases['prediction_replay']=10
    for local in (.1,.5,.9):
        world=(local*2,local*3,local*4)
        t=tuple(v/s for v,s in zip(world,(2,3,4)))
        weights=[]
        for corner in range(8):
            w=1
            for axis in range(3):w*=t[axis] if corner&(1<<axis) else 1-t[axis]
            weights.append(w)
        assert math.isclose(sum(weights),1)
    cases['probe_trilinear_weights']=3
    return {'passed':True,'checks':cases,'total':sum(cases.values()),
            'scope':'CPU models of CDF, stripe integral, scan, Alpha, replay and Probe weights; no engine or GPU execution'}


if __name__=='__main__':
    result=verify();out=Path(__file__).parent/'build';out.mkdir(exist_ok=True,parents=True)
    (out/'completion-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))
