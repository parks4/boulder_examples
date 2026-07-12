Contributing
============

Regenerating STONE YAML
-----------------------

1. Ensure the ``boulder-examples`` Conda environment is active.
2. Refresh vendored upstream scripts::

      python scripts/download_upstream.py

3. Regenerate runnable YAML files with :doc:`sim2stone <boulder:usage>` (via
   ``scripts/generate_examples.py``)::

      python scripts/generate_examples.py

4. Run validation tests::

      make test

Generated YAML must conform to the :doc:`STONE format <boulder:stone>`. For solver
mapping notes (``solve_steady``, ``advance_grid``, ``micro_step``, etc.) see
:doc:`boulder:cantera_upstream_examples`.

See also
--------

* :doc:`Boulder installation <boulder:installation>`
* `Cantera install guide <https://cantera.org/stable/install/index.html>`__
