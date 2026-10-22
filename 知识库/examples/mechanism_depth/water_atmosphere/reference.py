"""Small scalar CPU models; no GPU FFT, shader or performance claim."""
import math, cmath

def evolve(seed,t,omega):
 return {k:v*cmath.exp(1j*omega*t)+seed.get(-k,0).conjugate()*cmath.exp(-1j*omega*t) for k,v in seed.items()}
def inverse(h,n):
 return [sum(v*cmath.exp(2j*math.pi*k*x/n) for k,v in h.items()).real for x in range(n)]
def derivative(h,length,x):
 return sum(1j*2*math.pi*k/length*v*cmath.exp(2j*math.pi*k*x/length) for k,v in h.items()).real
def transmittance(extinction,distance): return math.exp(-extinction*distance)
def segment(extinction,scattering,distance,illumination):
 t=transmittance(extinction,distance)
 return (illumination*scattering*(-math.expm1(-extinction*distance))/extinction if extinction else illumination*scattering*distance,t)
def uv(r,mu,bottom,top,width,height):
 H=math.sqrt(top*top-bottom*bottom); rho=math.sqrt(max(0,r*r-bottom*bottom))
 d=-r*mu+math.sqrt(r*r*(mu*mu-1)+top*top)
 x=(d-(top-r))/(rho+H-(top-r))
 return .5/width+x*(1-1/width),.5/height+(rho/H)*(1-1/height)
def unmap(u,v,bottom,top,width,height):
 x=(u-.5/width)/(1-1/width); y=(v-.5/height)/(1-1/height)
 H=math.sqrt(top*top-bottom*bottom); rho=H*y; r=math.sqrt(rho*rho+bottom*bottom)
 d=top-r+x*(rho+H-(top-r))
 return r,1 if abs(d)<1e-12 else max(-1,min(1,(H*H-rho*rho-d*d)/(2*r*d)))
def phase(g,nu): return (1-g*g)/(4*math.pi*(1+g*g-2*g*nu)**1.5)


def optical_depth(r,mu,bottom,top,beta,scale,steps):
 if mu<0 and r*r*(mu*mu-1)+bottom*bottom>=0: return math.inf
 d=-r*mu+math.sqrt(max(0,r*r*(mu*mu-1)+top*top)); ds=d/steps
 return sum(beta*math.exp(-(math.sqrt(r*r+2*r*mu*((i+.5)*ds)+((i+.5)*ds)**2)-bottom)/scale)*ds for i in range(steps))
def build_lut(bottom,top,beta,scale,width,height,steps):
 return [[math.exp(-optical_depth(*unmap((i+.5)/width,(j+.5)/height,bottom,top,width,height),bottom,top,beta,scale,steps)) for i in range(width)] for j in range(height)]
def lookup_lut(lut,r,mu,bottom,top):
 h=len(lut); w=len(lut[0]); u,v=uv(r,mu,bottom,top,w,h)
 x=max(0,min(w-1,u*w-.5)); y=max(0,min(h-1,v*h-.5)); a=int(x); b=int(y); tx=x-a; ty=y-b
 return sum(lut[min(b+j,h-1)][min(a+i,w-1)]*((tx if i else 1-tx)*(ty if j else 1-ty)) for j in (0,1) for i in (0,1))
