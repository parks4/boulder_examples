Example catalog
===============

Pinned upstream: ``https://github.com/Cantera/cantera`` ``samples/python/reactors`` @ ``main``.

See :doc:`boulder:stone` for the STONE YAML format and :doc:`boulder:cantera_upstream_examples` for solver mapping from upstream Cantera scripts. Networks are simulated with :class:`cantera.ReactorNet`.

Steady combustor residence time
-------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/combustor.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/combustor.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/combustor.html <https://cantera.org/dev/examples/python/reactors/combustor.html>`_
:Status: **adapted**
:STONE: ``examples/combustor.yaml``
:Mechanism: ``gri30.yaml``

Upstream sweeps residence time down from 0.1 s in 0.9x steps until the combustor extinguishes (T <= 500 K) -- an exploratory stop condition, not a fixed value list, so it can't be expressed as a static sweep:/scenario: block. The base YAML is the single steady solve at the 0.1 s reference point (solver.kind: solve_steady, with a closure: residence_time MFC), and run_sweep.py (a host-provided sweep runner Boulder's /api/sweep invokes) reproduces the full extinction sweep, writing one scenario per residence time to the Scenario pane's store with residence_time_s/final_temperature_K/heat_release_rate_w_m3 attrs -- pick Residence Time S / Heat Release Rate in the Sweep results pane's axis selectors for the same plot upstream's script produces.

.. image:: /_static/screenshots/combustor.png
   :width: 100%

`Launch in GitHub Codespaces <https://codespaces.new/parks4/boulder_examples?devcontainer_path=.devcontainer/combustor/devcontainer.json&quickstart=1>`_ — opens this example running in Boulder, forwarded port opens in your browser.

Or run locally:

.. code-block:: bash

   boulder examples/combustor.yaml --no-open

Piston reactor with heat transfer
---------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/reactor2.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/reactor2.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/reactor2.html <https://cantera.org/dev/examples/python/reactors/reactor2.html>`_
:Status: **adapted**
:STONE: ``examples/reactor2.yaml``
:Mechanism: ``gri30.yaml``

Transient advance-grid example. The piston wall's expansion_rate_coeff (K) and heat_transfer_coeff (U) are both captured in STONE, so Boulder reproduces upstream's pressure-driven piston motion and heat exchange together; plots focus on reactor temperature and pressure evolution.

.. image:: /_static/screenshots/reactor2.png
   :width: 100%

`Launch in GitHub Codespaces <https://codespaces.new/parks4/boulder_examples?devcontainer_path=.devcontainer/reactor2/devcontainer.json&quickstart=1>`_ — opens this example running in Boulder, forwarded port opens in your browser.

Or run locally:

.. code-block:: bash

   boulder examples/reactor2.yaml --no-open

Nanosecond pulse discharge
--------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/nanosecond_pulse_discharge.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/nanosecond_pulse_discharge.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/nanosecond_pulse_discharge.html <https://cantera.org/dev/examples/python/reactors/nanosecond_pulse_discharge.html>`_
:Status: **adapted**
:STONE: ``examples/nanosecond_pulse_discharge.yaml``
:Mechanism: ``example_data/methane-plasma-pavan-2023.yaml``

Plasma micro-step example with Gaussian reduced-electric-field signal. Upstream runs with energy: "on" so plasma heating feeds back into gas temperature and accelerates the discharge; this adapter uses energy: "off" because Cantera 3.2's PlasmaPhase has no cp_mole() implementation, so energy: "on" raises "NotImplementedError: PlasmaPhase::cp_mole" the moment the reactor's energy equation needs a heat capacity. Without that thermal feedback the discharge never reaches upstream's self-sustaining avalanche regime, so temperature and product-species mole fractions stay many orders of magnitude below upstream's plot -- a genuine, currently open Cantera limitation (not a Boulder conversion defect). Re-check once PlasmaPhase::cp_mole is implemented upstream.

.. image:: /_static/screenshots/nanosecond_pulse_discharge.png
   :width: 100%

`Launch in GitHub Codespaces <https://codespaces.new/parks4/boulder_examples?devcontainer_path=.devcontainer/nanosecond_pulse_discharge/devcontainer.json&quickstart=1>`_ — opens this example running in Boulder, forwarded port opens in your browser.

Or run locally:

.. code-block:: bash

   boulder examples/nanosecond_pulse_discharge.yaml --no-open

