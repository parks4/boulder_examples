# AGENTS.md — Boulder Examples contributor and agent guide

This file is for human contributors and AI coding agents working on **Boulder Examples**
(the example catalog derived from Cantera's Python reactor samples, for
[Boulder](https://github.com/parks4/boulder)).

## Project layout

| Area | Path |
|------|------|
| Vendored upstream Cantera scripts (unchanged) | `upstream/cantera/reactors/` |
| sim2stone-friendly adapter scripts | `adapters/` |
| Generated runnable STONE YAML | `examples/*.yaml` |
| Catalog manifest (source of truth for status/notes/links) | `examples/manifest.yaml` |
| Generation scripts | `scripts/generate_examples.py`, `scripts/build_catalog_rst.py`, `scripts/build_devcontainers.py` |
| Per-example Codespaces devcontainers | `.devcontainer/<id>/` (generated) |
| Sphinx docs / catalog page | `docs/`, `docs/catalog.rst` (generated) |
| Tests | `tests/` |

## Adapters vs. upstream scripts

- `upstream/cantera/reactors/` holds **unmodified** vendored Cantera sample scripts, pinned
  to a commit recorded in `examples/manifest.yaml`. Never hand-edit these.
- Some examples convert cleanly straight from the upstream script; others need an
  `adapters/<name>.py` version instead (referenced from `scripts/generate_examples.py`'s
  `_GENERATED` list) because the raw upstream script isn't sim2stone-friendly, e.g.:
  - it runs its own transient loop as top-level code, so introspecting it afterward
    captures the *end* state of a finished run instead of the true initial conditions
    (see `adapters/reactor2.py`, `adapters/periodic_cstr.py`);
  - it builds a time-varying `Func1` via a helper function with default arguments, which
    sim2stone's AST matcher can't resolve (see `adapters/fuel_injection.py` — use
    module-level scalars instead).
  - A stepping/loop pattern kept under `if False:` in an adapter is intentional: it lets
    sim2stone's AST solver-hint detector recover timing parameters from the source text
    without actually re-running the transient at conversion time.

## Regenerating examples

After changing an adapter, `scripts/generate_examples.py`, or bumping the pinned `boulder`
version in `requirements.txt`:

```bash
conda activate boulder
python scripts/generate_examples.py   # regenerate examples/*.yaml
python scripts/build_catalog_rst.py   # regenerate docs/catalog.rst from manifest.yaml
python scripts/build_devcontainers.py # regenerate .devcontainer/<id>/ + README launch links
make test
make qa
```

Verify a regenerated example actually reproduces upstream's behavior — run both the
regenerated YAML (headless, via `DualCanteraConverter`/`BoulderRunner`) and, when in doubt,
the real upstream script directly, and compare. A YAML that merely validates against the
STONE schema is not the same as one that reproduces the right physics.

## Environment

```bash
conda env create -n boulder -f environment.yml
conda activate boulder
```

The conda env is named `boulder` (not `boulder-examples`) and must be on `PATH` without an
explicit `conda activate` inside devcontainers/Codespaces — see `.devcontainer/Dockerfile`.

## Verification (what to run before a PR)

```bash
make test        # pytest tests/
make qa           # ruff check + ruff format --check
make docs-build    # optional: full Sphinx build
```

## Coding conventions

- Match the existing style: **Ruff** for lint/format (see `pyproject.toml`).
- Prefer fixing the root cause (adapter script, or the `boulder` core package) over
  hand-patching generated YAML — generated files must stay reproducible from
  `scripts/generate_examples.py`.
- If a bug traces back to `boulder` core (sim2stone, the converter, the frontend), fix it
  there first; only regenerate/commit the example YAML here once the fix has shipped in a
  released `boulder` version that `requirements.txt` is bumped to.

## Git and releases

- **Do not commit** unless the user or maintainer explicitly asks.

## Pull requests

- **Disclose AI involvement.** Every PR written or substantially assisted by an AI coding
  agent must say so in the PR description, naming the model, e.g.:

  > *Extensive AI use — code & PR fully written by Claude Sonnet 5*

  Use whatever phrasing fits the actual level of involvement (e.g. "AI-assisted" vs. "fully
  written by") but always name the model.

## Further reading

- [README.md](README.md) — quick start, Codespaces launch links.
- [docs/contributing.rst](docs/contributing.rst) — regeneration workflow.
- [Boulder's AGENTS.md](https://github.com/parks4/boulder/blob/main/AGENTS.md) — conventions
  for the core `boulder` package this repo depends on.
