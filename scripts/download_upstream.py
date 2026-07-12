#!/usr/bin/env python3
"""Download vendored Cantera reactor samples at a pinned upstream commit."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_DIR = REPO_ROOT / "upstream" / "cantera" / "reactors"
API_URL = "https://api.github.com/repos/Cantera/cantera/contents/samples/python/reactors?ref=main"


def main() -> int:
    """Fetch all upstream ``.py`` samples into ``upstream/cantera/reactors``."""
    UPSTREAM_DIR.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(API_URL) as response:
        payload = json.load(response)
    for item in payload:
        name = item["name"]
        if not name.endswith(".py"):
            continue
        target = UPSTREAM_DIR / name
        with urllib.request.urlopen(item["download_url"]) as response:
            target.write_bytes(response.read())
        print(f"downloaded {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
