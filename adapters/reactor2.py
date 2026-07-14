"""Adapter for sim2stone: piston reactor network setup only.

Upstream runs its own 300-step advance loop before any conversion happens, so
introspecting the live objects afterward captures the *end* of a completed
run (already-compressed, already-hot) as if it were the initial condition --
losing the dramatic argon compression/heating the whole example is about.
This adapter stops before that loop (kept under ``if False:`` purely so
sim2stone's AST solver-hint detector can still recover n_steps/step_size from
the source text) so sim2stone captures the true initial state instead.
"""

import cantera as ct

ar = ct.Solution("air.yaml")
ar.TPX = 1000.0, 20.0 * ct.one_atm, "AR:1"

r1 = ct.IdealGasReactor(ar, name="Argon partition")

env = ct.Reservoir(ct.Solution("air.yaml"), name="Environment")

gas = ct.Solution("gri30.yaml")
gas.TP = 500.0, 0.2 * ct.one_atm
gas.set_equivalence_ratio(1.1, "CH4:1.0", "O2:1, N2:3.76")

r2 = ct.IdealGasReactor(gas, name="Reacting partition")

w = ct.Wall(r2, r1, A=1.0, K=0.5e-4, U=100.0, name="Piston")
w2 = ct.Wall(r2, env, A=1.0, U=500.0, name="External Wall")

sim = ct.ReactorNet([r1, r2])

if False:  # pragma: no cover - transient stepping pattern
    time = 0.0
    n_steps = 300
    for n in range(n_steps):
        time += 4.0e-4
        sim.advance(time)
