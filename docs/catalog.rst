Example catalog
===============

Pinned upstream: ``https://github.com/Cantera/cantera`` ``samples/python/reactors`` @ ``main``.

See :doc:`boulder:stone` for the STONE YAML format and :doc:`boulder:cantera_upstream_examples` for solver mapping from upstream Cantera scripts. Networks are simulated with :class:`cantera.ReactorNet`.

Steady combustor residence time
-------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/combustor.py`
:Status: **generated**
:STONE: ``examples/combustor.yaml``
:Mechanism: ``gri30.yaml``

Steady-state WSR with residence-time MFC closure and continuation solver. Boulder Plots should show heat-release and temperature versus residence time.

.. image:: /_static/screenshots/combustor.png
   :width: 100%

Codespaces launch:

.. code-block:: bash

   boulder examples/combustor.yaml --no-open

Piston reactor with heat transfer
---------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/reactor2.py`
:Status: **generated**
:STONE: ``examples/reactor2.yaml``
:Mechanism: ``gri30.yaml``

Transient advance-grid example. Wall heat-transfer coefficients are only partially captured in STONE; plots focus on reactor temperature evolution.

.. image:: /_static/screenshots/reactor2.png
   :width: 100%

Codespaces launch:

.. code-block:: bash

   boulder examples/reactor2.yaml --no-open

Nanosecond pulse discharge
--------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/nanosecond_pulse_discharge.py`
:Status: **adapted**
:STONE: ``examples/nanosecond_pulse_discharge.yaml``
:Mechanism: ``example_data/methane-plasma-pavan-2023.yaml``

Plasma micro-step example with Gaussian reduced-electric-field signal.

.. image:: /_static/screenshots/nanosecond_pulse_discharge.png
   :width: 100%

Codespaces launch:

.. code-block:: bash

   boulder examples/nanosecond_pulse_discharge.yaml --no-open

Mixer with two inlet streams
----------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/mix1.py`
:Status: **generated**
:STONE: ``examples/mix1.yaml``
:Mechanism: ``gri30.yaml``

Dual-mechanism steady mixer with MFC and valve connections.

.. image:: /_static/screenshots/mix1.png
   :width: 100%

Codespaces launch:

.. code-block:: bash

   boulder examples/mix1.yaml --no-open

Constant-pressure ignition
--------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/reactor1.py`
:Status: **adapted**
:STONE: ``examples/reactor1.yaml``
:Mechanism: ``h2o2.yaml``

Single IdealGasConstPressureReactor with temperature advance limit and advance_grid transient integration.

.. image:: /_static/screenshots/reactor1.png
   :width: 100%

Codespaces launch:

.. code-block:: bash

   boulder examples/reactor1.yaml --no-open

Periodic CSTR
-------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/periodic_cstr.py`
:Status: **adapted**
:STONE: ``examples/periodic_cstr.yaml``
:Mechanism: ``h2o2.yaml``

CSTR with MFC, valve, and heat-transfer wall.

.. image:: /_static/screenshots/periodic_cstr.png
   :width: 100%

Codespaces launch:

.. code-block:: bash

   boulder examples/periodic_cstr.yaml --no-open

Fuel injection with Gaussian pulse
----------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/fuel_injection.py`
:Status: **adapted**
:STONE: ``examples/fuel_injection.yaml``
:Mechanism: ``nDodecane_Reitz.yaml``

Transient fuel pulse; Gaussian MFC signal when AST detection succeeds.

.. image:: /_static/screenshots/fuel_injection.png
   :width: 100%

Codespaces launch:

.. code-block:: bash

   boulder examples/fuel_injection.yaml --no-open

Preconditioned single-reactor integration
-----------------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/preconditioned_integration.py`
:Status: **unsupported**
:Reason: Requires example_data/n-heptane-NUIG-2016.yaml, which is not bundled in the Cantera 3.2 conda distribution used by Boulder CI.

1D packed bed (DAE)
-------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/1D_packed_bed.py`
:Status: **unsupported**
:Reason: Custom scikits.odes DAE packed-bed model; no global ReactorNet.

1D PFR surface chemistry
------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/1D_pfr_surfchem.py`
:Status: **unsupported**
:Reason: Uses FlowReactor and spatial surface chemistry not supported by Boulder.

Continuous reactor temperature sweep
------------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/continuous_reactor.py`
:Status: **unsupported**
:Reason: Outer temperature sweep and time-varying residence time are not one static STONE file.

Custom SciPy ODE
----------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/custom.py`
:Status: **unsupported**
:Reason: No ReactorNet; integrates ODEs directly with SciPy.

Extensible inertial wall reactor
--------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/custom2.py`
:Status: **unsupported**
:Reason: ExtensibleIdealGasReactor subclass with extra state is not rebuildable in Boulder.

Internal combustion engine cycle
--------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/ic_engine.py`
:Status: **unsupported**
:Reason: Valves and MFCs use time_function lambdas and moving piston walls.

Non-ideal shock tube ignition delay sweep
-----------------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/non_ideal_shock_tube.py`
:Status: **unsupported**
:Reason: Multi-temperature IDT sweep and real-gas phase switching are not static STONE.

Plug-flow reactor (two methods)
-------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/pfr.py`
:Status: **unsupported**
:Reason: Multiple ReactorNet objects and chain/Lagrangian algorithms are not one static YAML.

Moving piston with velocity wall
--------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/piston.py`
:Status: **unsupported**
:Reason: Wall velocity callable and dual-mechanism piston dynamics are not captured in STONE.

Isothermal plasma electron balance
----------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/plasma.py`
:Status: **unsupported**
:Reason: No ReactorNet; SciPy ODE for electron density.

Porous media burner cascade
---------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/porous_media_burner.py`
:Status: **unsupported**
:Reason: Custom ExtensibleIdealGasConstPressureReactor cascade with radiation.

Preconditioned multi-sector network
-----------------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/preconditioned_network.py`
:Status: **unsupported**
:Reason: Multiple coupled networks and preconditioner benchmarking loops.

Sensitivity analysis
--------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/sensitivity1.py`
:Status: **unsupported**
:Reason: ReactorNet sensitivity API is not represented in STONE.

Surface PFR (FlowReactor)
-------------------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/surf_pfr.py`
:Status: **unsupported**
:Reason: FlowReactor and FlowReactorSurface are unsupported in Boulder.

Surface PFR chain
-----------------

:Upstream: `https://github.com/Cantera/cantera/blob/main/samples/python/reactors/surf_pfr_chain.py`
:Status: **unsupported**
:Reason: Repeated steady march with ReactorSurface chain is an algorithm, not static STONE.

