"""Wheel-step reference. SI units; suspension force follows the upward travel axis."""
from math import atan2,hypot,isfinite,copysign,sqrt

def contact_geometry(distance,radius,normal_alignment,axis_dot_normal,spherical):
    factor=sqrt(max(0,1-axis_dot_normal**2))
    support=radius if spherical else radius*factor
    lever=radius*factor if spherical else radius
    return {'length':distance-support/normal_alignment,'lever':lever}

def suspension(distance,radius,rest,minimum,maximum,k,c,normal_alignment,normal_speed):
    if not all(isfinite(x) for x in (radius,rest,minimum,maximum,k,c,normal_alignment,normal_speed)):raise ValueError('nonfinite input')
    if not (radius>0 and 0<=minimum<=rest<=maximum and k>=0 and c>=0):raise ValueError('invalid suspension')
    empty={'length':maximum,'compression':0.,'spring':0.,'load':0.}
    if distance is None or normal_alignment<.2:return empty
    if not isfinite(distance) or distance<0 or normal_alignment>1:raise ValueError('invalid query')
    raw=distance-radius/normal_alignment
    if raw>maximum:return empty
    length=max(minimum,raw);compression=max(0,rest-length)
    rate=-normal_speed/normal_alignment
    spring=max(0,k*compression+c*rate+10*k*max(0,minimum-raw))
    return dict(length=length,compression=compression,spring=spring,load=spring*normal_alignment)

def tire(vx,vy,omega,radius,load,mu,c_long,c_lat,v_min=1):
    if not all(isfinite(x) for x in (vx,vy,omega,radius,load,mu,c_long,c_lat,v_min)):raise ValueError('nonfinite input')
    if radius<=0 or v_min<=0 or min(load,mu,c_long,c_lat)<0:raise ValueError('invalid tire')
    denominator=max(abs(vx),v_min)
    fx=c_long*(radius*omega-vx)/denominator
    fy=-c_lat*atan2(vy,denominator)
    norm=hypot(fx,fy);limit=mu*load
    scale=min(1,limit/norm) if norm else 1
    return fx*scale,fy*scale

def spin(omega,drive,brake,fx,radius,inertia,dt):
    if not all(isfinite(x) for x in (omega,drive,brake,fx,radius,inertia,dt)):raise ValueError('nonfinite input')
    if radius<=0 or inertia<=0 or dt<=0 or brake<0:raise ValueError('invalid wheel')
    predicted=omega+dt*(drive-fx*radius)/inertia
    return copysign(max(0,abs(predicted)-dt*brake/inertia),predicted)

def wheel_step(distance,vx,vy,omega,drive,brake,dt,mass):
    if mass<=0:raise ValueError('invalid body mass')
    s=suspension(distance,.3,.6,.2,.8,20000,2000,1,0)
    fx,fy=tire(vx,vy,omega,.3,s['load'],1,10000,10000)
    return {'load':s['load'],'fx':fx,'fy':fy,'omega':spin(omega,drive,brake,fx,.3,1,dt),'dv':fx*dt/mass}