Mixer with two inlet streams
----------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/mix1.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/mix1.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/mix1.html <https://cantera.org/dev/examples/python/reactors/mix1.html>`_
:Status: **adapted**
:STONE: ``examples/mix1.yaml``
:Mechanism: ``gri30.yaml``

Dual-mechanism steady mixer with MFC and valve; uses solve_steady and OutletSink for the downstream boundary.

.. image:: /_static/screenshots/mix1.png
   :width: 100%

`Launch in GitHub Codespaces <https://codespaces.new/parks4/boulder_examples?devcontainer_path=.devcontainer/mix1/devcontainer.json&quickstart=1>`_ — opens this example running in Boulder, forwarded port opens in your browser.

Or run locally:

.. code-block:: bash

   boulder examples/mix1.yaml --no-open

Constant-pressure ignition
--------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/reactor1.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/reactor1.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/reactor1.html <https://cantera.org/dev/examples/python/reactors/reactor1.html>`_
:Status: **adapted**
:STONE: ``examples/reactor1.yaml``
:Mechanism: ``h2o2.yaml``

Single IdealGasConstPressureReactor with temperature advance limit and advance_grid transient integration.

.. image:: /_static/screenshots/reactor1.png
   :width: 100%

`Launch in GitHub Codespaces <https://codespaces.new/parks4/boulder_examples?devcontainer_path=.devcontainer/reactor1/devcontainer.json&quickstart=1>`_ — opens this example running in Boulder, forwarded port opens in your browser.

Or run locally:

.. code-block:: bash

   boulder examples/reactor1.yaml --no-open

Periodic CSTR
-------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/periodic_cstr.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/periodic_cstr.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/periodic_cstr.html <https://cantera.org/dev/examples/python/reactors/periodic_cstr.html>`_
:Status: **adapted**
:STONE: ``examples/periodic_cstr.yaml``
:Mechanism: ``h2o2.yaml``

CSTR with MFC, valve, and heat-transfer wall.

.. image:: /_static/screenshots/periodic_cstr.png
   :width: 100%

`Launch in GitHub Codespaces <https://codespaces.new/parks4/boulder_examples?devcontainer_path=.devcontainer/periodic_cstr/devcontainer.json&quickstart=1>`_ — opens this example running in Boulder, forwarded port opens in your browser.

Or run locally:

.. code-block:: bash

   boulder examples/periodic_cstr.yaml --no-open

Fuel injection with Gaussian pulse
----------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/fuel_injection.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/fuel_injection.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/fuel_injection.html <https://cantera.org/dev/examples/python/reactors/fuel_injection.html>`_
:Status: **adapted**
:STONE: ``examples/fuel_injection.yaml``
:Mechanism: ``nDodecane_Reitz.yaml``

Transient fuel pulse; Gaussian MFC signal when AST detection succeeds.

.. image:: /_static/screenshots/fuel_injection.png
   :width: 100%

`Launch in GitHub Codespaces <https://codespaces.new/parks4/boulder_examples?devcontainer_path=.devcontainer/fuel_injection/devcontainer.json&quickstart=1>`_ — opens this example running in Boulder, forwarded port opens in your browser.

Or run locally:

.. code-block:: bash

   boulder examples/fuel_injection.yaml --no-open

Preconditioned single-reactor integration
-----------------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/preconditioned_integration.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/preconditioned_integration.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/preconditioned_integration.html <https://cantera.org/dev/examples/python/reactors/preconditioned_integration.html>`_
:Status: **unsupported**
:Reason: Compares integration wall-clock time with vs. without a sparse preconditioner across two full re-runs of the same network -- a solver-performance A/B benchmark, not a single network solve, so it has no STONE representation (same class of issue as preconditioned_network below). The n-heptane-NUIG-2016.yaml mechanism it needs is already vendored under upstream/cantera/example_data/.

1D packed bed (DAE)
-------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/1D_packed_bed.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/1D_packed_bed.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/1D_packed_bed.html <https://cantera.org/dev/examples/python/reactors/1D_packed_bed.html>`_
:Status: **unsupported**
:Reason: Custom scikits.odes DAE packed-bed model; no global ReactorNet.

