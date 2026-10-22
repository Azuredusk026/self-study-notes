"""Independent CPU reference; column vectors, orthogonal basis, finite RIS domain.

Run test_reference.py with Python 3.10+. These scalar checks are not a GPU renderer.
"""
import math


def execute_plan(operations):
    """Run (precondition, atomic_apply, compensate) triples in sequence.

    An apply callback owns recovery from its own partial failure. Completed
    operations compensate in reverse order, even when a compensation fails.
    This process-local model provides no crash durability or concurrent isolation.
    """
    applied = []
    try:
        for precondition, apply, compensate in operations:
            precondition()
            apply()
            applied.append(compensate)
    except Exception as error:
        failures = []
        for compensate in reversed(applied):
            try:
                compensate()
            except Exception as compensation_error:
                failures.append(str(compensation_error))
        return False, str(error), failures
    return True, None, []


def retarget(delta, basis):
    """C D C^T for an orthogonal coordinate change C; supports 2D/3D."""
    n = len(basis)
    return tuple(tuple(sum(basis[i][a] * delta[a][b] * basis[j][b]
                           for a in range(n) for b in range(n))
                       for j in range(n)) for i in range(n))


def iris_uv(uv, view, depth):
    """View points from surface to camera; plane depth and UV use same scale."""
    if view[2] <= 1e-4:
        return None
    return tuple(uv[i] - depth * view[i] / view[2] for i in range(2))


def face_threshold(x, z):
    """Author-defined grayscale threshold; vertical light uses stored 1/4 turn."""
    if x*x + z*z < 1e-8:
        return .25
    return abs(math.atan2(x, z)) / math.pi


def ris_estimate(f, target, total, count):
    if total <= 0 or target <= 0 or count <= 0:
        return 0.
    return f * total / (count * target)


def merge_weight(target, source_weight, count):
    return target * source_weight * count
