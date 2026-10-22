"""探针、阴影和面积光的 CPU 数学参考，不含场景追踪与 GPU 资源。"""
import math

def probe_weights(t):
    return [math.prod(t[axis] if (corner>>axis)&1 else 1-t[axis] for axis in range(3)) for corner in range(8)]

def box_direction(p,r,bmin,bmax,capture):
    if any(p[i]<bmin[i] or p[i]>bmax[i] for i in range(3)) or not any(r):
        return None
    distances=[]
    for i in range(3):
        if r[i]>0:distances.append((bmax[i]-p[i])/r[i])
        elif r[i]<0:distances.append((bmin[i]-p[i])/r[i])
    distance=min(distances)
    direction=tuple(p[i]+distance*r[i]-capture[i] for i in range(3))
    length=math.sqrt(sum(x*x for x in direction))
    return tuple(x/length for x in direction) if length else None

def moment_visibility(mean,second,distance):
    if distance<=mean:return 1.0
    variance=max(second-mean*mean,0)
    return variance/(variance+(distance-mean)**2)

def history_update(history,estimate,hysteresis,valid=True):
    return history*hysteresis+estimate*(1-hysteresis) if valid else estimate

def clip_horizon(vertices):
    output=[]
    if not vertices:return output
    for a,b in zip(vertices,vertices[1:]+vertices[:1]):
        ina,inb=a[2]>=0,b[2]>=0
        if ina:output.append(a)
        if ina != inb:
            t=a[2]/(a[2]-b[2])
            output.append(tuple(a[i]+t*(b[i]-a[i]) for i in range(3)))
    return output

def polygon_cosine(vertices):
    points=clip_horizon(vertices)
    if len(points)<3:return 0.0
    directions=[]
    for p in points:
        length=math.sqrt(sum(x*x for x in p))
        if length<1e-12:raise ValueError('着色点位于灯面，超出本参考的适用范围')
        directions.append(tuple(x/length for x in p))
    integral=0
    for a,b in zip(directions,directions[1:]+directions[:1]):
        c=(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
        s=math.sqrt(sum(x*x for x in c));d=max(-1,min(1,sum(x*y for x,y in zip(a,b))))
        if s<1e-10:
            if d<0:raise ValueError('相邻方向反向，灯面过近或穿过着色点')
            continue
        integral+=c[2]*math.atan2(s,d)/s
    return abs(integral)/(2*math.pi)

def pcss_radius_uv(light_full_width,blocker_distance,receiver_distance,projected_full_width):
    if blocker_distance<=0 or projected_full_width<=0:raise ValueError('距离和投影覆盖必须为正')
    penumbra_full_width=light_full_width*max(0,receiver_distance-blocker_distance)/blocker_distance
    return penumbra_full_width/(2*projected_full_width)


def blend_probe_radiance(colors, weights, global_color):
    """线性颜色的一个通道；RGB 对三个通道分别使用同一组权重。"""
    if len(colors)!=len(weights) or any(not math.isfinite(w) or w<0 for w in weights):
        raise ValueError('颜色与权重数量相等，权重有限且非负')
    total=sum(weights)
    global_weight=max(1-total,0)
    return (sum(w*c for w,c in zip(weights,colors))+global_weight*global_color)/max(total,1)
