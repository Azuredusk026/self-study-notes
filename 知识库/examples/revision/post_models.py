"""颜色与后处理数学参考，所有 RGB 运算均在线性 sRGB 原色下。"""
import math

def srgb_decode(x):
    return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4

def srgb_encode(x):
    return x*12.92 if x<=.0031308 else 1.055*x**(1/2.4)-.055

def premult_filter(samples,weights):
    return tuple(sum(w*c[k]*a for (c,a),w in zip(samples,weights)) for k in range(3)),sum(w*a for (_,a),w in zip(samples,weights))

def adapt_exposure(current,target,dt,tau):
    if not all(math.isfinite(x) for x in (current,target,dt,tau)):raise ValueError('曝光及时间参数需有限')
    if current<=0 or target<=0 or tau<=0 or dt<0:raise ValueError('曝光及时间常数需正，时间步长非负')
    alpha=1-math.exp(-dt/tau)
    return 2**((1-alpha)*math.log2(current)+alpha*math.log2(target))

def reexpose(history,previous_scale,current_scale):
    if not all(math.isfinite(x) for x in (history,previous_scale,current_scale)):raise ValueError('拒绝非有限曝光历史')
    if previous_scale<=0 or current_scale<=0:raise ValueError('拒绝无效曝光历史')
    return history*current_scale/previous_scale

def coc_radius(depth,focus,focal_length,f_number,sensor_width,width):
    if not all(math.isfinite(x) for x in (depth,focus,focal_length,f_number,sensor_width,width)):raise ValueError('薄透镜参数需有限')
    if depth<=0 or focal_length<=0 or focus<=focal_length or f_number<=0 or sensor_width<=0 or width<=0:raise ValueError('无效薄透镜参数')
    return focal_length**2/(2*f_number*(focus-focal_length))*(depth-focus)/depth*width/sensor_width

def ssao_weight(center_z,sample_z,scene_z,radius,bias):
    t=min(1,radius/max(abs(center_z-scene_z),radius*1e-4))
    return (1 if scene_z>=sample_z+bias else 0)*t*t*(3-2*t)

def soft_bloom(color,threshold,knee):
    if not all(math.isfinite(x) for x in (*color,threshold,knee)) or min(color)<0 or not 0<=knee<=threshold:
        raise ValueError('提取模型需要非负有限颜色且0<=knee<=threshold')
    brightness=max(color)
    if brightness<=0:return (0,0,0)
    if knee>0:
        q=max(0,min(2*knee,brightness-threshold+knee))
        soft=q*q/(4*knee)
    else:soft=0
    contribution=max(brightness-threshold,soft,0)/brightness
    return tuple(c*contribution for c in color)

def combine_scales(levels,scatter):
    result=levels[-1]
    for value in reversed(levels[:-1]):result=(1-scatter)*value+scatter*result
    return result

def luminance_reinhard(rgb):
    y=sum(c*w for c,w in zip(rgb,(.2126,.7152,.0722)))
    return tuple(c/(1+y) for c in rgb)

def motion_blur_uv(uv,backward_velocity,shutter_seconds,frame_seconds,index,count):
    """Current-image gather location for a trailing shutter and prev-current UV velocity."""
    if not all(math.isfinite(x) for x in (*uv,*backward_velocity,shutter_seconds,frame_seconds)):
        raise ValueError('采样参数需有限')
    if shutter_seconds<0 or frame_seconds<=0 or count<1 or not 0<=index<count:
        raise ValueError('无效快门或采样范围')
    if not isinstance(index,int) or not isinstance(count,int):raise ValueError('采样索引与数量需为整数')
    weight=(index+.5)/count*shutter_seconds/frame_seconds
    return tuple(u-v*weight for u,v in zip(uv,backward_velocity))
