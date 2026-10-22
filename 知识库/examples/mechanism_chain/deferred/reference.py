"""CPU reference for the explicitly defined teaching contracts, not a renderer."""
import math


def _mul(matrix, vector):
    return tuple(sum(a*b for a,b in zip(row, vector)) for row in matrix)


def reconstruct(uv, depth, inverse_projection):
    h = _mul(inverse_projection, (2*uv[0]-1, 1-2*uv[1], depth, 1))
    return tuple(v/h[3] for v in h[:3])


def transform_point(matrix, point):
    return _mul(matrix, (*point, 1))[:3]


def transform_direction(matrix, direction):
    return _mul(matrix, (*direction, 0))[:3]


def shade(normal, to_light, model):
    n_len = math.sqrt(sum(x*x for x in normal))
    l_len = math.sqrt(sum(x*x for x in to_light))
    if n_len == 0 or l_len == 0:
        raise ValueError('zero direction')
    if model == 1:
        return 1.0
    if model != 0:
        raise ValueError('unknown model')
    return max(0, sum(n*l for n,l in zip(normal,to_light))/(n_len*l_len))/math.pi


def over(premultiplied, alpha, background):
    return tuple(s+(1-alpha)*d for s,d in zip(premultiplied,background))


def resolve(samples):
    return sum(samples)/len(samples)
