"""Shared helpers for the Boulder examples catalog."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "examples" / "manifest.yaml"

# Keep in sync with scripts/build_devcontainers.py, which writes the
# per-example .devcontainer/<id>/devcontainer.json these URLs target.
GITHUB_OWNER = "parks4"
GITHUB_REPO = "boulder_examples"


def codespaces_url(example_id: str) -> str:
    """Return the codespaces.new launch URL for one example's devcontainer."""
    return (
        f"https://codespaces.new/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"?devcontainer_path=.devcontainer/{example_id}/devcontainer.json&quickstart=1"
    )


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
