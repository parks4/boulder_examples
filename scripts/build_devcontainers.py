#!/usr/bin/env python3
"""Generate one per-example devcontainer.json under .devcontainer/<id>/.

Also regenerates the README "Launch Links" section.

Each config launches a Codespace that runs ``boulder examples/<id>.yaml
--host 0.0.0.0 --no-open`` on attach and forwards port 8050 with
onAutoForward: openBrowser, so opening the Codespaces launch link takes you
straight to that example's running Boulder GUI. All configs share the
existing root Dockerfile/environment.yml (same conda env, same dependency
set) — only the launched example and the ports label differ.

The root .devcontainer/devcontainer.json is untouched; it stays the
general-purpose/manual fallback config.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from boulder_examples.catalog import (  # noqa: E402
    codespaces_url,
    load_manifest,
    runnable_entries,
)

PORT = 8050
CONDA_ENV = "boulder"
README = REPO_ROOT / "README.md"
LAUNCH_LINKS_START = "<!-- LAUNCH_LINKS:START -->"
LAUNCH_LINKS_END = "<!-- LAUNCH_LINKS:END -->"


def _config_for(entry: dict) -> dict:
    example_id = entry["id"]
    title = entry["title"]
    return {
        "name": f"Boulder - {title}",
        "build": {
            "dockerfile": "../Dockerfile",
            "context": "../..",
        },
        "forwardPorts": [PORT],
        "postCreateCommand": (
            f"conda env update -n {CONDA_ENV} -f environment.yml --prune"
        ),
        "postAttachCommand": (
            f"conda run -n {CONDA_ENV} boulder examples/{example_id}.yaml "
            f"--host 0.0.0.0 --no-open"
        ),
        "remoteEnv": {
            "PATH": f"/opt/conda/envs/{CONDA_ENV}/bin:${{containerEnv:PATH}}"
        },
        "portsAttributes": {
            str(PORT): {
                "label": f"Boulder - {title}",
                "onAutoForward": "openBrowser",
            }
        },
        "customizations": {"vscode": {"extensions": ["ms-python.python", "charliermarsh.ruff"]}},
        "remoteUser": "vscode",
    }


def _launch_links_section(entries: list[dict]) -> str:
    lines = [LAUNCH_LINKS_START, "## Launch Links", ""]
    lines.append(
        "One-click Codespaces launches — each opens this example running in "
        "Boulder; the forwarded port opens in your browser automatically."
    )
    lines.append("")
    for entry in entries:
        lines.append(f"- [{entry['title']}]({codespaces_url(entry['id'])})")
    lines.append(LAUNCH_LINKS_END)
    return "\n".join(lines)


def _update_readme(entries: list[dict]) -> None:
    text = README.read_text(encoding="utf-8")
    section = _launch_links_section(entries)
    pattern = re.compile(
        re.escape(LAUNCH_LINKS_START) + r".*?" + re.escape(LAUNCH_LINKS_END),
        re.DOTALL,
    )
    if pattern.search(text):
        text = pattern.sub(section, text)
    else:
        text = text.rstrip("\n") + "\n\n" + section + "\n"
    README.write_text(text, encoding="utf-8")
    print(f"updated {README.relative_to(REPO_ROOT)}")


def main() -> int:
    manifest = load_manifest()
    devcontainer_dir = REPO_ROOT / ".devcontainer"
    entries = runnable_entries(manifest)
    written = []
    for entry in entries:
        example_id = entry["id"]
        out_dir = devcontainer_dir / example_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "devcontainer.json"
        out_path.write_text(
            json.dumps(_config_for(entry), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(example_id)
        print(f"wrote {out_path.relative_to(REPO_ROOT)}")
    print(f"{len(written)} per-example devcontainer configs written")
    _update_readme(entries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
