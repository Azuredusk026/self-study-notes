"""Explicit radial damage and planar rigid-cluster teaching model, not an engine."""
import math

def damage(strengths, distances, radius, budget):
    if len(strengths)!=len(distances) or radius<=0 or budget<0:raise ValueError('invalid damage input')
    if any(not math.isfinite(x) or x<0 for x in [*strengths,*distances,radius,budget]):raise ValueError('nonfinite or negative')
    weights=[max(0,1-d/radius) if h>0 else 0 for h,d in zip(strengths,distances)]
    total=sum(weights)
    return [max(0,h-budget*w/total) if total else h for h,w in zip(strengths,weights)]

def components(count, edges, supports):
    adjacency=[[] for _ in range(count)]
    for a,b in edges:adjacency[a].append(b);adjacency[b].append(a)
    seen=set();out=[]
    for start in range(count):
        if start in seen:continue
        stack=[start];group=set()
        while stack:
            node=stack.pop()
            if node in seen:continue
            seen.add(node);group.add(node);stack.extend(adjacency[node])
        out.append((frozenset(group),bool(group&supports)))
    return out

def cluster(masses, xs, own_inertias, old_center_x, old_velocity_y, omega_z):
    if not masses or not(len(masses)==len(xs)==len(own_inertias)) or any(m<=0 for m in masses):raise ValueError('invalid cluster')
    mass=sum(masses);center=sum(m*x for m,x in zip(masses,xs))/mass
    inertia=sum(i+m*(x-center)**2 for m,x,i in zip(masses,xs,own_inertias))
    velocity=old_velocity_y+omega_z*(center-old_center_x)
    return mass,center,inertia,velocity
