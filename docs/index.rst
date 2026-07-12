Boulder Examples
================

Catalog of `Cantera reactor-network samples`_ expressed as Boulder
:doc:`STONE <boulder:stone>` YAML files.

Runnable examples may include GUI screenshots in the catalog when present under
``docs/_static/screenshots/``.
YAML files are generated with :doc:`Boulder's sim2stone workflow <boulder:usage>` from
vendored upstream scripts (see :doc:`contributing`).

Related documentation
---------------------

* :doc:`Boulder user guide <boulder:usage>` — CLI, headless export, and plugins
* :doc:`STONE specification <boulder:stone>` — YAML network format
* :doc:`Cantera upstream examples in Boulder <boulder:cantera_upstream_examples>`
* `Cantera user guide <https://cantera.org/stable/userguide/index.html>`__
* `Cantera Python reactor samples <https://github.com/Cantera/cantera/tree/main/samples/python/reactors>`__

Each runnable catalog entry builds a :class:`cantera.ReactorNet` from an upstream script
using :class:`~boulder.cantera_converter.DualCanteraConverter` (see :doc:`boulder:usage`).

.. _Cantera reactor-network samples: https://github.com/Cantera/cantera/tree/main/samples/python/reactors

.. toctree::
   :maxdepth:  2
   :caption: Catalog

   catalog
   contributing

Launch in Codespaces
--------------------

Open `this repository in a Codespace`_ and run::

   boulder examples/<example>.yaml --no-open

.. _this repository in a Codespace: https://github.com/codespaces/new?hide_repo_select=true&repo=parks4/boulder_examples
