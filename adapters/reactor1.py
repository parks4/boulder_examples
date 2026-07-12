"""Adapter for sim2stone: const-pressure ignition network without integration."""

import cantera as ct

gas = ct.Solution("h2o2.yaml")
gas.TPX = 1001.0, ct.one_atm, "H2:2,O2:1,N2:4"
r = ct.IdealGasConstPressureReactor(gas, clone=False)

sim = ct.ReactorNet([r])

delta_T_max = 20.0
r.set_advance_limit("temperature", delta_T_max)

dt_max = 1.0e-5
t_end = 100 * dt_max

if False:  # pragma: no cover - advance-grid pattern for sim2stone_ast
    while sim.time < t_end:
        sim.advance(sim.time + dt_max)
