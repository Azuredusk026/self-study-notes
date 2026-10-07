"""CPU checks for mathematical contracts; no engine or GPU execution."""
import json
import math
import random
from pathlib import Path


def mip_bytes(width, height, bw=4, bh=4, byte_count=8):
    total = 0
    while True:
        total += ((width + bw - 1) // bw) * ((height + bh - 1) // bh) * byte_count
        if width == height == 1:
            return total
        width, height = max(1, width // 2), max(1, height // 2)


def circle_box(center, radius, lo, hi):
    closest = tuple(max(a, min(b, c)) for c, a, b in zip(center, lo, hi))
    delta = tuple(c - q for c, q in zip(center, closest))
    length = math.hypot(*delta)
    if length > radius:
        return None
    if length > 1e-12:
        return tuple(d / length for d in delta), radius - length
    faces = [(center[0] - lo[0], (-1, 0)), (hi[0] - center[0], (1, 0)),
             (center[1] - lo[1], (0, -1)), (hi[1] - center[1], (0, 1))]
    distance, normal = min(faces, key=lambda item: item[0])
    return normal, radius + distance


def slab(origin, direction, lo, hi, t_min=0.0, t_max=math.inf):
    for o, d, a, b in zip(origin, direction, lo, hi):
        if d == 0:
            if not a <= o <= b:
                return None
            continue
        near, far = sorted(((a - o) / d, (b - o) / d))
        t_min, t_max = max(t_min, near), min(t_max, far)
        if t_min > t_max:
            return None
    return t_min, t_max


def gerstner(x, z, time, k, amplitude, omega, q, direction):
    dx, dz = direction
    phase = k * (dx * x + dz * z) - omega * time
    s, c = math.sin(phase), math.cos(phase)
    position = (x + dx * q * amplitude * c, amplitude * s,
                z + dz * q * amplitude * c)
    tangent = (1 - q * k * amplitude * s * dx * dx,
               k * amplitude * c * dx, -q * k * amplitude * s * dx * dz)
    binormal = (-q * k * amplitude * s * dx * dz,
                k * amplitude * c * dz, 1 - q * k * amplitude * s * dz * dz)
    return position, tangent, binormal


def effective_samples(alpha, count):
    # First sample initializes history; subsequent samples use alpha.
    weights = [(1 - alpha) ** (count - 1)]
    weights += [alpha * (1 - alpha) ** i for i in range(count - 1)]
    return sum(weights) ** 2 / sum(w * w for w in weights)


def verify():
    checks = {}
    for w, h, expected in [(1, 1, 8), (4, 4, 24), (5, 1, 32), (1024, 1024, 699064)]:
        assert mip_bytes(w, h) == expected
    checks['block_mip_budget'] = 4
    for radius in (0.1, 0.5, 2.0):
        for center in ((0, 0), (0.8, 0), (-0.2, 0.9), (1.1, 0), (1.1, 1.1)):
            hit = circle_box(center, radius, (-1, -1), (1, 1))
            if hit:
                normal, depth = hit
                moved = tuple(c + n * (depth + 1e-8) for c, n in zip(center, normal))
                assert circle_box(moved, radius, (-1, -1), (1, 1)) is None
    checks['circle_box_resolution'] = 15
    cases = [((0, 0, 0), (1, 0, 0), (0, 1)),
             ((-1, 0, 0), (0, 1, 0), (0, 1)),
             ((-2, 0, 0), (0, 1, 0), None),
             ((2, 0, 0), (-1, 0, 0), (1, 3)),
             ((2, 0, 0), (1, 0, 0), None)]
    for origin, direction, expected in cases:
        assert slab(origin, direction, (-1, -1, -1), (1, 1, 1)) == expected
    checks['parallel_slab_and_intervals'] = len(cases)
    rng = random.Random(20261007)
    for _ in range(30):
        angle = rng.uniform(-math.pi, math.pi)
        direction = math.cos(angle), math.sin(angle)
        x, z, time = rng.random(), rng.random(), rng.random()
        args = (time, 2.0, 0.1, 1.2, 0.5, direction)
        position, tangent, binormal = gerstner(x, z, *args)
        epsilon = 1e-5
        for axis, derivative in [(0, tangent), (1, binormal)]:
            delta_x, delta_z = ((epsilon, 0) if axis == 0 else (0, epsilon))
            plus = gerstner(x + delta_x, z + delta_z, *args)[0]
            minus = gerstner(x - delta_x, z - delta_z, *args)[0]
            for a, b, analytic in zip(plus, minus, derivative):
                assert math.isclose((a-b)/(2*epsilon), analytic, rel_tol=1e-7, abs_tol=1e-7)
    checks['gerstner_analytic_derivatives'] = 30
    # Ring measure cancels the radial 1/r singularity.
    for distance in (0.001, 0.01, 0.1):
        steps = 20000
        dr = 60 * distance / steps
        integral = sum((math.exp(-((i+.5)*dr)/distance)
                       + math.exp(-((i+.5)*dr)/(3*distance))) * dr / (4*distance)
                       for i in range(steps))
        assert math.isclose(integral, 1.0, abs_tol=1e-6)
    checks['normalized_diffusion_energy'] = 3
    assert math.isclose(effective_samples(.1, 1000), 19, rel_tol=1e-12)
    table = {str(n): effective_samples(.1, n) for n in (5, 10, 15)}
    for a in (0.0, .1, 1.0, 10.0, 100.0):
        y = a/(1+a)
        assert math.isclose(y/(1-y), a, rel_tol=1e-12, abs_tol=1e-12)
    checks['temporal_weights_and_reinhard'] = 6
    frames = [b'\x00\x03abc', b'\x00\x01z', b'\x00\x00']
    wire = b''.join(frames)
    for _ in range(20):
        output, buffer = [], bytearray()
        remaining = wire
        while remaining:
            size = rng.randint(1, 5)
            buffer.extend(remaining[:size]); remaining = remaining[size:]
            while len(buffer) >= 2:
                size = int.from_bytes(buffer[:2], 'big')
                if len(buffer) < 2 + size:
                    break
                output.append(bytes(buffer[2:2+size])); del buffer[:2+size]
        assert output == [b'abc', b'z', b''] and not buffer
    checks['tcp_fragmentation'] = 20
    return {'passed': True, 'checks': checks, 'total': sum(checks.values()),
            'taa_effective_samples': table,
            'scope': 'CPU mathematical and framing models; no engine, network socket, or GPU execution'}


if __name__ == '__main__':
    result = verify()
    output = Path(__file__).parent/'build'
    output.mkdir(parents=True, exist_ok=True)
    (output/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))
