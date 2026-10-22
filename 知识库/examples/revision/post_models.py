"""颜色与后处理数学参考，所有 RGB 运算均在线性 sRGB 原色下。"""
import math

def srgb_decode(x):
    return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4

def srgb_encode(x):
    return x*12.92 if x<=.0031308 else 1.055*x**(1/2.4)-.055

def premult_filter(samples,weights):
    return tuple(sum(w*c[k]*a for (c,a),w in zip(samples,weights)) for k in range(3)),sum(w*a for (_,a),w in zip(samples,weights))

def adapt_exposure(current,target,dt,tau):
    if current<=0 or target<=0 or tau<=0 or dt<0:raise ValueError('曝光及时间常数需正，时间步长非负')
    alpha=1-math.exp(-dt/tau)
    return 2**((1-alpha)*math.log2(current)+alpha*math.log2(target))

def reexpose(history,previous_scale,current_scale):
    if previous_scale<=0 or current_scale<=0:raise ValueError('拒绝无效曝光历史')
    return history*current_scale/previous_scale

def coc_radius(depth,focus,focal_length,f_number,sensor_width,width):
    if depth<=0 or focus<=focal_length or f_number<=0 or sensor_width<=0:raise ValueError('无效薄透镜参数')
    return focal_length**2/(2*f_number*(focus-focal_length))*(depth-focus)/depth*width/sensor_width

def ssao_weight(center_z,sample_z,scene_z,radius,bias):
    t=min(1,radius/max(abs(center_z-scene_z),1e-4))
    return (1 if scene_z>=sample_z+bias else 0)*t*t*(3-2*t)

def soft_bloom(color,threshold,knee):
    brightness=max(color)
    if knee>0:
        q=max(0,min(2*knee,brightness-threshold+knee))
        soft=q*q/(4*knee)
    else:soft=0
    contribution=max(brightness-threshold,soft,0)/max(brightness,1e-6)
    return tuple(c*contribution for c in color)

def combine_scales(levels,scatter):
    result=levels[-1]
    for value in reversed(levels[:-1]):result=(1-scatter)*value+scatter*result
    return result

def luminance_reinhard(rgb):
    y=sum(c*w for c,w in zip(rgb,(.2126,.7152,.0722)))
    return tuple(c/(1+y) for c in rgb)
