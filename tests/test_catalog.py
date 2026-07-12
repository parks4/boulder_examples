"""Catalog manifest integrity tests."""

from __future__ import annotations

from boulder_examples.catalog import REPO_ROOT, load_manifest, runnable_entries

EXPECTED_IDS = {
    "1D_packed_bed",
    "1D_pfr_surfchem",
    "combustor",
    "continuous_reactor",
    "custom",
    "custom2",
    "fuel_injection",
    "ic_engine",
    "mix1",
    "nanosecond_pulse_discharge",
    "non_ideal_shock_tube",
    "periodic_cstr",
    "pfr",
    "piston",
    "plasma",
    "porous_media_burner",
    "preconditioned_integration",
    "preconditioned_network",
    "reactor1",
    "reactor2",
    "sensitivity1",
    "surf_pfr",
    "surf_pfr_chain",
}


def test_manifest_covers_all_upstream_samples() -> None:
    """Assert the manifest lists exactly the 23 upstream Cantera reactor samples."""
    manifest = load_manifest()
    ids = {entry["id"] for entry in manifest["examples"]}
    assert ids == EXPECTED_IDS


def test_manifest_classifications_are_valid() -> None:
    """Assert each entry uses a supported status and required fields."""
    manifest = load_manifest()
    for entry in manifest["examples"]:
        assert entry["status"] in {"generated", "adapted", "unsupported"}
        assert entry["upstream_file"]
        assert entry["upstream_url"].startswith("https://github.com/Cantera/cantera/")
        if entry["status"] == "unsupported":
            assert entry.get("unsupported_reason"), f"missing reason for {entry['id']}"
        else:
            assert entry.get("stone_yaml"), f"missing yaml for {entry['id']}"
            assert entry.get("screenshot"), f"missing screenshot for {entry['id']}"


def test_runnable_assets_exist() -> None:
    """Assert runnable manifest entries reference existing YAML and screenshot files."""
    manifest = load_manifest()
    for entry in runnable_entries(manifest):
        yaml_path = REPO_ROOT / entry["stone_yaml"]
        screenshot_path = REPO_ROOT / entry["screenshot"]
        assert yaml_path.is_file(), f"missing YAML for {entry['id']}: {yaml_path}"
        assert screenshot_path.is_file(), f"missing screenshot for {entry['id']}: {screenshot_path}"


def test_upstream_scripts_are_vendored() -> None:
    """Assert every manifest entry has a vendored upstream Python script."""
    manifest = load_manifest()
    for entry in manifest["examples"]:
        upstream = REPO_ROOT / "upstream" / "cantera" / "reactors" / entry["upstream_file"]
        assert upstream.is_file(), f"missing upstream script: {upstream}"
