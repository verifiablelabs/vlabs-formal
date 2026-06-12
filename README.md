# vlabs-formal

Lean 4 formal track for the Verifiable Labs promotion gate, plus its Python
property-test mirror.

Selected mathematical properties behind the contamination-resistant promotion gate are machine-verified in Lean 4. The implementation is property-tested against the formal specification.

**Status: pointer repository.** The development is open source today in
[verifiable-labs-envs](https://github.com/verifiablelabs/verifiable-labs-envs):

| Component | Current location |
|---|---|
| Lean 4 modules (16 files, zero `sorry`; Lean + Mathlib pinned to v4.28.0) | `formal/VerifiableLabsFormal/` |
| Python mirror of the formal definitions (clean score, CleanVGS, generalization gap, 8-condition promotion gate) | `src/verifiable_labs_envs/formal_spec/` |
| Property tests binding the mirror to the spec (70+ for the clean track) | `tests/formal_spec/` |
| CI: `lake build` + zero-`sorry` check | `.github/workflows/formal-verification.yml` |

What is — and is not — claimed: the Lean development covers selected
mathematical properties of the gate (monotonicity, bounds, decision
soundness of the defined predicates). It does not cover the surrounding
service code, and we do not claim it does.

## License

Apache-2.0.
