# `formal/` — machine-verified Lean 4 proofs

This directory contains a standalone Lake project with the formal proofs behind Verifiable Labs's
reward-calibration stack. **The mathematics here is machine-verified.** The Python implementation in
`src/verifiable_labs_envs/formal_spec/` is property-tested against this specification — it is itself
**not** formally verified. The honest claim is described in the project root `README.md` under
"Formally verified guarantees".

All proofs in this directory are **`sorry`-free** and depend only on the three standard Lean
axioms: `propext`, `Classical.choice`, `Quot.sound`. You can verify any individual theorem with
`#print axioms <theorem_name>` inside a Lean session.

## Module map

| File | Headline theorems | Plain-English meaning |
|---|---|---|
| `VerifiableLabsFormal/CalibratedReward.lean` | `calibratedReward_bounded`, `calibratedReward_mono_V`, `calibratedReward_mono_C`, `calibratedReward_anti_H`, `calibratedReward_strict_anti_H` | The calibrated reward `R* = V·C − λ·H` lies in `[−λ, 1]`, increases in the value `V` and confidence `C`, and decreases in hackability `H` (strictly when `λ > 0`). |
| `VerifiableLabsFormal/VGS.lean` | `VGS_bounded`, `VGS_mono_{G,C,R,D}`, `VGS_anti_{H,K,L}`, `VGS_strict_mono_G` | The Verifiable Generalization Score `VGS = G·C·R·D − λH − μK − νL` is bounded in `[−(λ+μ+ν), 1]`, increases in every quality term, and decreases in every penalty term. |
| `VerifiableLabsFormal/AdaptiveDifficulty.lean` | `fixedPoint_iff_solve_rate_eq`, `exists_fixedPoint`, `stability_nonexpansive`, `stability_strict` | The difficulty update `d' = d + η(s − s*)` has a fixed point exactly when `s(d) = s*`; under antitone, `L`-Lipschitz solve-rate with `η·L < 1` the iteration is non-expansive around the fixed point, and strictly contracting away from it. |
| `VerifiableLabsFormal/VerifierInvariance.lean` | `invariant_preserves_correct`, `shortcut_violates_invariance`, `invariantSubgroup`, `invariant_of_generators` | Invariance of a verifier under a transformation pair `(T_X, T_A)` preserves correctness; a verifier that flips under an invariance is a shortcut; the set of invariant transformations forms a subgroup. |
| `VerifiableLabsFormal/ConformalCoverage.lean` ⭐ | `split_conformal_coverage`, `split_conformal_reward_coverage` | The split-conformal calibration set produces a residual interval that contains the true reward with probability at least `1 − α`, proved via order statistics and a leave-one-out exchangeability argument. *This is the proof anchoring our public reward-interval guarantee.* |
| `VerifiableLabsFormal/ModelRouting.lean` | `selected_model_optimal`, `cheaper_model_preferred`, `near_optimal_under_error` | The argmax of the utility `U = Q − γ·Cost − δ·Latency − ρ·Risk` is optimal; under `ε`-bounded utility estimation error the routed model is `2ε`-near-optimal. |
| `VerifiableLabsFormal/VerifiablePipeline.lean` | `pipeline_reward_bounded`, `pipeline_conformal_coverage`, `pipeline_difficulty_stable`, `pipeline_routing_near_optimal`, `pipeline_generalization_strict_mono`, 4 others | Composition theorem: the bundled pipeline output preserves every guarantee proved in the six modules above. |
| `VerifiableLabsFormal/SelfImprovementGate.lean` | `AcceptUpdate` definition, `accepted_sequence_mono_VGS`, `accepted_sequence_VGS_lower_bound` | A 7-condition checkpoint-acceptance predicate; any accepted sequence has VGS monotone non-decreasing, with `VGS_n ≥ VGS_0 + n·τ`. |
| `VerifiableLabsFormal/Main.lean` | — (no theorems) | Top-level option/scope file — heartbeat limits, `BigOperators` / `Classical` open, pretty-printer settings. Lake builds this to validate the configuration. |

## Provenance

Proofs authored and discharged by **[Aristotle](https://aristotle.harmonic.fun)** (Harmonic AI's
interactive theorem-proving system). Export checked into this repo on **2026-05-21**. Aristotle's
original Lake package was named `RequestProject`; the package and directory were renamed to
`VerifiableLabsFormal` on import. Proof content (the `.lean` files) is otherwise byte-identical to
the export — the only mechanical edits were the six `import RequestProject.X` →
`import VerifiableLabsFormal.X` lines inside `VerifiablePipeline.lean`. See `ARISTOTLE_SUMMARY.md`
for Aristotle's run-by-run authoring notes.

