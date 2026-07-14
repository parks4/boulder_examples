#!/usr/bin/env python3
"""Host-provided sweep runner — dispatches by config filename.

Boulder's ``/api/sweep/run`` always invokes a file literally named
``run_sweep.py`` next to the preloaded config (see
``boulder/api/routes/sweep.py``'s ``_RUNNER_NAME``), passing the config's
filename as the sole positional argument. Since every example in this repo
lives flat under ``examples/``, one runner file is shared across all of them;
``main()`` below dispatches on the config's stem to the right implementation.

This is the documented escape hatch for a run-set whose cases can't be
expressed as a static ``sweep:``/``scenario:`` block:

- ``continuous_reactor.yaml``: the same inlet temperature must propagate to
  *two* network nodes at once (the inlet reservoir and the reactor's
  isothermal initial state), which STONE's single-``path`` sweep axis cannot
  express.
- ``combustor.yaml``: the sweep is *exploratory* -- residence time decreases
  by a fixed factor each iteration until the reactor extinguishes, so the
  number of points isn't known ahead of time; STONE's ``sweep:`` block only
  expresses fixed value lists/ranges.

Both write one composite scenario per run-set point to ``<stem>_scenarios.h5``
(the collection file Boulder's Scenario pane, ``/api/scenarios``, reads), and
print ``scenario N/M`` progress lines parsed by ``/api/sweep``.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import cantera as ct
import h5py
from boulder.payload_store import gui_payload_from_solution_array, write_payload

# ---------------------------------------------------------------------------
# continuous_reactor.yaml: CSTR inlet-temperature sweep (eleven fixed points).
# ---------------------------------------------------------------------------

# Same eleven points and reactor parameters as upstream continuous_reactor.py's
# sweep (see adapters/continuous_reactor.py for the mechanism-substitution note).
_CR_TEMPERATURES_K = [650, 700, 750, 775, 825, 850, 875, 925, 950, 1075, 1100]
_CR_REACTOR_PRESSURE = ct.one_atm
_CR_INLET_X = {"CH4": 0.095, "O2": 0.21, "N2": 0.695}
_CR_RESIDENCE_TIME_S = 2.0
_CR_REACTOR_VOLUME_M3 = 30.5 * (1e-2) ** 3
_CR_MAX_SIMULATION_TIME_S = 50.0
_CR_SAMPLE_EVERY_N_STEPS = 10
_CR_REACTOR_ID = "stirred_reactor"
_CR_MECHANISM = "gri30.yaml"


def _cr_solve_one_temperature(reactor_temperature: float, inlet_X: dict) -> ct.SolutionArray:
    """Build and solve the CSTR at one inlet temperature; return its trajectory."""
    gas = ct.Solution(_CR_MECHANISM)
    gas.TPX = reactor_temperature, _CR_REACTOR_PRESSURE, inlet_X

    tank = ct.Reservoir(gas)
    exhaust = ct.Reservoir(gas)
    reactor = ct.IdealGasMoleReactor(gas, energy="off", volume=_CR_REACTOR_VOLUME_M3, name=_CR_REACTOR_ID)

    def mdot(t: float) -> float:
        return reactor.mass / _CR_RESIDENCE_TIME_S

    mfc = ct.MassFlowController(tank, reactor, mdot=mdot)
    ct.PressureController(reactor, exhaust, primary=mfc, K=1e-6)

    net = ct.ReactorNet([reactor])
    net.initial_time = 0.0

    history = ct.SolutionArray(gas, extra=["t"])
    t = 0.0
    counter = 0
    while t < _CR_MAX_SIMULATION_TIME_S:
        t = net.step()
        counter += 1
        if counter % _CR_SAMPLE_EVERY_N_STEPS == 0:
            history.append(reactor.phase.state, t=t)

    # solve_steady() converges cleanly from this already-close warm-started
    # state (see adapters/continuous_reactor.py for why advance_to_steady_state
    # is avoided) and pins down the exact steady point for the KPI attrs below.
    # Right at this system's low/high-temperature extinction boundary, the
    # long transient march's exact trajectory is numerically sensitive
    # (BLAS/OpenMP thread-count differences between environments perturb
    # floating-point rounding over thousands of adaptive steps), and that can
    # occasionally leave solve_steady() unable to converge from this
    # particular warm start (observed via the GUI's subprocess invocation,
    # not the plain CLI one -- same script, different thread-count
    # environment). The already-integrated t=50s transient endpoint is
    # itself an excellent approximation of steady state, so fall back to it
    # rather than aborting the whole sweep over one scenario.
    try:
        net.solve_steady()
    except ct.CanteraError as exc:
        print(
            f"[warn] solve_steady() did not converge at T={reactor_temperature} K "
            f"({exc}); using the transient endpoint at t={_CR_MAX_SIMULATION_TIME_S}s instead.",
            flush=True,
        )
    history.append(reactor.phase.state, t=_CR_MAX_SIMULATION_TIME_S)
    return history


def _run_continuous_reactor_sweep(config_path: Path) -> int:
    store_path = config_path.with_name(f"{config_path.stem}_scenarios.h5")

    total = len(_CR_TEMPERATURES_K)
    inlet_X = dict(_CR_INLET_X)
    kpi_species = ("CH4", "CO", "O2")
    scenario_kpis: dict[str, dict[str, float]] = {}
    for i, reactor_temperature in enumerate(_CR_TEMPERATURES_K, start=1):
        print(f"scenario {i}/{total}: T={reactor_temperature} K", flush=True)
        history = _cr_solve_one_temperature(float(reactor_temperature), inlet_X)
        names = history.species_names
        final_X = dict(zip(names, history.X[-1]))
        # Warm-start the next point from this one's converged composition,
        # mirroring upstream's "reactor_X = stirred_reactor.phase.X" carry-over.
        inlet_X = final_X

        scenario_id = f"T0_{reactor_temperature}K"
        scenario_kpis[scenario_id] = {f"final_X_{sp}": float(final_X[sp]) for sp in kpi_species}
        payload = gui_payload_from_solution_array(history, _CR_REACTOR_ID)
        write_payload(
            store_path,
            payload,
            mechanism=_CR_MECHANISM,
            group=scenario_id,
            fresh=(i == 1),
        )

    with h5py.File(str(store_path), "r+") as handle:
        handle.attrs["mechanism_name"] = _CR_MECHANISM
        handle.attrs["reactor_mode"] = "CSTR temperature sweep"
        handle.attrs["map_config"] = config_path.name
        handle.attrs["created_at"] = time.time()
        handle.attrs["cantera_version"] = ct.__version__
        for i, reactor_temperature in enumerate(_CR_TEMPERATURES_K, start=1):
            scenario_id = f"T0_{reactor_temperature}K"
            grp = handle[scenario_id]
            grp.attrs["t0_K"] = float(reactor_temperature)
            grp.attrs["label"] = f"T = {reactor_temperature} K"
            grp.attrs["order"] = i
            grp.attrs["final_temperature_K"] = float(reactor_temperature)
            grp.attrs["computed_at"] = time.time()
            for key, value in scenario_kpis[scenario_id].items():
                grp.attrs[key] = value

    print(f"Sweep complete — {total} scenario(s) written to {store_path.name}")
    return 0


# ---------------------------------------------------------------------------
# combustor.yaml: exploratory residence-time sweep down to extinction.
# ---------------------------------------------------------------------------

_CB_MECHANISM = "gri30.yaml"
_CB_EQUIVALENCE_RATIO = 0.5
_CB_FUEL_OXIDIZER = ("CH4:1.0", "O2:1.0, N2:3.76")
_CB_INITIAL_RESIDENCE_TIME_S = 0.1
_CB_RESIDENCE_TIME_DECAY = 0.9
_CB_EXTINCTION_TEMPERATURE_K = 500.0
_CB_REACTOR_ID = "combustor"


def _cb_build_network() -> tuple[ct.ReactorNet, ct.IdealGasReactor, ct.Solution, list]:
    """Mirror adapters/combustor.py's network exactly (same ids, same states)."""
    gas_in = ct.Solution(_CB_MECHANISM, transport_model=None)
    gas_in.TP = 300.0, ct.one_atm
    gas_in.set_equivalence_ratio(_CB_EQUIVALENCE_RATIO, *_CB_FUEL_OXIDIZER)
    inlet = ct.Reservoir(gas_in, name="inlet")

    gas_comb = ct.Solution(_CB_MECHANISM, transport_model=None)
    gas_comb.TP = gas_in.T, gas_in.P
    gas_comb.set_equivalence_ratio(_CB_EQUIVALENCE_RATIO, *_CB_FUEL_OXIDIZER)
    gas_comb.equilibrate("HP")
    combustor = ct.IdealGasReactor(gas_comb, clone=False, name=_CB_REACTOR_ID)
    combustor.volume = 1.0

    exhaust = ct.Reservoir(gas_comb, name="exhaust")

    residence_time_box = [_CB_INITIAL_RESIDENCE_TIME_S]  # mutable cell for mdot's closure

    def mdot(t: float) -> float:
        return combustor.mass / residence_time_box[0]

    inlet_mfc = ct.MassFlowController(inlet, combustor, mdot=mdot, name="air_inlet")
    ct.PressureController(combustor, exhaust, primary=inlet_mfc, K=0.01, name="outlet_pc")

    sim = ct.ReactorNet([combustor])
    return sim, combustor, gas_comb, residence_time_box


