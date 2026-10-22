"""Python 3.11; take 1/2 stones, last mover wins; values use root perspective."""
from dataclasses import dataclass, field
from math import log, sqrt
from random import Random
@dataclass
class Node:
    stones: int
    player: int
    action: int=0
    visits: int=0
    total: float=0
    children: list=field(default_factory=list)
    def actions(self): return list(range(1,min(2,self.stones)+1))
def search(stones, iterations, seed):
    if stones<0 or iterations<1: raise ValueError('invalid search input')
    rng=Random(seed); root=Node(stones,1); trace=[]
    for _ in range(iterations):
        node=root; path=[root]
        while node.stones:
            unused=[a for a in node.actions() if a not in [c.action for c in node.children]]
            if unused:
                a=unused[0]
                child=Node(node.stones-a,-node.player,a)
                node.children.append(child); node=child; path.append(node)
                break
            node=max(node.children,key=lambda c:node.player*c.total/c.visits+sqrt(2*log(node.visits)/c.visits))
            path.append(node)
        count,player=node.stones,node.player
        while count:
            count-=rng.choice(list(range(1,min(2,count)+1)))
            player=-player
        value=-player
        for p in path: p.visits+=1; p.total+=value
        trace.append({'path':[p.action for p in path[1:]],'value':value,
                      'root':[(c.action,c.visits,c.total) for c in root.children]})
    return root,trace
if __name__=='__main__':
    r,t=search(4,120,7)
    print(t[:5]); print([(c.action,c.visits,c.total) for c in r.children])
