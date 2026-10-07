"""Small serial graph compiler; execution-only edges never retain dead producers."""
from dataclasses import dataclass, field
import argparse
import json
from pathlib import Path


@dataclass(frozen=True)
class Version:
    resource: str
    number: int


@dataclass
class Pass:
    name: str
    reads: list = field(default_factory=list)
    writes: list = field(default_factory=list)
    side_effect: bool = False


class Graph:
    def __init__(self):
        self.passes = []
        self.producer = {}
        self.versions = {}
        self.outputs = []

    def import_resource(self, name):
        version = Version(name, 0)
        self.versions[name] = 0
        self.producer[version] = None
        return version

    def add(self, name, reads=(), writes=(), side_effect=False):
        index = len(self.passes)
        for version in reads:
            if version not in self.producer:
                raise ValueError(f"uninitialized version {version}")
        produced = []
        for resource in writes:
            number = self.versions.get(resource, -1) + 1
            self.versions[resource] = number
            version = Version(resource, number)
            self.producer[version] = index
            produced.append(version)
        self.passes.append(Pass(name, list(reads), produced, side_effect))
        return produced

    def compile(self):
        live = set()
        stack = [self.producer[v] for v in self.outputs]
        stack.extend(i for i, p in enumerate(self.passes) if p.side_effect)
        while stack:
            index = stack.pop()
            if index is None or index in live:
                continue
            live.add(index)
            stack.extend(self.producer[v] for v in self.passes[index].reads)

        # Data edges retain content. Reuse ordering edges are built AFTER culling.
        edges, last_writer, readers = set(), {}, {}
        for index in sorted(live):
            p = self.passes[index]
            for version in p.reads:
                producer = self.producer[version]
                if producer is not None and producer != index:
                    edges.add((producer, index, "RAW"))
                successors = [(v.number, writer) for v, writer in self.producer.items()
                              if writer in live and v.resource == version.resource
                              and v.number > version.number and writer != index]
                if successors:
                    _, overwrite = min(successors)
                    edges.add((index, overwrite, "WAR"))
                readers.setdefault(version.resource, set()).add(index)
            for version in p.writes:
                resource = version.resource
                for reader in readers.get(resource, set()):
                    if reader != index:
                        edges.add((reader, index, "WAR"))
                previous = last_writer.get(resource)
                if previous is not None and previous != index:
                    edges.add((previous, index, "WAW"))
                readers[resource] = set()
                last_writer[resource] = index

        dependencies = {i: set() for i in live}
        for before, after, _ in edges:
            dependencies[after].add(before)
        order = []
        while dependencies:
            ready = sorted(i for i, dep in dependencies.items() if not dep)
            if not ready:
                raise ValueError("cycle or read of a superseded resource version")
            for index in ready:
                order.append(index)
                del dependencies[index]
                for dep in dependencies.values():
                    dep.discard(index)
        position = {index: slot for slot, index in enumerate(order)}
        intervals = {}
        for index in order:
            for version in self.passes[index].reads + self.passes[index].writes:
                interval = intervals.setdefault(version.resource, [position[index], position[index]])
                interval[1] = max(interval[1], position[index])
        # Outputs survive through the frame boundary, imported resources are external.
        for version in self.outputs:
            if version.resource in intervals:
                intervals[version.resource][1] = len(order)
        return {"order": [self.passes[i].name for i in order],
                "culled": [p.name for i, p in enumerate(self.passes) if i not in live],
                "edges": [(self.passes[a].name, self.passes[b].name, kind) for a, b, kind in sorted(edges)],
                "intervals": intervals}


def compatible_alias(first, second, same_allocation_class=True):
    return same_allocation_class and (first[1] < second[0] or second[1] < first[0])


def verify():
    graph = Graph()
    scene = graph.import_resource("Scene")
    half, = graph.add("Downsample", [scene], ["Half"])
    blur, = graph.add("Blur", [half], ["Blurred"])
    output, = graph.add("Compose", [scene, blur], ["Output"])
    graph.outputs = [output]
    compiled = graph.compile()
    assert compiled["order"] == ["Downsample", "Blur", "Compose"]
    assert not compatible_alias(compiled["intervals"]["Half"], compiled["intervals"]["Blurred"])
    graph.passes[2].reads = [scene]
    stripped = graph.compile()
    assert stripped["order"] == ["Compose"]
    assert stripped["culled"] == ["Downsample", "Blur"]

    versions = Graph()
    x1, = versions.add("A", writes=["X"])
    b, = versions.add("B", [x1], ["BResult"])
    x2, = versions.add("C", writes=["X"])
    d, = versions.add("D", [x2], ["DResult"])
    versions.outputs = [b, d]
    plan = versions.compile()
    assert ("A", "B", "RAW") in plan["edges"]
    assert ("B", "C", "WAR") in plan["edges"]
    assert ("A", "C", "WAW") in plan["edges"]
    assert ("C", "D", "RAW") in plan["edges"]
    versions.outputs = [d]
    assert versions.compile()["order"] == ["C", "D"]
    # An overwritten value is not retained merely by WAW ordering.
    effects = Graph()
    effects.add("Readback", side_effect=True)
    assert effects.compile()["order"] == ["Readback"]
    try:
        effects.add("Bad", [Version("Missing", 0)])
    except ValueError:
        pass
    else:
        raise AssertionError("invalid read accepted")
    assert compatible_alias([2, 7], [8, 12])
    assert not compatible_alias([2, 7], [7, 12])
    assert not compatible_alias([2, 7], [8, 12], False)
    stale = Graph()
    old, = stale.add("WriteOld", writes=["X"])
    new, = stale.add("Overwrite", writes=["X"])
    result, = stale.add("ReadBoth", [old, new], ["Out"])
    stale.outputs = [result]
    try:
        stale.compile()
    except ValueError:
        pass
    else:
        raise AssertionError("overwritten content accepted")
    return {"passed": True, "checks": 15, "blur_plan": compiled, "culled_plan": stripped,
            "version_plan": plan, "scope": "single serial physical resource per name; no GPU barrier emission or engine integration"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "build")
    args = parser.parse_args()
    result = verify()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
