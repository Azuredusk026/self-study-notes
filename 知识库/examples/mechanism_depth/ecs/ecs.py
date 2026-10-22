"""Single-threaded explicit byte-buffer model; no CPU timing claims."""
import ctypes
import math
import struct
from contextlib import contextmanager

P,V,H,D=1,2,4,8
FORMATS={0:'<Q',P:'<3f',V:'<3f',H:'<i',D:''}
def align(n): return (n+63)//64*64

def cache_coverage(mode,count):
    if count<0 or mode not in ('aos','soa'): raise ValueError('layout/count')
    addresses=[]
    if mode=='aos':
        addresses=[(i*64,24) for i in range(count)]
    else:
        addresses=[(base+i*12,12) for base in (0,align(count*12)) for i in range(count)]
    lines={a//64 for start,size in addresses for a in range(start,start+size)}
    return len(lines),count*24,len(lines)*64

class Layout:
    def __init__(self,mask,block_bytes=4096):
        if mask<0 or mask & ~15: raise ValueError('mask')
        self.mask=mask
        self.components=[k for k in (P,V,H,D) if mask&k]
        def build(n):
            end=64; offsets={}
            for key in [0]+self.components:
                offsets[key]=align(end)
                end=offsets[key]+n*struct.calcsize(FORMATS[key])
            return offsets,end
        capacity=0
        while build(capacity+1)[1]<=block_bytes: capacity+=1
        if not capacity: raise ValueError('block too small')
        self.capacity=capacity
        self.offsets,self.used_bytes=build(capacity)
        self.block_bytes=block_bytes

class Chunk:
    def __init__(self,layout):
        self.layout=layout;self.count=0
        self.owner=ctypes.create_string_buffer(layout.block_bytes+63)
        self.base_address=align(ctypes.addressof(self.owner))
    def address(self,key,row):
        return self.base_address+self.layout.offsets[key]+row*struct.calcsize(FORMATS[key])
    def read(self,key,row):
        fmt=FORMATS[key]
        if not fmt:return None
        values=struct.unpack(fmt,ctypes.string_at(self.address(key,row),struct.calcsize(fmt)))
        return values if key in (P,V) else values[0]
    def write(self,key,row,value):
        data=encode(key,value)
        if data:ctypes.memmove(self.address(key,row),data,len(data))
    def entity(self,row):return self.read(0,row)

def encode(key,value):
    try:
        if key==D:
            if value is not None:raise ValueError('tag payload')
            return b''
        return struct.pack(FORMATS[key],*(value if key in (P,V) else (value,)))
    except (KeyError,TypeError,struct.error,OverflowError) as exc:raise ValueError('component payload') from exc

class World:
    def __init__(self):self.groups={};self.locations={};self.query_cache={};self.iterating=0
    def _guard(self):
        if self.iterating:raise RuntimeError('structural change during iteration')
    def _validate(self,values):
        for k,v in values.items():
            if k not in (P,V,H,D):raise ValueError('component')
            encode(k,v)
    def _append(self,eid,values):
        mask=sum(values)
        if mask not in self.groups:
            self.groups[mask]=[];self.query_cache.clear()
        chunks=self.groups[mask]
        if not chunks or chunks[-1].count==chunks[-1].layout.capacity:chunks.append(Chunk(Layout(mask)))
        chunk=chunks[-1];row=chunk.count
        chunk.write(0,row,eid)
        for k,v in values.items():chunk.write(k,row,v)
        chunk.count+=1;self.locations[eid]=(chunk,row)
    def spawn(self,eid,values):
        self._guard();self._validate(values);encode(0,eid)
        if eid in self.locations:raise ValueError('duplicate entity')
        self._append(eid,values)
    def values(self,eid):
        chunk,row=self.locations[eid]
        return {k:chunk.read(k,row) for k in chunk.layout.components}
    def change(self,eid,add=None,remove=0):
        self._guard();add=add or {};self._validate(add)
        chunk,row=self.locations[eid];values=self.values(eid)
        if any(k in values for k in add):raise ValueError('already present')
        values={k:v for k,v in values.items() if not k&remove};values.update(add)
        if sum(values)==chunk.layout.mask:return
        self._append(eid,values)
        last=chunk.count-1
        if row!=last:
            for key in [0]+chunk.layout.components:chunk.write(key,row,chunk.read(key,last))
            self.locations[chunk.entity(row)]=(chunk,row)
        chunk.count-=1
    def query_chunks(self,required,excluded=0):
        query=(required,excluded)
        if query not in self.query_cache:
            self.query_cache[query]=[m for m in self.groups if m&required==required and not m&excluded]
        return [c for mask in self.query_cache[query] for c in self.groups[mask] if c.count]
    def query_ids(self,required,excluded=0):
        return [c.entity(i) for c in self.query_chunks(required,excluded) for i in range(c.count)]
    @contextmanager
    def iteration(self):
        self.iterating+=1
        try:yield
        finally:self.iterating-=1
    def integrate(self,dt):
        if not math.isfinite(dt):raise ValueError('finite dt')
        with self.iteration():
            for c in self.query_chunks(P|V,D):
                for i in range(c.count):c.write(P,i,tuple(p+v*dt for p,v in zip(c.read(P,i),c.read(V,i))))
    def check_invariants(self):
        seen={}
        for chunks in self.groups.values():
            for c in chunks:
                assert 0<=c.count<=c.layout.capacity
                for row in range(c.count):
                    eid=c.entity(row);assert eid not in seen;seen[eid]=(c,row)
        assert seen==self.locations
