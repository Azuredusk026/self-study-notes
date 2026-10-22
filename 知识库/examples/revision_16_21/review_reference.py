"""正文帧分配器的整数模型；不分配真实存储，不测量性能。"""
def arena_allocate(cursor, size, alignment, capacity, maximum=(1 << 64)-1):
    if not 0 <= cursor <= capacity <= maximum or not 0 <= size <= maximum:
        raise ValueError('invalid unsigned range')
    if alignment <= 0 or alignment > maximum or alignment & (alignment-1):
        raise ValueError('alignment must be a representable power of two')
    if cursor > maximum-(alignment-1):
        raise OverflowError('alignment addition would wrap')
    offset = (cursor+alignment-1) & ~(alignment-1)
    if offset > capacity or size > capacity-offset:
        raise MemoryError('capacity exceeded')
    return offset, offset+size


def accept_snapshot(current_tick, current_ack, incoming_tick, incoming_ack):
    """同一会话纪元；Tick已展开，16位ACK的有效窗口小于半空间。"""
    difference = (incoming_ack-current_ack) & 65535
    return incoming_tick > current_tick and (difference == 0 or difference < 32768)


def uct_select(children, parent_visits, exploration, player_sign):
    """children项为访问数、根玩家累计收益；仅双人零和决策节点。"""
    import math
    if not children or parent_visits <= 0 or player_sign not in (-1,1) or exploration < 0:
        raise ValueError('invalid UCT state')
    best, score = None, -math.inf
    for i, (visits,value) in enumerate(children):
        if visits == 0:
            return i
        candidate = player_sign*value/visits + exploration*math.sqrt(math.log(parent_visits)/visits)
        if candidate > score:
            best, score = i,candidate
    return best


def goap_plan(start, goal, actions, max_expansions=1000):
    """有限键值状态的回归搜索；actions=(名称,前提字典,赋值效果字典,非负成本)。"""
    import heapq
    import itertools
    import math
    if any(not math.isfinite(a[3]) or a[3] < 0 for a in actions):
        raise ValueError('nonnegative finite action costs required')
    key = lambda facts: tuple(sorted(facts.items()))
    serial = itertools.count()
    best = {key(goal):0}
    pending = [(0,next(serial),dict(goal),[])]
    expanded = 0
    while pending:
        cost,_,required,reverse_actions = heapq.heappop(pending)
        if cost != best[key(required)]:
            continue
        if all(k in start and start[k] == v for k,v in required.items()):
            return list(reversed(reverse_actions))
        expanded += 1
        if expanded > max_expansions:
            raise RuntimeError('search budget exhausted')
        for name,preconditions,effects,action_cost in actions:
            if not any(k in required and required[k] == v for k,v in effects.items()):
                continue
            if any(k in required and required[k] != v for k,v in effects.items()):
                continue
            remaining = {k:v for k,v in required.items() if k not in effects}
            if any(k in remaining and remaining[k] != v for k,v in preconditions.items()):
                continue
            remaining.update(preconditions)
            next_cost = cost+action_cost
            if next_cost >= best.get(key(remaining),math.inf):
                continue
            best[key(remaining)] = next_cost
            heapq.heappush(pending,(next_cost,next(serial),remaining,reverse_actions+[name]))
    return None
