"""CPU references for scan indexing and readback publication ordering."""
def blocked_scan(values, block_size=64):
    if block_size < 1 or block_size & (block_size-1):
        raise ValueError('power-of-two block size required')
    output=[]
    base=0
    for begin in range(0,len(values),block_size):
        count=min(block_size,len(values)-begin)
        scratch=list(values[begin:begin+count])+[0]*(block_size-count)
        step=1
        while step<block_size:
            for i in range(2*step-1,block_size,2*step):
                scratch[i]+=scratch[i-step]
            step*=2
        total=scratch[-1];scratch[-1]=0
        step=block_size//2
        while step:
            for i in range(2*step-1,block_size,2*step):
                left=scratch[i-step]
                scratch[i-step]=scratch[i]
                scratch[i]+=left
            step//=2
        output.extend(base+x for x in scratch[:count])
        base+=total
    return output,base

class ReadbackModel:
    def __init__(self, capacity):
        self.capacity=capacity
        self.pending={}
        self.epoch=0
        self.latest=None
    def submit(self, sequence):
        if sequence in self.pending: raise ValueError('sequence reused')
        if len(self.pending)>=self.capacity: return False
        self.pending[sequence]=self.epoch
        return True
    def complete(self, sequence, value, error=False):
        epoch=self.pending.pop(sequence)
        if not error and epoch==self.epoch and (self.latest is None or sequence>self.latest[0]):
            self.latest=(sequence,value)
    def invalidate(self):
        self.epoch+=1
        self.latest=None


def blocked_minmax(values):
    """64 个元素一组的树形归约；空输入由宿主直接返回，无需调度。"""
    if not values:
        return None
    group_results=[]
    for begin in range(0,len(values),64):
        group=values[begin:begin+64]
        minima=list(group)+[float('inf')]*(64-len(group))
        maxima=list(group)+[float('-inf')]*(64-len(group))
        offset=32
        while offset:
            for lane in range(offset):
                minima[lane]=min(minima[lane],minima[lane+offset])
                maxima[lane]=max(maxima[lane],maxima[lane+offset])
            offset//=2
        group_results.append((minima[0],maxima[0]))
    return min(p[0] for p in group_results),max(p[1] for p in group_results)
