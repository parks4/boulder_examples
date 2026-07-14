"""Adapter for sim2stone: moving-piston reactor network setup only.

Upstream runs its own 200-step advance loop before any conversion happens, so
introspecting the live objects afterward would capture the *end* of a
completed run (already-equilibrated) as if it were the initial condition.
This adapter stops before that loop (kept under ``if False:`` purely so
sim2stone's AST solver-hint detector can still recover n_steps/step_size, and
its wall-velocity-closure detector can recover the delayed proportional
piston motion, from the source text) so sim2stone captures the true initial
state instead.
"""

import cantera as ct

gas1 = ct.Solution("h2o2.yaml")
gas1.TPX = 900.0, ct.one_atm, "H2:2, O2:1, AR:20"
r1 = ct.IdealGasReactor(gas1, name="Left reactor (H2/O2/Ar)")
r1.volume = 0.5

gas2 = ct.Solution("gri30.yaml")
gas2.TPX = 900.0, ct.one_atm, "CO:2, H2O:0.01, O2:5"
r2 = ct.IdealGasReactor(gas2, name="Right reactor (CO/H2O/O2)")
r2.volume = 0.1


def v(t):
    if t < 0.1:
        return 0.0
    else:
        return (r1.phase.P - r2.phase.P) * 1e-4


w = ct.Wall(r1, r2, velocity=v, name="Piston")

sim = ct.ReactorNet([r1, r2])

if False:  # pragma: no cover - transient stepping pattern
    time = 0.0
    n_steps = 200
    for n in range(n_steps):
        time += 1.0e-3
        sim.advance(time)
