#!/usr/bin/env python3
"""Verify each example YAML via the Boulder HTTP API (same path as the GUI)."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted(p for p in (REPO_ROOT / "examples").glob("*.yaml") if p.name != "manifest.yaml")
BASE = "http://127.0.0.1:8050"


def _cantera_env() -> dict[str, str]:
    import cantera as ct

    base = Path(ct.__file__).resolve().parent / "data"
    example = base / "example_data"
    parts: list[str] = []
    if example.is_dir():
        parts.append(str(example))
    parts.append(str(base))
    prev = os.environ.get("CANTERA_DATA", "").strip()
    if prev:
        parts.append(prev)
    return {**os.environ, "CANTERA_DATA": os.pathsep.join(parts)}


def _post_json(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read())


def _stream_to_completion(sim_id: str, timeout_s: float = 300.0) -> dict:
    url = f"{BASE}/api/simulations/{sim_id}/stream"
    event = None
    deadline = time.time() + timeout_s
    with urllib.request.urlopen(url, timeout=timeout_s) as resp:
        while time.time() < deadline:
            line = resp.readline().decode("utf-8", errors="replace").strip()
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:") and event in ("complete", "error"):
                return {"event": event, "data": json.loads(line[5:])}
    raise TimeoutError(f"stream timed out for {sim_id}")


def _simulate_yaml(path: Path) -> None:
    from boulder.config import load_config_file, normalize_config

    normalized = normalize_config(load_config_file(str(path)))
    sim_id = _post_json(f"{BASE}/api/simulations", {"config": normalized})["simulation_id"]
    result = _stream_to_completion(sim_id)
    if result["event"] == "error":
        msg = result["data"].get("error_message") or result["data"]
        raise RuntimeError(str(msg))


def main() -> int:
    os.environ.update(_cantera_env())
    try:
        _get_json(f"{BASE}/api/health")
    except urllib.error.URLError as exc:
        print(f"Boulder API not reachable at {BASE}: {exc}", file=sys.stderr)
        return 1

    failures: list[str] = []
    for path in EXAMPLES:
        try:
            _simulate_yaml(path)
            print(f"OK  {path.name}")
        except Exception as exc:
            failures.append(f"{path.name}: {exc}")
            print(f"FAIL {path.name}: {exc}", file=sys.stderr)

    if failures:
        print("\nFailed:", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print(f"\nAll {len(EXAMPLES)} examples completed via API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
