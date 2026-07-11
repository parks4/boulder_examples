.PHONY: conda-env-update test docs-build qa screenshot refresh-manifest

CONDA_ENV ?= boulder-examples

conda-env-update:
	conda env update -n $(CONDA_ENV) -f environment.yml --prune

test:
	python -m pytest tests -vv

docs-build:
	python scripts/build_catalog_rst.py
	cd docs && python -m sphinx -b html . _build/html $(SPHINXOPTS)

qa:
	ruff check .
	ruff format --check .

screenshot:
	python scripts/capture_screenshots.py

refresh-manifest:
	python scripts/generate_examples.py