To credit Aristotle on PRs touching `formal/`, tag `@Aristotle-Harmonic` in the PR description.

## Toolchain pin

The Lean toolchain and Mathlib revision are pinned in `lean-toolchain` and `lake-manifest.json`
respectively:

| Component | Version |
|---|---|
| Lean | `leanprover/lean4:v4.28.0` |
| Mathlib | `v4.28.0`, git rev `8f9d9cff6bd728b17a24e163c9402775d9e6a365` |

**Do not bump versions without re-verifying every proof.** Mathlib bumps routinely refactor
identifiers used in proof scripts; a single rename inside `Mathlib.Probability` can break
`split_conformal_coverage` overnight. The CI workflow `formal-verification.yml` enforces a green
`lake build` on every push that touches `formal/**`.

## Local verification

```bash
# One-time: install elan (Lean version manager)
curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- -y --default-toolchain none
source ~/.elan/env

# Build (first run downloads ~1 GB of Mathlib oleans via the official cache)
cd formal/
lake exe cache get        # mandatory — without this, the build takes ~1 h instead of ~5 min
lake build

# Sorry-free check
! grep -rn '\bsorry\b' . --include='*.lean'

# Inspect axioms used by any theorem
lake env lean --run <(cat <<'EOF'
import VerifiableLabsFormal.ConformalCoverage
#print axioms split_conformal_coverage
EOF
)
# expected output: `split_conformal_coverage` depends on axioms: [propext, Classical.choice, Quot.sound]
```

## What this directory is and isn't

|   |   |
|---|---|
| ✅ Is | A machine-verified mathematical specification of the public guarantees Verifiable Labs claims (calibrated-reward bounds, conformal coverage, gate monotonicity, etc.). |
| ✅ Is | The source of truth that the Python module `src/verifiable_labs_envs/formal_spec/` mirrors and property-tests against. |
| ❌ Isn't | A proof of correctness of the Python code or the hosted API. The implementation is property-tested for parity with this spec; the implementation itself is not formally verified. |
| ❌ Isn't | A licence to write the phrases *"formally verified code"*, *"formally verified system"*, or *"formally verified API"* in any other documentation. Never make those claims. The only approved wording is in the project `README.md`. |

## Contamination-resistant clean-gate track

