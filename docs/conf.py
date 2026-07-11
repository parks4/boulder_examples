# Configuration file for the Sphinx documentation builder.

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

project = "Boulder Examples"
author = "Erwan Pannier"
copyright = "2026, Spark Cleantech SAS"

try:
    from importlib.metadata import version as pkg_version

    release = pkg_version("boulder")
except Exception:  # pragma: no cover
    release = "unknown"
version = release

extensions = [
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_title = "Boulder Examples"

myst_enable_extensions = ["colon_fence"]
