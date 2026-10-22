"""Python 3.11 标准库机制实验；全部数值使用正文约定。"""
import math
import os
from pathlib import Path
import sqlite3
import tempfile


def clock_sample(t0, t1, t2, t3):
    return ((t1-t0)+(t2-t3))/2, (t3-t0)-(t2-t1)


def newer(a, b):
    return 0 < ((a-b) & 65535) < 32768


def reconcile(authoritative, ack, commands, wall):
    x = authoritative
    for seq, displacement in commands:
        if newer(seq, ack):
            x = min(wall, x+displacement)
    return x


def history(samples, time):
    if not samples or time < samples[0][0] or time > samples[-1][0]:
        raise ValueError('outside history')
    for t, x in samples:
        if time == t:
            return x
    for (ta,xa),(tb,xb) in zip(samples,samples[1:]):
        if ta < time < tb:
            return xa+(xb-xa)*(time-ta)/(tb-ta)
    raise ValueError('invalid ordered history')


def ray_sphere(origin, direction, center, radius):
    m = [a-b for a,b in zip(origin,center)]
    b = sum(a*d for a,d in zip(m,direction))
    c = sum(a*a for a in m)-radius*radius
    disc = b*b-c
    if disc < 0:
        return None
    enter, leave = -b-math.sqrt(disc), -b+math.sqrt(disc)
    return max(0,enter) if leave >= 0 else None


def credit(path, account, transaction, amount, fail_before_record=False):
    # 教学账本：授权在调用层完成；业务写入和去重结果处于同一事务。
    db = sqlite3.connect(path, isolation_level=None)
    try:
        db.execute('CREATE TABLE IF NOT EXISTS balance(account TEXT PRIMARY KEY, value INTEGER)')
        db.execute('CREATE TABLE IF NOT EXISTS requests(account TEXT, id TEXT, amount INTEGER, result INTEGER, PRIMARY KEY(account,id))')
        db.execute('BEGIN IMMEDIATE')
        old = db.execute('SELECT amount,result FROM requests WHERE account=? AND id=?', (account,transaction)).fetchone()
        if old:
            if old[0] != amount:
                raise ValueError('same request ID, different payload')
            db.execute('COMMIT')
            return old[1]
        db.execute('INSERT INTO balance VALUES(?,?) ON CONFLICT(account) DO UPDATE SET value=value+excluded.value',(account,amount))
        result = db.execute('SELECT value FROM balance WHERE account=?',(account,)).fetchone()[0]
        if fail_before_record:
            raise RuntimeError('injected interruption')
        db.execute('INSERT INTO requests VALUES(?,?,?,?)',(account,transaction,amount,result))
        db.execute('COMMIT')
        return result
    except BaseException:
        if db.in_transaction:
            db.execute('ROLLBACK')
        raise
    finally:
        db.close()


def rollback(inputs, late_tick, confirmed):
    states, x = [], 0
    for u in inputs:
        states.append(x)
        x += u
    inputs = list(inputs)
    inputs[late_tick] = confirmed
    x = states[late_tick]
    events = [(i,states[i+1]) for i in range(late_tick)]
    for i in range(late_tick,len(inputs)):
        x += inputs[i]
        events.append((i,x))
    return x, events


def xpbd(x0,x1,w0,w1,rest,compliance,dt,lam):
    if dt <= 0 or min(w0,w1,compliance,rest) < 0 or x0 == x1:
        raise ValueError('invalid parameters or undefined direction')
    if w0+w1 == 0:
        return x0,x1,lam
    n = 1 if x1 > x0 else -1
    alpha = compliance/(dt*dt)
    dl = (-(abs(x1-x0)-rest)-alpha*lam)/(w0+w1+alpha)
    return x0-w0*dl*n, x1+w1*dl*n, lam+dl


def unsupported(count, edges, supports):
    graph = [set() for _ in range(count)]
    for a,b in edges:
        graph[a].add(b)
        graph[b].add(a)
    unseen, result = set(range(count)), []
    while unseen:
        todo, component = [min(unseen)], set()
        while todo:
            i = todo.pop()
            if i not in unseen:
                continue
            unseen.remove(i)
            component.add(i)
            todo.extend(graph[i] & unseen)
        if not component & supports:
            result.append(component)
    return result


def tire_limit(fx, fy, mu, load):
    magnitude = math.hypot(fx,fy)
    scale = min(1,mu*load/magnitude) if magnitude else 0
    return fx*scale, fy*scale


def slide(displacement, normal):
    into = min(0, sum(a*b for a,b in zip(displacement,normal)))
    return tuple(a-into*b for a,b in zip(displacement,normal))


def publish(path, data, fail_before_replace=False):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if fail_before_replace:
            raise RuntimeError('injected interruption')
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