def _run_combustor_sweep(config_path: Path) -> int:
    store_path = config_path.with_name(f"{config_path.stem}_scenarios.h5")

    sim, combustor, gas_comb, residence_time_box = _cb_build_network()

    # Phase 1: solve every point first (cheap; a handful of steady solves) so
    # the true point count is known before printing "scenario i/N" progress --
    # this sweep is exploratory (stops at extinction), unlike
    # continuous_reactor's fixed eleven points.
    points: list[dict] = []
    while combustor.T > _CB_EXTINCTION_TEMPERATURE_K:
        sim.initial_time = 0.0
        sim.solve_steady()
        points.append(
            {
                "residence_time_s": residence_time_box[0],
                "final_temperature_K": float(combustor.T),
                "heat_release_rate_w_m3": float(gas_comb.heat_release_rate),
                "state": gas_comb.state,
            }
        )
        residence_time_box[0] *= _CB_RESIDENCE_TIME_DECAY

    total = len(points)
    for i, point in enumerate(points, start=1):
        print(
            f"scenario {i}/{total}: tres={point['residence_time_s']:.3e} s, "
            f"T={point['final_temperature_K']:.1f} K",
            flush=True,
        )
        history = ct.SolutionArray(gas_comb, extra=["t"])
        history.append(point["state"], t=0.0)
        payload = gui_payload_from_solution_array(history, _CB_REACTOR_ID)
        scenario_id = f"tres_{i:03d}"
        write_payload(
            store_path,
            payload,
            mechanism=_CB_MECHANISM,
            group=scenario_id,
            fresh=(i == 1),
        )

    with h5py.File(str(store_path), "r+") as handle:
        handle.attrs["mechanism_name"] = _CB_MECHANISM
        handle.attrs["reactor_mode"] = "Combustor residence-time sweep"
        handle.attrs["map_config"] = config_path.name
        handle.attrs["created_at"] = time.time()
        handle.attrs["cantera_version"] = ct.__version__
        for i, point in enumerate(points, start=1):
            scenario_id = f"tres_{i:03d}"
            grp = handle[scenario_id]
            grp.attrs["residence_time_s"] = point["residence_time_s"]
            grp.attrs["final_temperature_K"] = point["final_temperature_K"]
            grp.attrs["heat_release_rate_w_m3"] = point["heat_release_rate_w_m3"]
            grp.attrs["label"] = f"tres = {point['residence_time_s']:.3e} s"
            grp.attrs["order"] = i
            grp.attrs["computed_at"] = time.time()

    print(f"Sweep complete — {total} scenario(s) written to {store_path.name}")
    return 0


def main(argv: list) -> int:
    if not argv:
        print("Usage: run_sweep.py <config.yaml> [--no-plot]", file=sys.stderr)
        return 2
    config_path = Path(argv[0]).resolve()
    if config_path.stem == "combustor":
        return _run_combustor_sweep(config_path)
    if config_path.stem == "continuous_reactor":
        return _run_continuous_reactor_sweep(config_path)
    print(
        f"run_sweep.py: no host-defined sweep implemented for '{config_path.stem}'.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
