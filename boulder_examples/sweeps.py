"""Host-produced run-sets, declared from a config's ``sweep.runner``.

Most sweeps belong in the YAML as a declarative ``sweep:`` block — see
``examples/continuous_reactor.yaml``, whose inlet-temperature axis drives two
nodes at once with a multi-target ``path:``. A runner is only for a run-set
that cannot be enumerated up front.

``combustor`` is that case. Its points must be solved **sequentially**, each
warm-started from the previous solve, because the sweep walks the combustor
*down its extinction branch*: residence time shrinks by a fixed factor until
the flame blows out. Two consequences make a declarative axis wrong here:

1. The branch is path-dependent. Re-solving each residence time independently
   from the equilibrium initial state finds the *ignited* solution, not the
   continued one — different physics, not merely a slower route to the same
   answer.
2. The number of points is only known once extinction happens.

Boulder resolves ``sweep.runner`` and calls it in-process with the collection
store path; this module writes scenarios into it with the same
``write_payload`` any sweep uses.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import cantera as ct
import h5py
from boulder.payload_store import gui_payload_from_solution_array, write_payload

_CR_TEMPERATURES_K = [650, 700, 750, 775, 825, 850, 875, 925, 950, 1075, 1100]
_CR_REACTOR_PRESSURE = ct.one_atm
_CR_INLET_X = {"CH4": 0.095, "O2": 0.21, "N2": 0.695}
_CR_RESIDENCE_TIME_S = 2.0
_CR_REACTOR_VOLUME_M3 = 30.5 * (1e-2) ** 3
_CR_MAX_SIMULATION_TIME_S = 50.0
_CR_SAMPLE_EVERY_N_STEPS = 10
_CR_REACTOR_ID = "stirred_reactor"
_CR_KPI_SPECIES = ("CH4", "CO", "O2")

_MECHANISM = "gri30.yaml"
_EQUIVALENCE_RATIO = 0.5
_FUEL_OXIDIZER = ("CH4:1.0", "O2:1.0, N2:3.76")
_INITIAL_RESIDENCE_TIME_S = 0.1
_RESIDENCE_TIME_DECAY = 0.9
_EXTINCTION_TEMPERATURE_K = 500.0
_REACTOR_ID = "combustor"


def _cr_solve_one_temperature(reactor_temperature: float, inlet_X: Dict[str, float]) -> ct.SolutionArray:
    """Build and solve the CSTR at one inlet temperature; return its trajectory."""
    gas = ct.Solution(_MECHANISM)
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

    # Pin the exact steady point for the KPI attrs. Right at this system's
    # extinction boundary the long transient march is numerically sensitive
    # (thread-count differences perturb rounding over thousands of adaptive
    # steps), so solve_steady() can occasionally fail to converge from this
    # warm start. The t=50 s endpoint is itself an excellent approximation, so
    # fall back to it rather than losing the whole sweep over one point.
    try:
        net.solve_steady()
    except ct.CanteraError as exc:
        print(
            f"[warn] solve_steady() did not converge at T={reactor_temperature} K "
            f"({exc}); using the transient endpoint at "
            f"t={_CR_MAX_SIMULATION_TIME_S}s instead.",
            flush=True,
        )
    history.append(reactor.phase.state, t=_CR_MAX_SIMULATION_TIME_S)
    return history


def continuous_reactor(
    store_path: "str | Path",
    progress: Optional[Callable[..., None]] = None,
) -> None:
    """Sweep the CSTR's inlet temperature, warm-starting each point.

    Upstream carries the converged composition from one temperature into the
    next (``reactor_X = stirred_reactor.phase.X``). That carry-over is load
    bearing, not a speed trick: solving each temperature independently from a
    fixed initial composition leaves CVode with a poor initial guess near the
    extinction boundary, and the 825 K point fails its error test outright.
    Sequential warm-starting is therefore what makes this a runner rather than
    a declarative ``sweep:`` axis.

    (The two-nodes-from-one-value problem it also has *is* expressible now, via
    a multi-target ``sweep`` ``path:`` list — see STONE_SPECIFICATIONS.md — but
    that alone does not survive the numerics above.)
    """
    store_path = Path(store_path)
    total = len(_CR_TEMPERATURES_K)
    inlet_X: Dict[str, float] = dict(_CR_INLET_X)
    scenario_kpis: Dict[str, Dict[str, float]] = {}

    for i, reactor_temperature in enumerate(_CR_TEMPERATURES_K, start=1):
        message = f"scenario {i}/{total}: T={reactor_temperature} K"
        print(message, flush=True)
        if progress is not None:
            progress(i, total, message)

        history = _cr_solve_one_temperature(float(reactor_temperature), inlet_X)
        final_X = dict(zip(history.species_names, history.X[-1]))
        inlet_X = final_X  # warm-start the next point (see docstring)

        scenario_id = f"T0_{reactor_temperature}K"
        scenario_kpis[scenario_id] = {f"final_X_{sp}": float(final_X[sp]) for sp in _CR_KPI_SPECIES}
        write_payload(
            store_path,
            gui_payload_from_solution_array(history, _CR_REACTOR_ID),
            mechanism=_MECHANISM,
            group=scenario_id,
            fresh=(i == 1),
        )

    with h5py.File(str(store_path), "r+") as handle:
        handle.attrs["mechanism_name"] = _MECHANISM
        handle.attrs["reactor_mode"] = "CSTR temperature sweep"
        handle.attrs["created_at"] = time.time()
        handle.attrs["cantera_version"] = ct.__version__
        for i, reactor_temperature in enumerate(_CR_TEMPERATURES_K, start=1):
            scenario_id = f"T0_{reactor_temperature}K"
            grp = handle[scenario_id]
            # `t0_K` is the swept input and the plot's default X axis; the
            # `final_*` attrs are results.
            grp.attrs["t0_K"] = float(reactor_temperature)
            grp.attrs["final_temperature_K"] = float(reactor_temperature)
            grp.attrs["label"] = f"T = {reactor_temperature} K"
            grp.attrs["order"] = i
            grp.attrs["computed_at"] = time.time()
            for key, value in scenario_kpis[scenario_id].items():
                grp.attrs[key] = value

    print(f"Sweep complete — {total} scenario(s) written to {store_path.name}")


def _build_network():
    """Mirror adapters/combustor.py's network exactly (same ids, same states)."""
    gas_in = ct.Solution(_MECHANISM, transport_model=None)
    gas_in.TP = 300.0, ct.one_atm
    gas_in.set_equivalence_ratio(_EQUIVALENCE_RATIO, *_FUEL_OXIDIZER)
    inlet = ct.Reservoir(gas_in, name="inlet")

    gas_comb = ct.Solution(_MECHANISM, transport_model=None)
    gas_comb.TP = gas_in.T, gas_in.P
    gas_comb.set_equivalence_ratio(_EQUIVALENCE_RATIO, *_FUEL_OXIDIZER)
    gas_comb.equilibrate("HP")
    combustor = ct.IdealGasReactor(gas_comb, clone=False, name=_REACTOR_ID)
    combustor.volume = 1.0

    exhaust = ct.Reservoir(gas_comb, name="exhaust")

    residence_time_box = [_INITIAL_RESIDENCE_TIME_S]  # mutable cell for mdot's closure

    def mdot(t: float) -> float:
        return combustor.mass / residence_time_box[0]

    inlet_mfc = ct.MassFlowController(inlet, combustor, mdot=mdot, name="air_inlet")
    ct.PressureController(combustor, exhaust, primary=inlet_mfc, K=0.01, name="outlet_pc")

    sim = ct.ReactorNet([combustor])
    return sim, combustor, gas_comb, residence_time_box


