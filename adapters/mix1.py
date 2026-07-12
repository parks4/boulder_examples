"""Adapter for sim2stone: dual-stream mixer without running solve_steady."""

import cantera as ct

gas_a = ct.Solution("air.yaml")
gas_a.TPX = 300.0, ct.one_atm, "O2:0.21, N2:0.78, AR:0.01"
rho_a = gas_a.density

gas_b = ct.Solution("gri30.yaml")
gas_b.TPX = 300.0, ct.one_atm, "CH4:1"
rho_b = gas_b.density

res_a = ct.Reservoir(gas_a, name="air_reservoir")
res_b = ct.Reservoir(gas_b, name="fuel_reservoir")

gas_mixer = ct.Solution("gri30.yaml")
gas_mixer.TPX = 300.0, ct.one_atm, "O2:0.21, N2:0.78, AR:0.01"
mixer = ct.IdealGasReactor(gas_mixer, name="mixer")

ct.MassFlowController(res_a, mixer, mdot=rho_a * 2.5 / 0.21, name="air_inlet")
ct.MassFlowController(res_b, mixer, mdot=rho_b * 1.0, name="fuel_inlet")

# OutletSink is represented as a downstream reservoir for sim2stone capture only.
downstream = ct.Reservoir(gas_a, name="outlet")
ct.Valve(mixer, downstream, K=10.0, name="outlet_valve")

sim = ct.ReactorNet([mixer])

if False:  # pragma: no cover - solve_steady pattern for sim2stone_ast
    sim.solve_steady()
