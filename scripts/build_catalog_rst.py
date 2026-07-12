"""Generate docs/catalog.rst from examples/manifest.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "examples" / "manifest.yaml"
OUTPUT = REPO_ROOT / "docs" / "catalog.rst"


def main() -> int:
    """Write the Sphinx catalog page."""
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    lines = [
        "Example catalog",
        "===============",
        "",
        f"Pinned upstream: ``{manifest['upstream']['repository']}`` "
        f"``{manifest['upstream']['path']}`` @ ``{manifest['upstream']['ref']}``.",
        "",
        "See :doc:`boulder:stone` for the STONE YAML format and "
        ":doc:`boulder:cantera_upstream_examples` for solver mapping from upstream "
        "Cantera scripts. Networks are simulated with :class:`cantera.ReactorNet`.",
        "",
    ]
    for entry in manifest["examples"]:
        lines.append(entry["title"])
        lines.append("-" * len(entry["title"]))
        lines.append("")
        lines.append(f":Upstream: `{entry['upstream_url']}`")
        lines.append(f":Status: **{entry['status']}**")
        if entry["status"] == "unsupported":
            lines.append(f":Reason: {entry['unsupported_reason']}")
            lines.append("")
            continue
        lines.append(f":STONE: ``{entry['stone_yaml']}``")
        lines.append(f":Mechanism: ``{entry.get('mechanism', '')}``")
        if entry.get("notes"):
            lines.append("")
            lines.append(entry["notes"])
        lines.append("")
        rel = entry["screenshot"].replace("docs/", "")
        lines.append(f".. image:: /{rel}")
        lines.append("   :width: 100%")
        lines.append("")
        lines.append("Codespaces launch:")
        lines.append("")
        lines.append(".. code-block:: bash")
        lines.append("")
        lines.append(f"   boulder {entry['stone_yaml']} --no-open")
        lines.append("")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
