#!/usr/bin/env python3
"""Capture post-solve Boulder GUI screenshots for runnable catalog examples."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from boulder_examples.catalog import REPO_ROOT as ROOT
from boulder_examples.catalog import load_manifest, runnable_entries

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:  # pragma: no cover
    raise SystemExit("playwright is required: pip install playwright && playwright install chromium") from exc


def _wait_for_health(port: int, timeout_s: float = 120.0) -> None:
    import urllib.error
    import urllib.request

    deadline = time.time() + timeout_s
    url = f"http://127.0.0.1:{port}/api/health"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.5)
    raise RuntimeError(f"Boulder server did not become healthy at {url}")


def _subprocess_env() -> dict[str, str]:
    import os

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


def _capture_one(yaml_path: Path, output_png: Path, port: int) -> None:
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "boulder.cli",
            str(yaml_path),
            "--no-open",
            "--no-port-search",
            "--port",
            str(port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=_subprocess_env(),
    )
    try:
        _wait_for_health(port=port)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(f"http://127.0.0.1:{port}/")
            page.get_by_role("button", name="Run Simulation").click()
            page.locator("#simulation-overlay").wait_for(state="hidden", timeout=600_000)
            page.locator("#simulation-results-card").wait_for(timeout=600_000)
            plots = page.get_by_role("button", name="Plots")
            if plots.get_attribute("data-active") != "true":
                plots.click()
            time.sleep(1.0)
            output_png.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(output_png), full_page=True)
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.kill()


def main() -> int:
    """Capture screenshots for all runnable manifest entries."""
    manifest = load_manifest()
    failures = 0
    for index, entry in enumerate(runnable_entries(manifest)):
        yaml_path = ROOT / entry["stone_yaml"]
        output_png = ROOT / entry["screenshot"]
        port = 8050 + index
        print(f"screenshot {entry['id']} -> {output_png} (port {port})")
        try:
            _capture_one(yaml_path, output_png, port=port)
        except Exception as exc:
            failures += 1
            print(f"screenshot failed for {entry['id']}: {exc}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
