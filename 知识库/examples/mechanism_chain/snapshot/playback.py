class Playback:
    def __init__(self,r):
        self.r=r
        self.mode='playing'
        self.generation=0
        self.frozen_since=None

    def step(self,now,dt,target,samples):
        # Input: validated sorted unique timestamps of one server epoch.
        latest=samples[-1]
        if self.mode=='frozen':
            if now-self.frozen_since>=0.5 or samples[0]>self.r:
                self.mode='waiting'
            elif len(samples)>=2 and latest-self.r>=0.1:
                self.mode='playing'
                self.frozen_since=None
            return self.r
        if self.mode=='waiting':
            # A genuine left/right pair must cover the new, nondecreasing anchor.
            if len(samples)>=2 and samples[-2]>=self.r:
                self.r=min(max(target,samples[0],self.r),samples[-2])
                self.mode='playing'
                self.generation+=1
                self.frozen_since=None
            return self.r
        if samples[0]>self.r:
            self.mode='waiting'
            return self.r
        playback_target=min(target,latest-0.05)
        if abs(playback_target-self.r)>0.5:
            self.mode='waiting'
            return self.r
        rate=min(1.05,max(0.95,1+2*(playback_target-self.r)))
        candidate=self.r+rate*dt
        limit=latest+0.1
        self.r=min(candidate,limit)
        if candidate>=limit:
            self.mode='frozen'
            self.frozen_since=now
        return self.r
