# vlabs-formal

Lean 4 formal track for the Verifiable Labs promotion gate, plus its Python
property-test mirror.

Selected mathematical properties behind the contamination-resistant promotion gate are machine-verified in Lean 4. A hand-maintained Python mirror has property tests derived from selected definitions; no mechanized code-to-proof parity is claimed.

The development is maintained in this repository:

| Component | Current location |
|---|---|
| Lean 4 modules (16 files, zero `sorry`; Lean + Mathlib pinned to v4.28.0) | `formal/VerifiableLabsFormal/` |
| Python mirror source (packaged as `vlabs_formal.formal_spec`) | `src/verifiable_labs_envs/formal_spec/` |
| Property tests binding the mirror to the spec (70+ for the clean track) | `tests/formal_spec/` |
| CI: `lake build` + zero-`sorry` check | `.github/workflows/formal-verification.yml` |

## Install and locate the Lean sources

From a checkout:

```bash
python -m pip install .
python -c "import vlabs_formal; print(vlabs_formal.formal_root())"
```

The wheel includes all 16 Lean modules, `lakefile.toml`, `lake-manifest.json`,
and `lean-toolchain` under `vlabs_formal/lean`. Its property-tested mirror is
packaged under `vlabs_formal.formal_spec`; production integrations should use
`vlabs_sdk.formal_spec` from `vlabs-sdk`. The wheel deliberately does **not**
publish `verifiable_labs_envs`, because that namespace belongs to the SDK and
shipping it from two distributions creates order-dependent imports.

What is — and is not — claimed: the Lean development covers selected
mathematical properties of the gate (monotonicity, bounds, decision
soundness of the defined predicates). It does not cover the surrounding
service code, and we do not claim it does.

## License

Apache-2.0.
