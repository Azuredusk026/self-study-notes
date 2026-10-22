"""Artist-defined angle-field model, not a spatial distance transform."""
import math

def bake(angles, lit):
 if len(angles)!=len(lit) or len(angles)<2 or angles[0]!=0 or angles[-1]!=1:
  raise ValueError('need ordered endpoints')
 if any(b<=a for a,b in zip(angles,angles[1:])) or any(v not in (0,1) for v in lit):
  raise ValueError('invalid samples')
 if any(b>a for a,b in zip(lit,lit[1:])):raise ValueError('dark-to-lit reentry')
 if all(lit):return 1.0,0.0
 if not any(lit):return 0.0,0.0
 last=lit.index(0)-1
 return (angles[last]+angles[last+1])/2,angles[last+1]-angles[last]

def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)

def evaluate(light, fields, vertical, transition):
 length=math.sqrt(sum(v*v for v in light))
 if not length or transition<=0:raise ValueError('nonzero light and positive transition')
 x,y,z=(v/length for v in light);h=math.hypot(x,z)
 t=abs(math.atan2(x,z))/math.pi if h>1e-8 else vertical
 d=fields[0] if x<0 else fields[1]
 angular=smooth(t-.01,t+.01,d)
 vertical_lit=smooth(vertical-.01,vertical+.01,(fields[0]+fields[1])/2)
 w=smooth(0,transition,h)
 return vertical_lit*(1-w)+angular*w
