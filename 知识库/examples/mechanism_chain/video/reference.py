"""Independent CPU arithmetic for the video article; not a diffusion model."""
from math import exp, log, sqrt
from statistics import median

def sample_history(colors, weights, confidence):
    if any(w>0 and q<.8 for w,q in zip(weights,confidence)):
        return None
    return sum(c*w for c,w in zip(colors,weights))

def apply_gain(output, gain, mask):
    return [p*(1+m*(gain-1)) for p,m in zip(output,mask)]

def next_confidence(content_valid, history_accepted, candidate):
    return [v*(q if m else 1) for v,m,q in zip(content_valid,history_accepted,candidate)]


def exposure_gain(target, output, eligible, previous):
    ratios = [log(a/b) for a,b,m in zip(target,output,eligible) if m and a>.01 and b>.01]
    if not ratios:
        return previous
    candidate = min(1.25, max(.8, exp(median(ratios))))
    return min(previous*1.05, max(previous/1.05, candidate))


def project_clean(current, history, mask, weight):
    return [p*(1-weight*m)+h*weight*m for p,h,m in zip(current,history,mask)]


def ddim_update(clean, noise, alpha_next):
    return sqrt(alpha_next)*clean + sqrt(1-alpha_next)*noise


def choose_steps(timesteps, strength):
    count = int(len(timesteps)*strength)
    if not 0 < strength <= 1 or count < 1:
        raise ValueError('strength must retain at least one step')
    return timesteps[len(timesteps)-count:]


def history_state(previous_q, previous_anchor, confidence, accepted, content_valid, approved=False):
    if not content_valid:
        return (0, 0)
    if approved:
        return (1, 1)
    if not accepted:
        return (1, 0)
    return (previous_q*confidence,previous_anchor*confidence)

def anchor_weights(left_distance,right_distance,left_anchor,right_anchor):
    span = left_distance+right_distance
    if span <= 0:
        raise ValueError('keyframe interval must have positive length')
    left = right_distance/span*left_anchor if left_anchor >= .8 else 0
    right = left_distance/span*right_anchor if right_anchor >= .8 else 0
    total = left+right
    return (left/total,right/total) if total > 0 else None
