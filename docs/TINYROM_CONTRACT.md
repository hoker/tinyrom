# tinyrom Contract

tinyrom is the low-level ROM math engine.

tinyrom owns:

- Loading ROM bytes.
- Loading TOML definitions.
- Exposing raw NumPy views.
- Applying `real = raw * factor + offset`.
- Reversing math for patching.
- Saving ROM bytes.

tinyrom does not own:

- Application workflows.
- Project-specific tuning policy.
- UI.
- Undo/redo.
- Flashing.
- Tuning strategy.

Downstream tools should treat tinyrom as a deterministic library: inspect bytes, compute maps, compute patches, and save only when explicitly requested by their own application flow.
