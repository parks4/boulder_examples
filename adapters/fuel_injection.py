"""Adapter for sim2stone: fuel injection network without long integration."""

import cantera as ct
import numpy as np

gas = ct.Solution("nDodecane_Reitz.yaml", "nDodecane_IG")
gas.case_sensitive_species_names = True

gas.TPX = 300, 20 * ct.one_atm, "c12h26:1.0"
inlet = ct.Reservoir(gas)

gas.TP = 1000, 20 * ct.one_atm
gas.set_equivalence_ratio(0.30, "c12h26", "n2:3.76, o2:1.0")
gas.equilibrate("TP")
r = ct.IdealGasReactor(gas)
r.volume = 0.001


# Module-level scalars (rather than a helper function with default args) so
# sim2stone's AST matcher can resolve peak/center/fwhm into a signals: block
# instead of snapshotting the live Func1 at whatever instant it's introspected.
total_mass = 3.0e-3
std_dev = 0.5
center_time = 2.0
fuel_amplitude = total_mass / (std_dev * np.sqrt(2 * np.pi))
fuel_fwhm = std_dev * 2 * np.sqrt(2 * np.log(2))
fuel_gaussian = ct.Func1("Gaussian", [fuel_amplitude, center_time, fuel_fwhm])

ct.MassFlowController(inlet, r, mdot=fuel_gaussian)
sim = ct.ReactorNet([r])

tfinal = 10.0

if False:  # pragma: no cover - transient stepping pattern
    tnow = 0.0
    dt = 0.01
    while tnow < tfinal:
        tnow = sim.advance(tnow + dt)
