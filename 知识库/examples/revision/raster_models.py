"""Scalar reference models, not an API or GPU implementation."""

def motion_uv(current_clip, previous_clip, top_left=True):
    """Current-minus-previous UV; finite float4 inputs with positive w, no jitter."""
    dx = .5 * (current_clip[0]/current_clip[3] - previous_clip[0]/previous_clip[3])
    dy = .5 * (current_clip[1]/current_clip[3] - previous_clip[1]/previous_clip[3])
    return dx, -dy if top_left else dy

def weighted_oit(layers, background):
    """Layers are (linear unassociated RGB, alpha in [0,1], positive weight).

    Finite inputs and a representable sum are required. Binary64 reference;
    does not simulate render-target quantization, overflow or API blending.
    """
    accum = [0.0, 0.0, 0.0]
    mass = 0.0
    revealage = 1.0
    for color, alpha, weight in layers:
        contribution = alpha * weight
        for i in range(3):
            accum[i] += color[i] * contribution
        mass += contribution
        revealage *= 1-alpha
    if mass == 0:
        return tuple(background)
    return tuple(accum[i]/mass*(1-revealage)+background[i]*revealage for i in range(3))

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
