"""Exact finite-domain outcomes for source-support normalization, not GPU code."""


def merge_outcomes(pools, current_target, source_targets, mode):
    weights=[0.0 if y is None else current_target[y]*w*m for y,w,m in pools]
    total=sum(weights)
    if total==0:
        return []
    outcomes=[]
    for origin,((y,_,_),weight) in enumerate(zip(pools,weights)):
        if weight==0:
            continue
        if mode=='naive':
            numerator=1
            denominator=sum(m for _,_,m in pools)
        elif mode=='support':
            numerator=1
            denominator=sum(m for (_,_,m),h in zip(pools,source_targets) if h[y]>0)
        elif mode=='weighted':
            numerator=source_targets[origin][y]
            denominator=sum(m*h[y] for (_,_,m),h in zip(pools,source_targets))
        else:
            raise ValueError('unknown normalization')
        multiplier=total*numerator/(current_target[y]*denominator)
        outcomes.append((y,multiplier,weight/total,origin))
    return outcomes


def area_to_parameter(area, contribution, target, proposal_pdf, multiplier):
    if area <= 0:
        raise ValueError('emitter area must be positive')
    return (contribution*area,target*area,proposal_pdf*area,multiplier/area)
