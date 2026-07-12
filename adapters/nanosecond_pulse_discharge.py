"""Adapter for sim2stone: nanosecond pulse discharge network setup only.

Upstream runs a plasma micro-step loop that fails during headless execution with
energy='on'. This adapter preserves the Gaussian E/N signal and micro-step pattern
for AST extraction while stopping before integration.
"""

import cantera as ct
import numpy as np

EN_peak = 190 * 1e-21
pulse_center = 24e-9
pulse_width = 3e-9
pulse_fwhm = pulse_width * 2 * (2 * np.log(2)) ** 0.5
gaussian_EN = ct.Func1("Gaussian", [EN_peak, pulse_center, pulse_fwhm])

gas = ct.Solution("example_data/methane-plasma-pavan-2023.yaml")
gas.TPX = 300.0, 101325.0, "CH4:0.095, O2:0.19, N2:0.715, e:1E-11"
gas.reduced_electric_field = gaussian_EN(0)
gas.update_electron_energy_distribution()

r = ct.ConstPressureReactor(gas, energy="off", clone=False)
sim = ct.ReactorNet([r])
sim.verbose = False

t_total = 90e-9
dt_max = 1e-10
dt_chunk = 1e-9

# Preserve upstream micro-step structure for sim2stone AST (not executed).
if False:  # pragma: no cover - pattern reference for sim2stone_ast
    t = 0.0
    while t < t_total:
        t_end = min(t + dt_chunk, t_total)
        while sim.time < t_end:
            sim.advance(sim.time + dt_max)
        EN_t = gaussian_EN(t)
        gas.reduced_electric_field = EN_t
        gas.update_electron_energy_distribution()
        sim.reinitialize()
        t = t_end
