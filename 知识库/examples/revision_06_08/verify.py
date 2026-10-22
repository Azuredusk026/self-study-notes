"""Run CPU references and standalone shader compilation; no GPU execution."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def locate(name):
    executable = shutil.which(name)
    if executable:
        return executable
    sdk = os.environ.get("VULKAN_SDK")
    candidates = [Path(sdk) / "Bin" / name] if sdk else []
    candidates += sorted(Path("C:/VulkanSDK").glob("*/Bin/" + name), reverse=True)
    return str(next((p for p in candidates if p.is_file()), ""))


def run(label, command):
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=60)
    return {"label": label, "command": command, "exit_code": completed.returncode,
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "stdout": completed.stdout, "stderr": completed.stderr}


def main():
    results = [run("CPU reference tests", [sys.executable, "-B", "test_reference.py"])]
    versions = {}
    with tempfile.TemporaryDirectory(prefix="kb-texture-geometry-") as temporary:
        for name, source, arguments, suffix in (
            ("glslangValidator.exe", "pom.frag", ["-V", "-S", "frag"], "spv"),
            ("dxc.exe", "domain.hlsl", ["-T", "ds_6_0", "-E", "DSMain"], "dxil"),
        ):
            executable = locate(name)
            if not executable:
                results.append({"label": source, "status": "UNVERIFIED",
                                "reason": name + " is unavailable"})
                continue
            versions[name] = run("version", [executable, "--version"])
            output = str(Path(temporary) / (source + "." + suffix))
            output_flag = "-o" if name.startswith("glslang") else "-Fo"
            result = run(source, [executable, *arguments, source, output_flag, output])
            if result["status"] == "PASS" and not Path(output).is_file():
                result.update(status="FAIL", reason="compiler produced no artifact")
            if Path(output).is_file():
                result["artifact_bytes"] = Path(output).stat().st_size
            results.append(result)
    record = {"recorded_at": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "versions": versions, "checks": results,
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(ROOT.iterdir())
                                if p.suffix in {".py", ".frag", ".hlsl"}},
              "engine_runtime": "UNVERIFIED", "gpu_capture": "UNVERIFIED",
              "visual_result": "UNVERIFIED", "performance": "UNVERIFIED"}
    (ROOT / "results.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8", newline="\n")
    for result in results:
        print(result["label"] + ": " + result["status"])
    return int(any(result["status"] == "FAIL" for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
