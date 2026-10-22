"""Independent CPU teaching models; Python 3.10+, standard library only."""
import bisect
import math


def draw_cdf(weights, u):
    if not weights or not math.isfinite(u) or not 0 <= u < 1:
        raise ValueError('nonempty weights and u in [0,1) required')
    if any(not math.isfinite(w) or w < 0 for w in weights):
        raise ValueError('finite nonnegative weights required')
    # Scaling avoids overflow in the cumulative sum.
    scale = max(weights)
    if scale == 0:
        return min(int(u * len(weights)), len(weights) - 1), 1 / len(weights)
    cdf, total = [], 0.0
    for w in weights:
        total += w / scale
        cdf.append(total)
    target = min(u * total, math.nextafter(total, -math.inf))
    index = bisect.bisect_right(cdf, target)
    return index, (weights[index] / scale) / total


def sh_irradiance(coefficients, direction):
    x, y, z = direction
    pi = math.pi
    # Real basis order: 00, 1-1, 10, 11, 2-2, 2-1, 20, 21, 22.
    basis = [1 / math.sqrt(4*pi), math.sqrt(3/(4*pi))*y,
             math.sqrt(3/(4*pi))*z, math.sqrt(3/(4*pi))*x,
             math.sqrt(15/(4*pi))*x*y, math.sqrt(15/(4*pi))*y*z,
             math.sqrt(5/(16*pi))*(3*z*z-1), math.sqrt(15/(4*pi))*x*z,
             math.sqrt(15/(16*pi))*(x*x-y*y)]
    kernel = [pi] + [2*pi/3]*3 + [pi/4]*5
    return sum(c*b*a for c, b, a in zip(coefficients, basis, kernel))


def gradient_noise(position, seed):
    i = math.floor(position)
    t = position - i
    def gradient(k):
        h = ((k & 0xffffffff) ^ seed) & 0xffffffff
        h = ((h ^ (h >> 16)) * 0x45d9f3b) & 0xffffffff
        h ^= h >> 16
        return 1 if h & 1 else -1
    a = gradient(i) * t
    b = gradient(i + 1) * (t - 1)
    fade = t*t*t*(t*(6*t-15)+10)
    return a + fade*(b-a)
