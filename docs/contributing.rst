Contributing
============

Regenerating STONE YAML
-----------------------

1. Ensure the ``boulder-examples`` Conda environment is active.
2. Refresh vendored upstream scripts::

      python scripts/download_upstream.py

3. Regenerate runnable YAML files::

      python scripts/generate_examples.py

4. Run validation tests::

      make test

Refreshing GUI screenshots
--------------------------

Screenshots are committed under ``docs/_static/screenshots/`` and embedded in the
generated catalog page. They are captured **after** the network is solved and the
**Plots** tab is selected in the Boulder GUI.

::

   pip install playwright
   playwright install chromium
   make screenshot

Each screenshot should reproduce the upstream Cantera example curves as closely as the
static STONE adaptation allows. Document any divergence in ``examples/manifest.yaml``.
