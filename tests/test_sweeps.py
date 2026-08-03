"""Every example that ships a scenario store must still offer Run Sweep.

This suite had no sweep coverage at all, which is why the two sweep examples
could break completely and stay green: Boulder used to run a file literally
named ``run_sweep.py`` next to a config, that discovery was removed, and since
neither config declared a run-set of its own, both silently lost their Run
Sweep button *and* their Scenario pane — with no way to regenerate a store
through the GUI at all.

These tests pin the contract that broke without solving anything: a sweep
example must advertise a runnable run-set, and a declared ``sweep.runner``
must actually import with the signature Boulder calls.

``*_scenarios.h5`` stores are generated, not committed (see .gitignore), so
the one test that inspects a store skips when it is absent.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import pytest
import yaml

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

#: Examples whose results are produced by a sweep.
SWEEP_EXAMPLES = ["combustor", "continuous_reactor"]

try:  # `sweep.runner` landed in parks4/boulder#139
    from boulder.runset import sweep_runner_of
except ImportError:  # pragma: no cover - depends on the installed boulder
    sweep_runner_of = None  # type: ignore[assignment]

#: The runner tests below need a Boulder that understands `sweep.runner`.
#: They skip (loudly) rather than fail on an older pin, and switch themselves
#: back on as soon as the pin moves -- the skip reason says exactly what to do.
requires_runner_support = pytest.mark.skipif(
    sweep_runner_of is None,
    reason=(
        "installed boulder predates sweep.runner (parks4/boulder#139); "
        "bump the boulder pin in environment.yml once it is released"
    ),
)


def _config(stem: str) -> dict:
    return yaml.safe_load((EXAMPLES / f"{stem}.yaml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("stem", SWEEP_EXAMPLES)
def test_boulder_sees_a_runnable_run_set(stem: str) -> None:
    """The exact check that silently started returning False."""
    from boulder.api.routes.sweep import has_run_set

    cfg_path = EXAMPLES / f"{stem}.yaml"
    assert has_run_set(_config(stem), str(cfg_path)) is True, (
        f"{stem}.yaml declares no run-set, so the GUI hides Run Sweep and the "
        "Scenario pane -- even though its scenario store is committed"
    )


@requires_runner_support
@pytest.mark.parametrize("stem", SWEEP_EXAMPLES)
def test_declared_sweep_runner_actually_resolves(stem: str) -> None:
    """A dotted path is only better than filename magic if it is checked."""
    from boulder.cantera_converter import resolve_dotted_path

    dotted = sweep_runner_of(_config(stem))
    if dotted is None:
        pytest.skip(f"{stem} uses a declarative sweep, not a runner")

    runner = resolve_dotted_path(dotted)
    assert callable(runner), f"{dotted} is not callable"


@requires_runner_support
@pytest.mark.parametrize("stem", SWEEP_EXAMPLES)
def test_runner_accepts_the_store_path_and_optional_progress(stem: str) -> None:
    """Boulder calls ``runner(store)`` or ``runner(store, progress=...)``."""
    import inspect

    from boulder.cantera_converter import resolve_dotted_path

    dotted = sweep_runner_of(_config(stem))
    if dotted is None:
        pytest.skip(f"{stem} uses a declarative sweep, not a runner")

    params = inspect.signature(resolve_dotted_path(dotted)).parameters
    positional: List[str] = [
        name
        for name, p in params.items()
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        and p.default is inspect.Parameter.empty
    ]
    assert len(positional) == 1, (
        f"{dotted} must take exactly one required positional argument (the store path); got {positional}"
    )
    if "progress" in params:
        assert params["progress"].default is not inspect.Parameter.empty, (
            "`progress` is supplied only when Boulder sees it in the signature, "
            "so it must be optional for a direct call to still work"
        )


def test_no_example_relies_on_run_sweep_py_discovery() -> None:
    """Boulder no longer runs a sibling script; nothing may depend on it."""
    assert not (EXAMPLES / "run_sweep.py").exists(), (
        "examples/run_sweep.py is back -- Boulder does not discover it, so the "
        "sweep it implements would never run. Declare sweep.runner instead."
    )


@pytest.mark.parametrize("stem", SWEEP_EXAMPLES)
def test_store_carries_enough_numeric_attrs_to_plot(stem: str) -> None:
    """The Sweep Results plot hides itself below two numeric axes.

    Bookkeeping attrs are excluded by the plot, so a store carrying only those
    renders nothing -- the difference between a working catalog screenshot and
    an empty pane.
    """
    h5py = pytest.importorskip("h5py")

    store = EXAMPLES / f"{stem}_scenarios.h5"
    if not store.is_file():
        # Stores are generated (gitignored), so a fresh checkout has none.
        pytest.skip(f"{store.name} not generated in this checkout")

    bookkeeping = {"order", "computed_at", "schema_version"}
    with h5py.File(str(store), "r") as handle:
        groups = [k for k in handle.keys() if isinstance(handle[k], h5py.Group)]
        assert groups, "store has no scenario groups"
        attrs = handle[groups[0]].attrs
        numeric = {k for k in attrs if k not in bookkeeping and isinstance(attrs[k], (int, float))}
    assert len(numeric) >= 2, (
        f"{stem} scenarios expose {sorted(numeric)} -- the plot needs at least "
        "two numeric attrs to offer an X and a Y axis"
    )
