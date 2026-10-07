"""Validate an R8_UNORM byte packing model using point reads, not filtering."""
import math
import argparse
import json
from pathlib import Path


def pack(value, identifier):
    q = math.floor(max(0, min(value, 1)) * 31 + 0.5)
    return ((identifier & 7) * 32 + q) / 255


def unpack(packed):
    byte = math.floor(max(0, min(packed, 1)) * 255 + 0.5)
    return byte // 32, (byte % 32) / 31


def verify():
    cases = 0
    for identifier in range(8):
        for q in range(32):
            result, value = unpack(pack(q / 31, identifier))
            assert result == identifier and math.isclose(value, q / 31)
            cases += 1
    for value in (-1, 0, 0.2, 0.5, 0.9, 1, 2):
        identifier, decoded = unpack(pack(value, 3))
        assert identifier == 3
        assert abs(decoded - max(0, min(value, 1))) <= 0.5 / 31 + 1e-12
        cases += 1
    # Linear averaging IDs does not preserve a meaningful discrete category.
    midpoint = (pack(0, 0) + pack(0, 6)) / 2
    assert unpack(midpoint)[0] == 3
    return {"passed": True, "cases": cases + 1, "scope": "R8_UNORM CPU round trip; GPU/half precision and filtering not validated"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "build")
    args = parser.parse_args()
    result = verify()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
