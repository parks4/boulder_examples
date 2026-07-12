"""Adapter for sim2stone: combustor — single steady solve at reference residence time."""

import cantera as ct

gas_in = ct.Solution("gri30.yaml", transport_model=None)
gas_in.TP = 300.0, ct.one_atm
gas_in.set_equivalence_ratio(0.5, "CH4:1.0", "O2:1.0, N2:3.76")
inlet = ct.Reservoir(gas_in, name="inlet")

gas_comb = ct.Solution("gri30.yaml", transport_model=None)
gas_comb.TP = gas_in.T, gas_in.P
gas_comb.set_equivalence_ratio(0.5, "CH4:1.0", "O2:1.0, N2:3.76")
gas_comb.equilibrate("HP")
combustor = ct.IdealGasReactor(gas_comb, clone=False, name="combustor")
combustor.volume = 1.0

exhaust = ct.Reservoir(gas_comb, name="exhaust")

residence_time = 0.1


def mdot(t):
    return combustor.mass / residence_time


inlet_mfc = ct.MassFlowController(inlet, combustor, mdot=mdot, name="air_inlet")
ct.PressureController(combustor, exhaust, primary=inlet_mfc, K=0.01, name="outlet_pc")

sim = ct.ReactorNet([combustor])
sim.initial_time = 0.0
sim.solve_steady()
