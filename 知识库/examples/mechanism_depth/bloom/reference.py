"""Scalar linear image reference; normalized coordinates, clamp boundary."""
from math import floor

def down2(src):
    h,w=len(src),len(src[0])
    if h%2 or w%2: raise ValueError("even dimensions required")
    return [[sum(src[2*y+j][2*x+i] for j in range(2) for i in range(2))/4
             for x in range(w//2)] for y in range(h//2)]

def bilinear(src,x,y):
    h,w=len(src),len(src[0]); ix,iy=floor(x),floor(y); fx,fy=x-ix,y-iy
    def at(a,b): return src[max(0,min(h-1,b))][max(0,min(w-1,a))]
    return sum(at(ix+i,iy+j)*(fx if i else 1-fx)*(fy if j else 1-fy)
               for j in range(2) for i in range(2))

def tent_up(src,w,h):
    sh,sw=len(src),len(src[0]); weights=[.25,.5,.25]
    return [[sum(weights[i+1]*weights[j+1]*bilinear(src,(x+.5)*sw/w-.5+i,(y+.5)*sh/h-.5+j)
                 for j in range(-1,2) for i in range(-1,2))
             for x in range(w)] for y in range(h)]

def pyramid(src,levels,scatter):
    if not 0<=scatter<=1: raise ValueError("scatter outside [0,1]")
    layers=[src]
    for _ in range(levels): layers.append(down2(layers[-1]))
    result=layers[-1]
    for layer in reversed(layers[:-1]):
        up=tent_up(result,len(layer[0]),len(layer))
        result=[[(1-scatter)*a+scatter*b for a,b in zip(row,ur)] for row,ur in zip(layer,up)]
    return result