1D PFR surface chemistry
------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/1D_pfr_surfchem.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/1D_pfr_surfchem.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/1D_pfr_surfchem.html <https://cantera.org/dev/examples/python/reactors/1D_pfr_surfchem.html>`_
:Status: **unsupported**
:Reason: Uses FlowReactor + ReactorSurface, now supported by Boulder (see surf_pfr below and https://github.com/parks4/boulder/pull/112) -- not yet adapted here: this script's mechanism (SiF4_NH3_mec.yaml, silicon nitride deposition) and matplotlib-only diagnostics (deposition rate, surface site fractions) need their own STONE mapping, tracked separately from surf_pfr's simpler single-species-output case.

Continuous reactor temperature sweep
------------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/continuous_reactor.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/continuous_reactor.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/continuous_reactor.html <https://cantera.org/dev/examples/python/reactors/continuous_reactor.html>`_
:Status: **adapted**
:STONE: ``examples/continuous_reactor.yaml``
:Mechanism: ``gri30.yaml``

The outer temperature sweep is not one static STONE file (STONE's inline sweep:/scenario: blocks can't drive two nodes — inlet reservoir and reactor initial state — from one swept value), so the base YAML is the CSTR topology at the 925 K baseline point and run_sweep.py (a host-provided sweep runner Boulder's /api/sweep invokes) independently solves the other ten upstream temperatures to steady state, writing them to the Scenario pane's store. Mechanism substituted: upstream's example_data/n-heptane-NUIG-2016.yaml (1268 species) is not bundled in Boulder CI's Cantera distribution and is also impractically slow to clone through Boulder's per-node solve pipeline; this repo vendors it under upstream/cantera/example_data/ for provenance, but the shipped example uses the bundled gri30.yaml (CH4/O2/N2) — same CSTR topology and sweep methodology, CH4/CO/O2 in place of NC7H16/CO/O2.

.. image:: /_static/screenshots/continuous_reactor.png
   :width: 100%

`Launch in GitHub Codespaces <https://codespaces.new/parks4/boulder_examples?devcontainer_path=.devcontainer/continuous_reactor/devcontainer.json&quickstart=1>`_ — opens this example running in Boulder, forwarded port opens in your browser.

Or run locally:

.. code-block:: bash

   boulder examples/continuous_reactor.yaml --no-open

Custom SciPy ODE
----------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/custom.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/custom.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/custom.html <https://cantera.org/dev/examples/python/reactors/custom.html>`_
:Status: **unsupported**
:Reason: No ReactorNet; integrates ODEs directly with SciPy.

Extensible inertial wall reactor
--------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/custom2.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/custom2.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/custom2.html <https://cantera.org/dev/examples/python/reactors/custom2.html>`_
:Status: **unsupported**
:Reason: ExtensibleIdealGasReactor subclass with extra state is not rebuildable in Boulder.

Internal combustion engine cycle
--------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/ic_engine.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/ic_engine.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/ic_engine.html <https://cantera.org/dev/examples/python/reactors/ic_engine.html>`_
:Status: **unsupported**
:Reason: Valves and MFCs use time_function lambdas and moving piston walls.

Non-ideal shock tube ignition delay sweep
-----------------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/non_ideal_shock_tube.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/non_ideal_shock_tube.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/non_ideal_shock_tube.html <https://cantera.org/dev/examples/python/reactors/non_ideal_shock_tube.html>`_
:Status: **unsupported**
:Reason: Multi-temperature IDT sweep and real-gas phase switching are not static STONE.

Plug-flow reactor (two methods)
-------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/pfr.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/pfr.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/pfr.html <https://cantera.org/dev/examples/python/reactors/pfr.html>`_
:Status: **unsupported**
:Reason: Multiple ReactorNet objects and chain/Lagrangian algorithms are not one static YAML.

Moving piston with velocity wall
--------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/piston.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/piston.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/piston.html <https://cantera.org/dev/examples/python/reactors/piston.html>`_
:Status: **adapted**
:STONE: ``examples/piston.yaml``
:Mechanism: ``gri30.yaml``

Dual-mechanism piston (h2o2.yaml left / gri30.yaml right) driven purely by a Wall velocity callable -- no expansion_rate_coeff/heat_transfer_coeff at all. Wall velocity Func1s (Cantera 3.0+) always read back as the evaluated float at the network's current time (same limitation as MassFlowController.mass_flow_rate), so sim2stone recovers the closure from source via AST detection instead: a ``{closure: pressure_proportional, coeff, start_time}`` spec matching upstream's ``def v(t): if t < 0.1: return 0.0 else: return (r1.phase.P - r2.phase.P) * 1e-4``. Dual-mechanism itself needed no new work -- per-node mechanism overrides already existed (see reactor2.yaml).

.. image:: /_static/screenshots/piston.png
   :width: 100%

`Launch in GitHub Codespaces <https://codespaces.new/parks4/boulder_examples?devcontainer_path=.devcontainer/piston/devcontainer.json&quickstart=1>`_ — opens this example running in Boulder, forwarded port opens in your browser.

Or run locally:

.. code-block:: bash

   boulder examples/piston.yaml --no-open

Isothermal plasma electron balance
----------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/plasma.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/plasma.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/plasma.html <https://cantera.org/dev/examples/python/reactors/plasma.html>`_
:Status: **unsupported**
:Reason: No ReactorNet; SciPy ODE for electron density directly. Not representable as a static STONE network, but this class of custom-ODE model can be implemented in Boulder today via a plugin using boulder.CustomStageNetwork (https://parks4.github.io/boulder/_api/boulder/index.html#boulder.CustomStageNetwork), see the "Extending Boulder with plugins" section of usage.rst (https://github.com/parks4/boulder/blob/main/docs/usage.rst#extending-boulder-with-plugins).

Porous media burner cascade
---------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/porous_media_burner.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/porous_media_burner.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/porous_media_burner.html <https://cantera.org/dev/examples/python/reactors/porous_media_burner.html>`_
:Status: **unsupported**
:Reason: Custom ExtensibleIdealGasConstPressureReactor cascade with radiation.

Preconditioned multi-sector network
-----------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/preconditioned_network.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/preconditioned_network.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/preconditioned_network.html <https://cantera.org/dev/examples/python/reactors/preconditioned_network.html>`_
:Status: **unsupported**
:Reason: Multiple coupled networks and preconditioner benchmarking loops.

Sensitivity analysis
--------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/sensitivity1.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/sensitivity1.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/sensitivity1.html <https://cantera.org/dev/examples/python/reactors/sensitivity1.html>`_
:Status: **unsupported**
:Reason: ReactorNet sensitivity API is not represented in STONE.

Surface PFR (FlowReactor)
-------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/surf_pfr.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/surf_pfr.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/surf_pfr.html <https://cantera.org/dev/examples/python/reactors/surf_pfr.html>`_
:Status: **adapted**
:STONE: ``examples/surf_pfr.yaml``
:Mechanism: ``methane_pox_on_pt.yaml``

Real distance-marched ct.FlowReactor + ct.ReactorSurface (catalytic methane partial oxidation over Pt), not a chain-of-CSTRs approximation -- solved via solver.axis: distance (parks4/boulder#112). The adapter stops before the distance-marching loop (kept under `if False:`, same convention as piston.py's stepping guard) so sim2stone captures the true inlet state instead of the fully-converted outlet state. FlowReactor.mass_flow_rate is write-only in the Cantera 3.2 Python API; sim2stone recovers it from continuity (density x speed x area) instead of a direct read. Known gap: download_script_emitter.py doesn't support FlowReactor yet (a separate reactor-dispatch pathway from create_reactor_from_node), so the --download native-script test is skipped for this example -- YAML validation, normalization, and the real DualCanteraConverter solve all work correctly.

.. image:: /_static/screenshots/surf_pfr.png
   :width: 100%

`Launch in GitHub Codespaces <https://codespaces.new/parks4/boulder_examples?devcontainer_path=.devcontainer/surf_pfr/devcontainer.json&quickstart=1>`_ — opens this example running in Boulder, forwarded port opens in your browser.

Or run locally:

.. code-block:: bash

   boulder examples/surf_pfr.yaml --no-open

Surface PFR chain
-----------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/surf_pfr_chain.py <https://github.com/Cantera/cantera/blob/main/samples/python/reactors/surf_pfr_chain.py>`_
:Cantera docs: `https://cantera.org/dev/examples/python/reactors/surf_pfr_chain.html <https://cantera.org/dev/examples/python/reactors/surf_pfr_chain.html>`_
:Status: **unsupported**
:Reason: Repeated steady march with a ReactorSurface chain (a chain-of-WSRs approximation, as opposed to surf_pfr's real distance-marched FlowReactor, now supported -- see https://github.com/parks4/boulder/pull/112) is an algorithm, not static STONE: it re-solves the same WSR to steady state once per chain link, carrying the converged state forward as the next link's inlet. Out of scope for a single STONE description.

