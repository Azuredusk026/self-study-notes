"""CPU reference for the explicit offline teaching pipeline, no diffusion runtime."""
from math import sqrt
def valid(q,size,current_id,history_id,expected_depth,history_depth,confidence,tolerance,cut):
    if cut: return 'cut'
    if not (0<=q[0]<size[0] and 0<=q[1]<size[1]): return 'bounds'
    if current_id!=history_id: return 'identity'
    if abs(expected_depth-history_depth)>tolerance: return 'depth'
    if confidence<.8: return 'confidence'
    return 'accept'
def latent_query(point,flow,scale):
    return tuple(p+b/scale for p,b in zip(point,flow))
def mix_normal(current,history,weight):
    v=tuple((1-weight)*c+weight*h for c,h in zip(current,history))
    length=sqrt(sum(x*x for x in v))
    return current if length<1e-6 else tuple(x/length for x in v)
def keyframe(a,b,wa,wb,conflict):
    if wa+wb<=0: raise ValueError('no anchor')
    if conflict: return a if wa>=wb else b
    return (a*wa+b*wb)/(wa+wb)
