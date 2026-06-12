import Mathlib

/-!
# CleanVGS

Module **D** of the contamination-resistant evaluation track.

The contamination-adjusted Verifiable Generalization Score is

```
clean_vgs raw_vgs dcr beta = raw_vgs * (1 - dcr) - beta * dcr,
```

where `raw_vgs ∈ [0,1]`, `dcr ∈ [0,1]` is the data-contamination-risk score, and
`beta ≥ 0` is a contamination penalty weight.

We prove the penalty inequality, monotonicity in `raw_vgs`, anti-monotonicity in
`dcr`, and the full-contamination collapse to `-beta`.
-/

namespace Verifiable.CleanVGS

/-- Contamination-adjusted VGS. -/
def clean_vgs (raw_vgs dcr beta : ℝ) : ℝ := raw_vgs * (1 - dcr) - beta * dcr

/-- **D.1** The clean VGS never exceeds the raw VGS. -/
theorem clean_vgs_le_raw_vgs {raw_vgs dcr beta : ℝ}
    (hraw0 : 0 ≤ raw_vgs) (hdcr0 : 0 ≤ dcr) (hbeta0 : 0 ≤ beta) :
    clean_vgs raw_vgs dcr beta ≤ raw_vgs := by
  unfold clean_vgs
  nlinarith

/-- **D.2** For fixed contamination risk in `[0,1]` and penalty, the clean VGS is
monotone (nondecreasing) in the raw VGS. -/
theorem clean_vgs_monotone_raw {raw₁ raw₂ dcr beta : ℝ}
    (hdcr1 : dcr ≤ 1) (hle : raw₁ ≤ raw₂) :
    clean_vgs raw₁ dcr beta ≤ clean_vgs raw₂ dcr beta := by
  unfold clean_vgs
  nlinarith

/-- **D.3** For fixed nonnegative raw VGS and penalty, the clean VGS is
anti-monotone (nonincreasing) in the contamination risk. -/
theorem clean_vgs_antitone_dcr {raw_vgs dcr₁ dcr₂ beta : ℝ}
    (hraw0 : 0 ≤ raw_vgs) (hbeta0 : 0 ≤ beta) (hle : dcr₁ ≤ dcr₂) :
    clean_vgs raw_vgs dcr₂ beta ≤ clean_vgs raw_vgs dcr₁ beta := by
  unfold clean_vgs
  nlinarith

/-- **D.4** At full contamination (`dcr = 1`) the clean VGS collapses to the
penalty `-beta`. -/
theorem clean_vgs_penalizes_full_contamination {raw_vgs beta : ℝ} :
    clean_vgs raw_vgs 1 beta = -beta := by
  unfold clean_vgs; ring

end Verifiable.CleanVGS
