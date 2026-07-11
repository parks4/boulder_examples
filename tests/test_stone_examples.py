"""Validate runnable STONE YAML examples through Boulder."""

from __future__ import annotations

import pytest
from boulder.config import load_config_file, normalize_config, validate_config
from boulder.validation import validate_normalized_config

from boulder_examples.catalog import REPO_ROOT, load_manifest, runnable_entries


@pytest.mark.parametrize(
    "entry",
    runnable_entries(load_manifest()),
    ids=lambda entry: entry["id"],
)
def test_stone_yaml_validates(entry: dict) -> None:
    """Each runnable manifest YAML loads, normalizes, and passes Boulder validation."""
    yaml_path = REPO_ROOT / entry["stone_yaml"]
    config = load_config_file(str(yaml_path))
    normalized = normalize_config(config)
    validate_config(normalized)
    validate_normalized_config(normalized)
