"""Shared helpers for the Boulder examples catalog."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "examples" / "manifest.yaml"


def load_manifest() -> dict[str, Any]:
    """Load and return the catalog manifest."""
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def runnable_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Return manifest entries that have a STONE YAML path."""
    return [entry for entry in manifest["examples"] if entry.get("stone_yaml")]


def unsupported_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Return manifest entries marked unsupported."""
    return [entry for entry in manifest["examples"] if entry["status"] == "unsupported"]
