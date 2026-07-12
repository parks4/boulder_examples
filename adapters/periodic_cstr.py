"""Adapter for sim2stone: periodic CSTR network without plotting."""

import cantera as ct

gas = ct.Solution("h2o2.yaml")
p = 60.0 * 133.3
t = 770.0
gas.TPX = t, p, "H2:2, O2:1"

upstream = ct.Reservoir(gas)
cstr = ct.IdealGasReactor(gas)
cstr.volume = 10.0 * 1.0e-6
env = ct.Reservoir(gas)
ct.Wall(cstr, env, A=1.0, U=0.02)

sccm = 1.25
vdot = sccm * 1.0e-6 / 60.0 * ((ct.one_atm / gas.P) * (gas.T / 273.15))
mdot = gas.density * vdot
ct.MassFlowController(upstream, cstr, mdot=mdot)

downstream = ct.Reservoir(gas)
ct.Valve(cstr, downstream, K=1.0e-9)

network = ct.ReactorNet([cstr])

if False:  # pragma: no cover - advance-grid pattern for sim2stone_ast
    t = 0.0
    dt = 0.1
    while t < 300.0:
        t += dt
        network.advance(t)