def combustor(
    store_path: "str | Path",
    progress: Optional[Callable[..., None]] = None,
) -> None:
    """Solve the combustor down to extinction, one scenario per point.

    Parameters
    ----------
    store_path :
        Collection store to write, resolved by Boulder from the config.
    progress :
        Optional ``(done, total, message)`` reporter supplied by Boulder, used
        to drive the Run Sweep status UI.

    """
    store_path = Path(store_path)
    sim, combustor_reactor, gas_comb, residence_time_box = _build_network()

    # Solve every point first (a handful of cheap steady solves) so the true
    # count is known before reporting "scenario i/N" -- this sweep is
    # exploratory, so the total does not exist until extinction is reached.
    points: List[Dict[str, Any]] = []
    while combustor_reactor.T > _EXTINCTION_TEMPERATURE_K:
        sim.initial_time = 0.0
        sim.solve_steady()
        points.append(
            {
                "residence_time_s": residence_time_box[0],
                "final_temperature_K": float(combustor_reactor.T),
                "heat_release_rate_w_m3": float(gas_comb.heat_release_rate),
                "state": gas_comb.state,
            }
        )
        residence_time_box[0] *= _RESIDENCE_TIME_DECAY

    total = len(points)
    for i, point in enumerate(points, start=1):
        message = (
            f"scenario {i}/{total}: tres={point['residence_time_s']:.3e} s, "
            f"T={point['final_temperature_K']:.1f} K"
        )
        print(message, flush=True)
        if progress is not None:
            progress(i, total, message)

        history = ct.SolutionArray(gas_comb, extra=["t"])
        history.append(point["state"], t=0.0)
        write_payload(
            store_path,
            gui_payload_from_solution_array(history, _REACTOR_ID),
            mechanism=_MECHANISM,
            group=f"tres_{i:03d}",
            fresh=(i == 1),
        )

    # KPI attrs: the numbers the Scenario pane's Sweep Results plot offers as
    # axes. `residence_time_s` is the swept input, the other two are results.
    with h5py.File(str(store_path), "r+") as handle:
        handle.attrs["mechanism_name"] = _MECHANISM
        handle.attrs["reactor_mode"] = "Combustor residence-time sweep"
        handle.attrs["created_at"] = time.time()
        handle.attrs["cantera_version"] = ct.__version__
        for i, point in enumerate(points, start=1):
            grp = handle[f"tres_{i:03d}"]
            grp.attrs["residence_time_s"] = point["residence_time_s"]
            grp.attrs["final_temperature_K"] = point["final_temperature_K"]
            grp.attrs["heat_release_rate_w_m3"] = point["heat_release_rate_w_m3"]
            grp.attrs["label"] = f"tres = {point['residence_time_s']:.3e} s"
            grp.attrs["order"] = i
            grp.attrs["computed_at"] = time.time()

    print(f"Sweep complete — {total} scenario(s) written to {store_path.name}")
