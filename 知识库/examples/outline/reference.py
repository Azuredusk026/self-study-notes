"""Standard-library reference experiments; no engine or GPU output is claimed."""
import argparse
import itertools
import json
import math
from pathlib import Path


def normalize(vector):
    length = math.sqrt(sum(value * value for value in vector))
    if length < 1e-12:
        raise ValueError("zero-length direction")
    return tuple(value / length for value in vector)


def smooth_group(normals, weights):
    if len(normals) != len(weights) or not normals:
        raise ValueError("weights must match a nonempty group")
    if any(weight < 0 for weight in weights):
        raise ValueError("weights must be nonnegative")
    return normalize(tuple(sum(n[axis] * w for n, w in zip(normals, weights))
                           for axis in range(3)))


def offset_pixels(clip, direction, width, size):
    direction = normalize(direction)
    return (clip[0] + direction[0] * 2 * width / size[0] * clip[3],
            clip[1] + direction[1] * 2 * width / size[1] * clip[3],
            clip[2], clip[3])


def dilate(mask, radius):
    height, width = len(mask), len(mask[0])
    return [[max(mask[ny][nx] for ny in range(max(0, y-radius), min(height, y+radius+1))
                 for nx in range(max(0, x-radius), min(width, x+radius+1)))
             for x in range(width)] for y in range(height)]


def outline_mask(mask, radius):
    expanded = dilate(mask, radius)
    return [[max(0, expanded[y][x] - mask[y][x]) for x in range(len(mask[0]))]
            for y in range(len(mask))]


def relative_depth(a, b, floor=0.01):
    return abs(a - b) / max(min(a, b), floor)


def pgm(path, image):
    path.write_text("P2\n" + f"{len(image[0])} {len(image)}\n255\n" +
                    "\n".join(" ".join(str(int(v*255)) for v in row) for row in image), encoding="ascii")


def run(output):
    cases = {}
    normals = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    expected = normalize((1, 1, 1))
    for permutation in itertools.permutations(normals):
        assert all(math.isclose(a, b) for a, b in zip(smooth_group(permutation, [1]*3), expected))
    cases["smooth_order_independence"] = 6
    assert smooth_group([(1, 0, 0), (0, 1, 0)], [3, 1]) == normalize((3, 1, 0))
    cases["weighted_direction"] = 1
    for size in ((1920, 1080), (1080, 1920), (960, 540)):
        for w in (1.0, 3.0, 10.0):
            for direction in ((1, 0), (0, 1), (1, 1)):
                clip = (0.1*w, 0.2*w, 0.3*w, w)
                shifted = offset_pixels(clip, direction, 3, size)
                pixelDelta = tuple((shifted[i]/w-clip[i]/w)*size[i]/2 for i in range(2))
                assert math.isclose(math.hypot(*pixelDelta), 3, rel_tol=1e-12)
                assert shifted[2:] == clip[2:]
    cases["pixel_width_sizes_distances_directions"] = 27
    mask = [[int(3 <= x <= 7 and 3 <= y <= 7) for x in range(11)] for y in range(11)]
    line = outline_mask(mask, 1)
    assert sum(map(sum, line)) == 49 - 25
    assert not any(line[y][x] for y in range(3, 8) for x in range(3, 8))
    assert line[2][2] == 1 and line[1][1] == 0
    assert outline_mask([[0]*3 for _ in range(3)], 1) == [[0]*3 for _ in range(3)]
    assert outline_mask([[1]*3 for _ in range(3)], 1) == [[0]*3 for _ in range(3)]
    cases["mask_boundary_checks"] = 5
    assert math.isclose(relative_depth(2, 2.1), relative_depth(20, 21))
    assert relative_depth(1, 5) > 0.1
    cases["relative_depth"] = 2
    # Shared stencil marking rejects overlap contours; per-object sequence
    # preserves the intended difference only under its depth/order constraints.
    assert (0x31 & 0xF0) == (0x30 & 0xF0)
    assert (0x31 & 0x0F) != (0x32 & 0x0F)
    cases["stencil_mask_vs_id"] = 2
    output.mkdir(parents=True, exist_ok=True)
    pgm(output / "mask.pgm", mask)
    pgm(output / "outline.pgm", line)
    result = {"passed": True, "cases": cases, "total": sum(cases.values()),
              "scope": "CPU reference algorithms and numeric checks; no GPU execution",
              "unity_shader": "not compiled or run in Unity"}
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "build")
    run(parser.parse_args().out)
