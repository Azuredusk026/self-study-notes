"""Python 3.10+ scalar models; no GPU, audio-device or engine implementation.

All collections are owned by the caller and used on one thread. Model units:
glyph/clip coordinates are pixels, depth is normalized [0, 1], gain is linear.
"""
from collections import deque


def ready_order(dependencies):
    """Topologically order a finite graph, rejecting cycles and missing nodes."""
    incoming = {node: len(set(deps)) for node, deps in dependencies.items()}
    consumers = {node: [] for node in dependencies}
    for node, deps in dependencies.items():
        for dep in dict.fromkeys(deps):
            if dep not in consumers:
                raise ValueError('unknown prerequisite: ' + dep)
            consumers[dep].append(node)
    ready = deque(node for node, count in incoming.items() if count == 0)
    result = []
    while ready:
        node = ready.popleft()
        result.append(node)
        for consumer in consumers[node]:
            incoming[consumer] -= 1
            if incoming[consumer] == 0:
                ready.append(consumer)
    if len(result) != len(dependencies):
        raise ValueError('dependency cycle')
    return result


def move_row(rows, index, added):
    """Move one entity to a new layout, filling its old slot with the last row."""
    destination = rows[index] | added
    rows[index] = rows[-1]
    rows.pop()
    return destination, {row['id']: i for i, row in enumerate(rows)}


def clipped(parent, child):
    """Intersect half-open pixel rectangles; None denotes no coverage."""
    rect = (max(parent[0], child[0]), max(parent[1], child[1]),
            min(parent[2], child[2]), min(parent[3], child[3]))
    return rect if rect[0] < rect[2] and rect[1] < rect[3] else None


def batch_keys(keys):
    """Merge only adjacent equal state keys, preserving translucent order."""
    groups = []
    for key in keys:
        if groups and groups[-1][0] == key:
            groups[-1] = (key, groups[-1][1] + 1)
        else:
            groups.append((key, 1))
    return groups


def glyph_quad(pen, offset, bearing, size):
    """Screen pen uses y-down; shaping offset and glyph bearing use y-up."""
    left = pen[0] + offset[0] + bearing[0]
    top = pen[1] - offset[1] - bearing[1]
    return left, top, left + size[0], top + size[1]


def mix_mono(output, samples, start_gain, end_gain):
    """Offline float model of a gain ramp; lengths equal; no output limiter."""
    count = len(output)
    return [output[i] + samples[i] * (
        end_gain if count == 1 else start_gain + (end_gain-start_gain)*i/(count-1)
    ) for i in range(count)]


def occluded(nearest, depths, reverse):
    """Depths cover the full projected bound; unknown/background stays visible."""
    return nearest < min(depths) if reverse else nearest > max(depths)


def select_cut(nodes, root, resident, threshold):
    """Tree-only coverage model. Root resident; children partition parent."""
    error, children = nodes[root]
    if error <= threshold or not children:
        return [root], []
    missing = [node for node in children if node not in resident]
    if missing:
        return [root], missing
    chosen, requests = [], []
    for node in children:
        child_chosen, child_requests = select_cut(nodes, node, resident, threshold)
        chosen.extend(child_chosen)
        requests.extend(child_requests)
    return chosen, requests
