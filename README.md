# Boulder Examples

Official [Boulder](https://github.com/parks4/boulder) example catalog derived from the
[Cantera Python reactor samples](https://github.com/Cantera/cantera/tree/main/samples/python/reactors).

Each runnable example is provided as a **STONE YAML** file that opens in the Boulder GUI.
Unsupported upstream samples are listed in the catalog with an explicit technical reason.

## How examples are generated

Runnable YAML files under `examples/` are produced with Boulder’s `sim2stone` tool:

```bash
sim2stone upstream/cantera/reactors/<script>.py -o examples/<name>.yaml --mechanism <mech>
```

Or regenerate the whole runnable set:

```bash
python scripts/generate_examples.py
```

Upstream scripts are vendored unchanged under `upstream/cantera/reactors/` at a pinned
Cantera commit recorded in [`examples/manifest.yaml`](examples/manifest.yaml).

## Quick start (Conda)

```bash
conda env create -n boulder-examples -f environment.yml
conda activate boulder-examples
make test
make docs-build
```

Launch an example in the GUI:

```bash
boulder examples/combustor.yaml --no-open
```

Headless download of the generated Cantera Python script:

```bash
boulder examples/reactor2.yaml --headless --download /tmp/reactor2.py
python /tmp/reactor2.py
```

## GitHub Codespaces

Open this repository in a Codespace (`.devcontainer/`) and run:

```bash
boulder examples/<example>.yaml --no-open
```

The online docs at GitHub Pages include per-example Codespaces launch links.

## Documentation

Sphinx docs live under `docs/`. The catalog lists upstream provenance, adaptation
notes, and Codespaces launch commands for each example.

## Testing

```bash
make test
```

Integration tests assert that every runnable YAML validates and that Boulder’s headless
`--download` Python script executes successfully (with documented skips for known-hard cases).

## License

MIT — see [LICENSE](LICENSE). Vendored Cantera samples remain under their upstream
BSD-3-Clause license in the `upstream/` tree.
