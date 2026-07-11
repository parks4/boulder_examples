"""Headless CLI download and execution tests for runnable examples."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from boulder_examples.catalog import REPO_ROOT, load_manifest, runnable_entries


def _subprocess_env() -> dict[str, str]:
    """Return subprocess env with Cantera data directories on CANTERA_DATA."""
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


_SKIP_DOWNLOAD: set[str] = {
    # Known hard cases in upstream Boulder CI as well.
    "combustor",
    "nanosecond_pulse_discharge",
    # Headless codegen/solve limitations with multi-mechanism or real-gas phases.
    "mix1",
    "fuel_injection",
}


@pytest.mark.integration
@pytest.mark.parametrize(
    "entry",
    runnable_entries(load_manifest()),
    ids=lambda entry: entry["id"],
)
def test_headless_downloaded_python_executes(entry: dict) -> None:
    """Boulder headless --download emits Python that runs without error for each example.

    Asserts:
    - ``boulder <yaml> --headless --download`` exits 0
    - the downloaded script exists
    - executing the downloaded script exits 0
    """
    if entry["id"] in _SKIP_DOWNLOAD:
        pytest.skip(f"known upstream limitation for {entry['id']}")

    if entry["id"] == "nanosecond_pulse_discharge":
        import cantera as ct

        mech = entry.get("mechanism", "")
        try:
            ct.Solution(mech)
        except (OSError, ValueError, RuntimeError) as exc:
            pytest.skip(f"plasma mechanism unavailable: {exc}")

    yaml_path = REPO_ROOT / entry["stone_yaml"]
    with tempfile.TemporaryDirectory() as tmp:
        out_py = Path(tmp) / f"{entry['id']}.py"
        cmd = [
            sys.executable,
            "-m",
            "boulder.cli",
            str(yaml_path),
            "--headless",
            "--download",
            str(out_py),
        ]
        env = _subprocess_env()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            env=env,
        )
        assert result.returncode == 0, result.stderr
        assert out_py.is_file()

        exec_result = subprocess.run(
            [sys.executable, str(out_py)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            env=env,
        )
        assert exec_result.returncode == 0, exec_result.stderr
