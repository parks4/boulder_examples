"""Adapter for sim2stone: CSTR baseline case for the continuous_reactor sweep.

Upstream builds one CSTR network (fuel/oxidizer reservoir -> MFC -> stirred
reactor -> PressureController -> exhaust reservoir) and re-solves it at eleven
inlet temperatures to trace species mole fraction vs. temperature. This
adapter emits the *same topology and solver idiom* at the baseline temperature
(925 K, the value upstream sets before the sweep begins) — the real
``while t < max_simulation_time: t = reactor_network.step()`` march, which
sim2stone's AST scan detects as ``advance_grid`` (same as an explicit
``.advance()`` loop, just with Cantera's own adaptive step size);
``run_sweep.py`` builds and solves the other ten points independently and
writes the scenario store the GUI's Scenario pane reads.

Mechanism note: upstream loads ``example_data/n-heptane-NUIG-2016.yaml``
(1268 species / 5336 reactions). That mechanism is not bundled in the Cantera
3.2 conda distribution used by Boulder CI, so this repo vendors it verbatim
under ``upstream/cantera/example_data/`` (see ``LICENSES/Cantera.txt``) for
provenance/future use — but Boulder's converter builds every node with
``clone=True`` (an independent ``Solution`` per reactor), and cloning a
1268-species/5336-reaction kinetics manager three times over is impractically
slow (multi-minute hangs observed, not just slow-but-tractable) inside
Boulder's pipeline, even though the same network solves in ~6 s through plain
Cantera. This adapter substitutes the bundled ``gri30.yaml`` with a lean
CH4/O2/N2 mixture instead, preserving the CSTR topology and
temperature-sweep methodology; the swept species are CH4/CO/O2 instead of
NC7H16/CO/O2.
"""

import cantera as ct

reactor_temperature = 925.0  # Kelvin — baseline point in upstream's sweep list
reactor_pressure = ct.one_atm
inlet_X = "CH4:0.095, O2:0.21, N2:0.695"

gas = ct.Solution("gri30.yaml")
gas.TPX = reactor_temperature, reactor_pressure, inlet_X

residence_time = 2.0  # s
reactor_volume = 30.5 * (1e-2) ** 3  # m3

fuel_air_mixture_tank = ct.Reservoir(gas, name="fuel_air_mixture_tank")
exhaust = ct.Reservoir(gas, name="exhaust")

stirred_reactor = ct.IdealGasMoleReactor(
    gas, energy="off", volume=reactor_volume, name="stirred_reactor"
)


def mdot(t):
    return stirred_reactor.mass / residence_time


mass_flow_controller = ct.MassFlowController(
    fuel_air_mixture_tank, stirred_reactor, mdot=mdot, name="mass_flow_controller"
)

pressure_regulator = ct.PressureController(
    stirred_reactor,
    exhaust,
    primary=mass_flow_controller,
    K=1e-6,
    name="pressure_regulator",
)

reactor_network = ct.ReactorNet([stirred_reactor])
reactor_network.initial_time = 0.0

max_simulation_time = 50.0  # seconds — matches upstream
t = 0.0
while t < max_simulation_time:
    t = reactor_network.step()
