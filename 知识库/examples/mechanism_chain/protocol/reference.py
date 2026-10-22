import os
import sqlite3
import sys


class Store:
    """One SQLite durability domain for protocol arithmetic, not a server framework."""
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS entity(id INTEGER PRIMARY KEY, owner TEXT, epoch INTEGER,
            items INTEGER, last_input INTEGER, frozen INTEGER, input_session TEXT);
          INSERT OR IGNORE INTO entity VALUES(42,'A',7,3,100,0,'session-1');
          CREATE TABLE IF NOT EXISTS migration(id TEXT PRIMARY KEY, owner TEXT, epoch INTEGER,
            items INTEGER, last_input INTEGER);
          CREATE TABLE IF NOT EXISTS asset(id INTEGER PRIMARY KEY, generation INTEGER, data BLOB);
          INSERT OR IGNORE INTO asset VALUES(1,0,X'6f6c64');
          CREATE TABLE IF NOT EXISTS job(id TEXT PRIMARY KEY, expected_generation INTEGER,
            desired BLOB, published_generation INTEGER, status TEXT);
        ''')
        self.db.commit()

    def close(self):
        self.db.close()

    def switch_session(self, old, new, drained):
        # drained comes from the authoritative queue-close barrier, not the client.
        if not drained or old == new:
            return False
        with self.db:
            changed = self.db.execute('UPDATE entity SET input_session=?,last_input=0 WHERE id=42 AND input_session=? AND frozen=0', (new, old)).rowcount
        return changed == 1

    def state(self):
        return self.db.execute('SELECT owner,epoch,items,last_input FROM entity WHERE id=42').fetchone()

    def prepare(self, migration):
        with self.db:
            self.db.execute('UPDATE entity SET frozen=1 WHERE id=42')
            self.db.execute('INSERT OR IGNORE INTO migration SELECT ?,owner,epoch,items,last_input FROM entity WHERE id=42', (migration,))

    def transfer(self, old_owner, old_epoch, new_owner, migration):
        with self.db:
            cursor = self.db.execute('''UPDATE entity SET owner=?,epoch=epoch+1,frozen=0
              WHERE id=42 AND owner=? AND epoch=? AND frozen=1
              AND EXISTS(SELECT 1 FROM migration m WHERE m.id=? AND m.owner=entity.owner
              AND m.epoch=entity.epoch AND m.items=entity.items AND m.last_input=entity.last_input)''',
              (new_owner, old_owner, old_epoch, migration))
        return cursor.rowcount == 1

    def consume(self, owner, epoch, sequence, session="session-1"):
        self.db.execute('BEGIN IMMEDIATE')
        current_owner, current_epoch, items, last, frozen, active_session = self.db.execute('SELECT owner,epoch,items,last_input,frozen,input_session FROM entity WHERE id=42').fetchone()
        if (owner, epoch) != (current_owner, current_epoch) or frozen:
            result = 'fenced'
        elif session != active_session:
            result = 'session'
        elif sequence <= last:
            result = 'duplicate'
        elif sequence != last + 1:
            result = 'gap'
        else:
            self.db.execute('UPDATE entity SET items=?,last_input=? WHERE id=42', (max(0, items-1), sequence))
            result = 'applied'
        self.db.commit()
        return result

    def plan_output(self, job, data):
        with self.db:
            generation, _ = self.output()
            self.db.execute('INSERT INTO job VALUES(?,?,?,NULL,?)', (job, generation, data, 'running'))

    def output(self):
        return self.db.execute('SELECT generation,data FROM asset WHERE id=1').fetchone()

    def external_edit(self, data):
        with self.db:
            self.db.execute('UPDATE asset SET generation=generation+1,data=? WHERE id=1', (data,))

    def publish(self, job):
        self.db.execute('BEGIN IMMEDIATE')
        expected, desired = self.db.execute('SELECT expected_generation,desired FROM job WHERE id=?', (job,)).fetchone()
        changed = self.db.execute('UPDATE asset SET generation=generation+1,data=? WHERE id=1 AND generation=?', (desired, expected)).rowcount
        if changed:
            self.db.execute('UPDATE job SET published_generation=? WHERE id=?', (expected+1, job))
        self.db.commit()
        return 'published' if changed else 'conflict'

    def recover_output(self, job):
        self.db.execute('BEGIN IMMEDIATE')
        expected, desired, published, status = self.db.execute('SELECT expected_generation,desired,published_generation,status FROM job WHERE id=?', (job,)).fetchone()
        generation, actual = self.output()
        if published is not None and (generation, actual) == (published, desired):
            result = 'succeeded'
            self.db.execute('UPDATE job SET status=? WHERE id=?', (result, job))
        elif published is None and generation == expected:
            result = 'ready'
        else:
            result = 'conflict'
        self.db.commit()
        return result


class Gesture:
    def __init__(self, values):
        self.values = values
        self.active = None

    def begin(self, identity):
        if self.active is not None:
            raise ValueError('gesture already active')
        self.active = (identity, self.values[identity])

    def update(self, value):
        identity, _ = self.active
        self.values[identity] = value

    def commit(self):
        if self.active is None:
            return None
        identity, old = self.active
        self.active = None
        new = self.values[identity]
        return (identity, old, new) if old != new else None

    def cancel(self):
        identity, old = self.active
        self.values[identity] = old
        self.active = None

    def undo(self, command):
        identity, old, new = command
        if self.values[identity] != new:
            raise ValueError('undo conflict')
        self.values[identity] = old

    def redo(self, command):
        identity, old, new = command
        if self.values[identity] != old:
            raise ValueError('redo conflict')
        self.values[identity] = new


if __name__ == '__main__':
    store = Store(sys.argv[1])
    if sys.argv[2] == 'before':
        store.db.execute('BEGIN IMMEDIATE')
        store.db.execute('UPDATE entity SET items=2,last_input=101 WHERE id=42')
        os._exit(19)
    store.consume('A', 7, 101)
    os._exit(19)
