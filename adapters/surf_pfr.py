"""Adapter for sim2stone: FlowReactor + surface chemistry, initial state only.

Upstream runs its own distance march (``while sim.distance < length:
sim.step()``) before any conversion happens, so introspecting the live
objects afterward would capture the *outlet* state (methane already
converted) as if it were the inlet condition. This adapter stops before
that loop (kept under ``if False:`` purely so sim2stone's AST solver-hint
detector can still recover the distance-grid bound from the source text,
mirroring ``piston.py``'s stepping-loop convention) so sim2stone captures
the true inlet state instead.

Builds ``ct.FlowReactor`` + ``ct.ReactorSurface`` (not ``ct.FlowReactorSurface``)
since that is the object pair Boulder's sim2stone reverse-direction detector
(``_flow_reactor_surface_props``) and forward-direction builder
(``DualCanteraConverter._build_flow_reactor_surface_phase``) both expect.
"""

import cantera as ct

# unit conversion factors to SI
cm = 0.01
minute = 60.0

tc = 800.0  # Temperature in Celsius
length = 0.3 * cm  # Catalyst bed length
area = 1.0 * cm**2  # Catalyst bed area
cat_area_per_vol = 1000.0 / cm  # Catalyst particle surface area per unit volume
velocity = 40.0 * cm / minute  # gas velocity
porosity = 0.3  # Catalyst bed porosity

t = tc + 273.15  # convert to Kelvin

surf = ct.Interface("methane_pox_on_pt.yaml", "Pt_surf")
surf.TP = t, ct.one_atm
gas = surf.adjacent["gas"]
gas.TPX = t, ct.one_atm, "CH4:1, O2:1.5, AR:0.1"

mass_flow_rate = velocity * gas.density * area * porosity

r = ct.FlowReactor(gas, clone=True)
r.area = area
r.surface_area_to_volume_ratio = cat_area_per_vol * porosity
r.mass_flow_rate = mass_flow_rate
r.energy_enabled = False

rsurf = ct.ReactorSurface(surf, r, clone=True, name="pfr_surface")

sim = ct.ReactorNet([r])

if False:  # pragma: no cover - distance-marching pattern
    while sim.distance < length:
        sim.step()
