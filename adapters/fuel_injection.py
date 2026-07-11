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


def fuel_mdot(total_mass=3.0e-3, std_dev=0.5, center_time=2.0):
    amplitude = total_mass / (std_dev * np.sqrt(2 * np.pi))
    fwhm = std_dev * 2 * np.sqrt(2 * np.log(2))
    return ct.Func1("Gaussian", [amplitude, center_time, fwhm])


ct.MassFlowController(inlet, r, mdot=fuel_mdot())
sim = ct.ReactorNet([r])

if False:  # pragma: no cover - transient stepping pattern
    tfinal = 10.0
    tnow = 0.0
    while tnow < tfinal:
        tnow = sim.step()
