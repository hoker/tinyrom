# tinyrom

tinyrom is a brutalist, math-first ROM calibration core. It keeps the engine small, deterministic, and local: load ROM bytes, project NumPy views over them, apply `Real World = (Raw * Factor) + Offset`, and save the result.

The core engine is intentionally tiny: `src/tinyrom/core.py` is under 100 lines and does only the essential work.

## Philosophy

tinyrom keeps calibration work close to the bytes and close to the math. The project favors plain files, direct memory views, and deterministic transformations that are easy to inspect.

- Zero bloat, zero-copy.
- TOML as the working schema.
- Deterministic Python math instead of opaque tooling behavior.
- Local-first workflows.

The guiding formula stays:

```text
Real World = (Raw * Factor) + Offset
```

## Repository Layout

Public source and fixtures live here:

- `src/tinyrom/` contains the package surface for contributors.
- `examples/` contains synthetic or redistributable fixtures.
- `tests/` contains regression tests for the core.
- `docs/TINYROM_CONTRACT.md` defines the core library contract.

Compatibility scripts remain at the repo root while the project is being cleaned up, but contributors should treat `src/tinyrom/` as the durable package home.

## Quickstart

Use Python 3.11 or newer:

```bash
python3 --version
```

Install tinyrom for local development:

```bash
python3 -m pip install -e .
```

Run the tests:

```bash
python3 -m unittest tests.test_core
```

Read sample maps:

```bash
python3 examples/read_maps.py
```

Patch a copied map and write a new ROM:

```bash
python3 examples/patch_copy.py
```

Convert a TunerPro XDF XML export into tinyrom TOML (synthetic fixture matches `definitions.toml`):

```bash
tinyrom-xdf2toml examples/definitions.xdf /tmp/definitions.toml
```

## Scope

tinyrom owns:

- ROM byte loading and saving
- TOML-driven map math
- XDF XML to TOML conversion

tinyrom does not own:

- application workflows
- user interfaces
- project-specific tuning policy
- flashing workflows

## Open Source Notes

Do not commit proprietary ROMs, XDFs, passwords, vendor installers, or TunerPro artifacts. The public repo should contain source code, docs, tests, and clean fixtures only.
