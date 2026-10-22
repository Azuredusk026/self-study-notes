"""Scalar reference models, not an API or GPU implementation."""

def perspective(weights, clip_w, attributes):
    factors = [s / w for s, w in zip(weights, clip_w)]
    return sum(s*a for s,a in zip(factors,attributes)) / sum(factors)

def depth_pair(z, near, far, reversed_z=False):
    a = far / (far-near)
    b = -far*near / (far-near)
    raw = a+b/z
    if reversed_z:
        raw = 1-raw
    restored = b/((1-raw if reversed_z else raw)-a)
    return raw, restored

def box_outside(normal, offset, center, extents):
    distance = sum(n*c for n,c in zip(normal,center))+offset
    radius = sum(abs(n)*e for n,e in zip(normal,extents))
    return distance < -radius

def clip_history(history, lower, upper):
    if all(lo <= h <= hi for h,lo,hi in zip(history,lower,upper)):
        return history
    center = [(lo+hi)*.5 for lo,hi in zip(lower,upper)]
    extent = [(hi-lo)*.5 for lo,hi in zip(lower,upper)]
    delta = [h-c for h,c in zip(history,center)]
    ratio = max((abs(d)/e if e>0 else (float('inf') if d else 0))
                for d,e in zip(delta,extent))
    return tuple(c+d/max(1,ratio) for c,d in zip(center,delta))

def stencil_replace(old, reference, write_mask):
    return (old & (~write_mask & 255)) | (reference & write_mask)
