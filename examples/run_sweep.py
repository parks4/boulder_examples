#!/usr/bin/env python3
"""Host-provided sweep runner for continuous_reactor.yaml.

Boulder's ``/api/sweep/run`` invokes ``run_sweep.py <config> --no-plot`` when
found next to a STONE config (see ``boulder/api/routes/sweep.py``) — this is
the documented escape hatch for a run-set whose cases can't be expressed as a
static ``sweep:``/``scenario:`` block (here: the same inlet temperature must
propagate to *two* network nodes at once — the inlet reservoir and the
reactor's isothermal initial state — which STONE's single-``path`` sweep axis
cannot express).

Rebuilds the CSTR from ``continuous_reactor.yaml`` at each of the eleven
inlet temperatures upstream's ``continuous_reactor.py`` sweeps (see its
``T = [...]`` list), solving each independently to steady state exactly as
the base YAML's ``settings.solver.kind: solve_steady`` does, and writes one
composite scenario per temperature to ``continuous_reactor_scenarios.h5`` —
the collection file Boulder's Scenario pane (``/api/scenarios``) reads.

Prints ``scenario N/M`` progress lines (parsed by ``/api/sweep`` to report
progress) and writes per-scenario KPI attrs (``final_X_CH4``, ``final_X_CO``,
``final_X_O2``) alongside the standard ``t0_K``/``label`` so a sweep-results
view can plot species mole fraction vs. temperature across all scenarios
without re-opening every group's full trajectory.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import cantera as ct
import h5py
from boulder.payload_store import gui_payload_from_solution_array, write_payload

# Same eleven points and reactor parameters as upstream continuous_reactor.py's
# sweep (see adapters/continuous_reactor.py for the mechanism-substitution note).
TEMPERATURES_K = [650, 700, 750, 775, 825, 850, 875, 925, 950, 1075, 1100]
REACTOR_PRESSURE = ct.one_atm
INLET_X = {"CH4": 0.095, "O2": 0.21, "N2": 0.695}
RESIDENCE_TIME_S = 2.0
REACTOR_VOLUME_M3 = 30.5 * (1e-2) ** 3
MAX_SIMULATION_TIME_S = 50.0
SAMPLE_EVERY_N_STEPS = 10
REACTOR_ID = "stirred_reactor"
MECHANISM = "gri30.yaml"


def _solve_one_temperature(reactor_temperature: float, inlet_X: dict) -> ct.SolutionArray:
    """Build and solve the CSTR at one inlet temperature; return its trajectory."""
    gas = ct.Solution(MECHANISM)
    gas.TPX = reactor_temperature, REACTOR_PRESSURE, inlet_X

    tank = ct.Reservoir(gas)
    exhaust = ct.Reservoir(gas)
    reactor = ct.IdealGasMoleReactor(gas, energy="off", volume=REACTOR_VOLUME_M3, name=REACTOR_ID)

    def mdot(t: float) -> float:
        return reactor.mass / RESIDENCE_TIME_S

    mfc = ct.MassFlowController(tank, reactor, mdot=mdot)
    ct.PressureController(reactor, exhaust, primary=mfc, K=1e-6)

    net = ct.ReactorNet([reactor])
    net.initial_time = 0.0

    history = ct.SolutionArray(gas, extra=["t"])
    t = 0.0
    counter = 0
    while t < MAX_SIMULATION_TIME_S:
        t = net.step()
        counter += 1
        if counter % SAMPLE_EVERY_N_STEPS == 0:
            history.append(reactor.phase.state, t=t)

    # solve_steady() converges cleanly from this already-close warm-started
    # state (see adapters/continuous_reactor.py for why advance_to_steady_state
    # is avoided) and pins down the exact steady point for the KPI attrs below.
    net.solve_steady()
    history.append(reactor.phase.state, t=MAX_SIMULATION_TIME_S)
    return history


def main(argv: list) -> int:
    if not argv:
        print("Usage: run_sweep.py <config.yaml> [--no-plot]", file=sys.stderr)
        return 2
    config_path = Path(argv[0]).resolve()
    store_path = config_path.with_name(f"{config_path.stem}_scenarios.h5")

    total = len(TEMPERATURES_K)
    inlet_X = dict(INLET_X)
    kpi_species = ("CH4", "CO", "O2")
    scenario_kpis: dict[str, dict[str, float]] = {}
    for i, reactor_temperature in enumerate(TEMPERATURES_K, start=1):
        print(f"scenario {i}/{total}: T={reactor_temperature} K", flush=True)
        history = _solve_one_temperature(float(reactor_temperature), inlet_X)
        names = history.species_names
        final_X = dict(zip(names, history.X[-1]))
        # Warm-start the next point from this one's converged composition,
        # mirroring upstream's "reactor_X = stirred_reactor.phase.X" carry-over.
        inlet_X = final_X

        scenario_id = f"T0_{reactor_temperature}K"
        scenario_kpis[scenario_id] = {f"final_X_{sp}": float(final_X[sp]) for sp in kpi_species}
        payload = gui_payload_from_solution_array(history, REACTOR_ID)
        write_payload(
            store_path,
            payload,
            mechanism=MECHANISM,
            group=scenario_id,
            fresh=(i == 1),
        )

    with h5py.File(str(store_path), "r+") as handle:
        handle.attrs["mechanism_name"] = MECHANISM
        handle.attrs["reactor_mode"] = "CSTR temperature sweep"
        handle.attrs["map_config"] = config_path.name
        handle.attrs["created_at"] = time.time()
        handle.attrs["cantera_version"] = ct.__version__
        for i, reactor_temperature in enumerate(TEMPERATURES_K, start=1):
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


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
