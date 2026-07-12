#!/usr/bin/env python3
"""Run Boulder solve for every runnable example YAML (headless smoke test)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted((REPO_ROOT / "examples").glob("*.yaml"))
EXAMPLES = [p for p in EXAMPLES if p.name != "manifest.yaml"]


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


def main() -> int:
    os.environ.update(_cantera_env())
    os.environ.setdefault("MPLBACKEND", "Agg")

    from boulder.config import load_config_file, normalize_config
    from boulder.runner import BoulderRunner

    failures: list[str] = []
    for yaml_path in EXAMPLES:
        name = yaml_path.name
        try:
            cfg = normalize_config(load_config_file(str(yaml_path)))
            runner = BoulderRunner(cfg)
            runner.solve()
            print(f"OK  {name}")
        except Exception as exc:
            failures.append(f"{name}: {exc}")
            print(f"FAIL {name}: {exc}", file=sys.stderr)

    if failures:
        print("\nFailed examples:", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print(f"\nAll {len(EXAMPLES)} examples solved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
