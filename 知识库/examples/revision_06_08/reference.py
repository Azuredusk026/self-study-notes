"""CPU scalar teaching models. No GPU execution, engine integration or timings.

Inputs are finite and satisfy each article's dimensions/space/range contract.
"""
import math


def texture_lod(dx, dy, size):
    rho=max(math.hypot(dx[0]*size[0],dx[1]*size[1]),
            math.hypot(dy[0]*size[0],dy[1]*size[1]))
    return math.log2(max(rho,1e-12))

def bilinear(pixels, uv):
    h,w=len(pixels),len(pixels[0])
    x,y=uv[0]*w-.5,uv[1]*h-.5
    ix,iy=math.floor(x),math.floor(y)
    fx,fy=x-ix,y-iy
    fetch=lambda x,y:pixels[min(h-1,max(0,y))][min(w-1,max(0,x))]
    return ((1-fy)*((1-fx)*fetch(ix,iy)+fx*fetch(ix+1,iy))
            +fy*((1-fx)*fetch(ix,iy+1)+fx*fetch(ix+1,iy+1)))

def mip_bytes(w,h,bw,bh,byte_count):
    result=[]
    while True:
        result.append(((w+bw-1)//bw)*((h+bh-1)//bh)*byte_count)
        if w==h==1: return result
        w,h=max(1,w//2),max(1,h//2)

def stream_targets(level_bytes,desired,priorities,budget):
    """Priority-first target residency; output index is finest allowed mip.

    Only plans targets. Upload/read fences and temporary memory are external.
    """
    targets=[len(levels)-1 for levels in level_bytes]
    used=sum(levels[-1] for levels in level_bytes)
    if used>budget: raise ValueError('mandatory fallback exceeds budget')
    order=sorted(range(len(targets)),key=lambda i:(-priorities[i],i))
    for i in order:
        while targets[i]>desired[i]:
            added=level_bytes[i][targets[i]-1]
            if used+added>budget: break
            targets[i]-=1; used+=added
    return targets

def vt_address(uv,mip,base_pages,page_size,border,cache_size,resident):
    """Page grid down to its one-page root; smaller mip-tail images are external.

    Integer base_pages and mip, 0<=uv<1; physical slot includes borders.
    """
    if base_pages<=0 or base_pages & (base_pages-1):
        raise ValueError('base page count must be a positive power of two')
    root_mip=base_pages.bit_length()-1
    if not 0<=mip<=root_mip:
        raise ValueError('mip range ends at the one-page root; tail not modeled')
    n=base_pages>>mip
    wanted=(mip,math.floor(uv[0]*n),math.floor(uv[1]*n))
    for level in range(mip,root_mip+1):
        n=base_pages>>level
        x,y=math.floor(uv[0]*n),math.floor(uv[1]*n)
        key=(level,x,y)
        if key in resident:
            slot=resident[key]; stride=page_size+2*border
            local=(uv[0]*n-x,uv[1]*n-y)
            physical=tuple((slot[i]*stride+border+local[i]*page_size)/cache_size[i] for i in range(2))
            return wanted,key,physical
    raise ValueError('resident ancestor required')

def pom_line(u,ray_uv,layers,depth):
    """1D section of POM. depth(u) in [0,1], bounded positive integer layers."""
    previous_u,previous_t=u,0.
    previous_error=depth(u)
    if previous_error<=0: return u,0.
    for i in range(1,layers+1):
        t=i/layers; current_u=u-ray_uv*t
        error=depth(current_u)-t
        if error<=0:
            weight=previous_error/(previous_error-error)
            return (previous_u+(current_u-previous_u)*weight,
                    previous_t+(t-previous_t)*weight)
        previous_u,previous_t,previous_error=current_u,t,error
    return u-ray_uv,1.

def select_lod(screen_fraction,current,thresholds,hysteresis):
    while current<len(thresholds) and screen_fraction<thresholds[current]-hysteresis: current+=1
    while current>0 and screen_fraction>thresholds[current-1]+hysteresis: current-=1
    return current

def normalize(v):
    length=math.sqrt(sum(x*x for x in v))
    if length==0: raise ValueError('nonzero direction required')
    return tuple(x/length for x in v)

def height_normal(left,right,down,up,spacing_x,spacing_z):
    return normalize((-(right-left)/(2*spacing_x),1.,-(up-down)/(2*spacing_z)))

def billboard_right(toward,up,fallback):
    dot=sum(a*b for a,b in zip(toward,up))
    f=tuple(toward[i]-up[i]*dot for i in range(3))
    if sum(x*x for x in f)>1e-8:
        return normalize((up[1]*f[2]-up[2]*f[1],up[2]*f[0]-up[0]*f[2],up[0]*f[1]-up[1]*f[0]))
    d=sum(a*b for a,b in zip(fallback,up))
    return normalize(tuple(fallback[i]-up[i]*d for i in range(3)))

def flatten_corners(corners):
    """Hashable complete exported vertex records; exact equality only."""
    lookup={}; vertices=[]; indices=[]
    for corner in corners:
        if corner not in lookup:
            lookup[corner]=len(vertices); vertices.append(corner)
        indices.append(lookup[corner])
    return vertices,indices

def cache_misses(indices,capacity):
    """LRU model; real hardware cache is not prescribed by this model."""
    cache=[]; misses=0
    for index in indices:
        if index in cache: cache.remove(index)
        else: misses+=1
        cache.insert(0,index)
        del cache[capacity:]
    return misses

def quadric_error(point,planes):
    """Normalized planes (nx,ny,nz,d), squared world-length error."""
    return sum((sum(n*x for n,x in zip(plane[:3],point))+plane[3])**2 for plane in planes)

def phong_point(points,normals,bary,strength):
    """Unit normals, affine barycentric coordinates; strength in [0,1]."""
    linear=tuple(sum(bary[j]*points[j][i] for j in range(3)) for i in range(3))
    projected=[]
    for p,n in zip(points,normals):
        distance=sum((linear[i]-p[i])*n[i] for i in range(3))
        projected.append(tuple(linear[i]-distance*n[i] for i in range(3)))
    curved=tuple(sum(bary[j]*projected[j][i] for j in range(3)) for i in range(3))
    return tuple((1-strength)*linear[i]+strength*curved[i] for i in range(3))

def ellipsoid_normal(point,center,radii):
    v=tuple((point[i]-center[i])/radii[i]**2 for i in range(3))
    return normalize(v) if any(v) else (0,1,0)

def smooth_step(points,neighbours,factor,fixed=()):
    result=[]
    for i,p in enumerate(points):
        adjacent=neighbours[i]
        if i in fixed or not adjacent: result.append(p); continue
        average=tuple(sum(points[j][k] for j in adjacent)/len(adjacent) for k in range(3))
        result.append(tuple(p[k]+factor*(average[k]-p[k]) for k in range(3)))
    return result