A second machine-verified track (modules **A–G**) extends the stack with the
mathematics behind Verifiable Labs's **contamination-resistant generated
evaluations** and **clean generalization gate**. Authored and discharged by
[Aristotle](https://aristotle.harmonic.fun); imported on **2026-06-12** with the
package/directory renamed from `RequestProject` to `VerifiableLabsFormal` (the
only mechanical edits were the six `import RequestProject.X` →
`import VerifiableLabsFormal.X` lines inside `CleanPipeline.lean`). All seven
files are **`sorry`-free** and depend only on the three standard axioms
(`propext`, `Classical.choice`, `Quot.sound`).

### Allowed public claim (the only approved wording for this track)

> "Selected mathematical properties behind Verifiable Labs' contamination-resistant
> promotion gate are machine-verified in Lean 4. The implementation is
> property-tested against the formal specification."

Equivalently, throughout the SDK: *machine-verified theorems in Lean 4;
implementation property-tested against the formal specification.*

### Forbidden claims (do NOT use)

- "The Verifiable Labs platform is formally verified."
- "Our code / API / system is formally verified."
- "We prove that the model generalizes."
- "We prove AGI safety."
- "We eliminate contamination completely."

### Scope and limitations

These results are mathematical properties of the scoring/gating layer over
abstract definitions (scores, risks, tolerances, timestamps). They are **not** a
verification of any software, API, model, or platform, and do not assert that
contamination is eliminated. The time/leakage results (module B) are
**per-checkpoint conditional** statements: *given* the stated assumption about
training-data membership, generated-after-freeze scenarios are clean for that
checkpoint — they reduce, but do not eliminate, leakage.

### Modules and namespaces

| File | Namespace |
|---|---|
| `VerifiableLabsFormal/ContaminationSplits.lean` | `Verifiable.ContaminationSplits` |
| `VerifiableLabsFormal/GeneratedAfterFreeze.lean` | `Verifiable.GeneratedAfterFreeze` |
| `VerifiableLabsFormal/ContaminationRisk.lean` | `Verifiable.ContaminationRisk` |
| `VerifiableLabsFormal/CleanVGS.lean` | `Verifiable.CleanVGS` |
| `VerifiableLabsFormal/GeneralizationGap.lean` | `Verifiable.GeneralizationGap` |
| `VerifiableLabsFormal/CleanPromotionGate.lean` | `Verifiable.CleanPromotionGate` |
| `VerifiableLabsFormal/CleanPipeline.lean` | `Verifiable.CleanPipeline` |

### Theorem table

| Module | Theorem | Plain-English meaning |
|---|---|---|
| A. ContaminationSplits | `hidden_eval_not_trainable` | A hidden-eval scenario under a valid policy is never trainable. |
| A. ContaminationSplits | `hidden_eval_not_public_release` | A hidden-eval scenario under a valid policy is never publicly released. |
| A. ContaminationSplits | `public_release_not_hidden` | A publicly released scenario is never a hidden-eval scenario. |
| A. ContaminationSplits | `split_disjoint_hidden_train` | A scenario cannot be both HiddenEval and Train. |
| A. ContaminationSplits | `split_disjoint_public_hidden` | A scenario cannot be both PublicDemo and HiddenEval. |
| B. GeneratedAfterFreeze | `generated_after_freeze_not_in_training` | A scenario generated after a checkpoint freeze (cutoff ≤ freeze) is not in that checkpoint's training data. |
| B. GeneratedAfterFreeze | `post_freeze_hidden_eval_clean_for_model` | A generated-after-freeze hidden eval is clean for that checkpoint, reducing leakage risk. |
| C. ContaminationRisk | `clean_score_bounds` | The contamination-adjusted score stays in [0,1]. |
| C. ContaminationRisk | `clean_score_le_raw` | Adjustment never increases the score. |
| C. ContaminationRisk | `clean_score_eq_raw_iff_zero_dcr_or_zero_raw` | No penalty exactly when no contamination risk or zero raw score. |
| C. ContaminationRisk | `clean_score_monotone_raw` | Higher raw score ⇒ higher clean score (fixed risk). |
| C. ContaminationRisk | `clean_score_antitone_dcr` | Higher contamination risk ⇒ lower clean score (fixed raw). |
| C. ContaminationRisk | `clean_score_zero_at_full_contamination` | Full contamination zeroes the score. |
| D. CleanVGS | `clean_vgs_le_raw_vgs` | Contamination-adjusted VGS never exceeds raw VGS. |
| D. CleanVGS | `clean_vgs_monotone_raw` | Higher raw VGS ⇒ higher clean VGS (fixed risk/penalty). |
| D. CleanVGS | `clean_vgs_antitone_dcr` | Higher contamination risk ⇒ lower clean VGS. |
| D. CleanVGS | `clean_vgs_penalizes_full_contamination` | Full contamination drives clean VGS to `-beta`. |
| E. GeneralizationGap | `positive_gap_implies_hidden_underperforms` | A positive public−hidden gap means hidden underperforms. |
| E. GeneralizationGap | `large_gap_implies_hidden_underperforms` | A large gap (τ ≥ 0) means hidden underperforms. |
| E. GeneralizationGap | `zero_gap_iff_equal` | Zero gap ⇔ equal public and hidden scores. |
| E. GeneralizationGap | `gap_bounded` | On [0,1] inputs the gap lies in [−1,1]. |
| E. GeneralizationGap | `reject_on_large_gap_sound` | Rejecting on a large gap is sound: rejected ⇒ hidden underperforms. |
| F. CleanPromotionGate | `accepted_update_improves_clean_vgs` | Accepted update improves clean VGS by ≥ τ. |
| F. CleanPromotionGate | `accepted_update_bounds_hack_risk` | Accepted update bounds the hack-risk increase. |
| F. CleanPromotionGate | `accepted_update_bounds_dcr` | Accepted update bounds the contamination-risk increase. |
| F. CleanPromotionGate | `accepted_update_no_regression` | Accepted update has no regression flag. |
| F. CleanPromotionGate | `accepted_sequence_clean_vgs_monotone` | A sequence of accepted updates is nondecreasing in clean VGS. |
| F. CleanPromotionGate | `accepted_sequence_clean_vgs_growth` | After n accepted updates, clean VGS ≥ initial + n·τ. |
| G. CleanPipeline | `clean_pipeline_acceptance_sound` | Gate acceptance entails ALL contamination-adjusted guarantees simultaneously — not public-score improvement alone. |

The Python mirror of this track lives in
`src/verifiable_labs_envs/formal_spec/` (modules `contamination_risk`,
`clean_vgs`, `generalization_gap`, `contamination_splits`,
`generated_after_freeze`, `clean_promotion_gate`, `clean_pipeline`) and is
property-tested against these theorems in `tests/formal_spec/`. The
`vlabs-prm-eval clean-gate` CLI command consumes eval cards through the same
predicate.
