"""Sequential transitions at mutex ownership points; not a C++ memory model simulator."""
from collections import deque

def predicate(closed, count):
    return closed or count > 0

class QueueModel:
    def __init__(self):
        self.jobs=deque()
        self.closed=False
    def push(self,item):
        if self.closed:return False
        self.jobs.append(item)
        return True
    def pop(self):
        if not predicate(self.closed,len(self.jobs)):return ('wait',None)
        if not self.jobs:return ('exit',None)
        return ('item',self.jobs.popleft())
    def close(self):
        self.closed=True

def publication(store,load,observed):
    """One-shot relation classifier under the article's single-writer assumptions."""
    return store=='release' and load=='acquire' and observed
