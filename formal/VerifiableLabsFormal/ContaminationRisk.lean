import Mathlib

/-!
# ContaminationRisk

Module **C** of the contamination-resistant evaluation track.

Given a raw score `raw ∈ [0,1]` and a *data-contamination-risk* score
`dcr ∈ [0,1]`, the contamination-adjusted (clean) score is

```
clean_score raw dcr = raw * (1 - dcr).
```

We prove boundedness, the penalty inequality `clean_score ≤ raw`, an exact
characterization of equality, monotonicity in `raw`, anti-monotonicity in `dcr`,
and the full-contamination collapse to zero.
-/

namespace Verifiable.ContaminationRisk

/-- Contamination-adjusted score. -/
def clean_score (raw dcr : ℝ) : ℝ := raw * (1 - dcr)

/-- **C.1** The clean score stays in `[0,1]`. -/
theorem clean_score_bounds {raw dcr : ℝ}
    (hraw0 : 0 ≤ raw) (hraw1 : raw ≤ 1) (hdcr0 : 0 ≤ dcr) (hdcr1 : dcr ≤ 1) :
    0 ≤ clean_score raw dcr ∧ clean_score raw dcr ≤ 1 := by
  unfold clean_score
  constructor
  · nlinarith
  · nlinarith

/-- **C.2** The clean score never exceeds the raw score. -/
theorem clean_score_le_raw {raw dcr : ℝ}
    (hraw0 : 0 ≤ raw) (hdcr0 : 0 ≤ dcr) :
    clean_score raw dcr ≤ raw := by
  unfold clean_score
  nlinarith

/-- **C.3** The clean score equals the raw score exactly when there is no
contamination risk or the raw score is zero. -/
theorem clean_score_eq_raw_iff_zero_dcr_or_zero_raw {raw dcr : ℝ} :
    clean_score raw dcr = raw ↔ (raw = 0 ∨ dcr = 0) := by
  unfold clean_score
  constructor
  · intro h
    have hmul : raw * dcr = 0 := by nlinarith [h]
    rcases mul_eq_zero.mp hmul with h0 | h0
    · exact Or.inl h0
    · exact Or.inr h0
  · rintro (h0 | h0) <;> rw [h0] <;> ring

/-- **C.4** For a fixed contamination risk in `[0,1]`, the clean score is
monotone (nondecreasing) in the raw score. -/
theorem clean_score_monotone_raw {raw₁ raw₂ dcr : ℝ}
    (hdcr1 : dcr ≤ 1) (hle : raw₁ ≤ raw₂) :
    clean_score raw₁ dcr ≤ clean_score raw₂ dcr := by
  unfold clean_score
  nlinarith

/-- **C.5** For a fixed nonnegative raw score, the clean score is anti-monotone
(nonincreasing) in the contamination risk. -/
theorem clean_score_antitone_dcr {raw dcr₁ dcr₂ : ℝ}
    (hraw0 : 0 ≤ raw) (hle : dcr₁ ≤ dcr₂) :
    clean_score raw dcr₂ ≤ clean_score raw dcr₁ := by
  unfold clean_score
  nlinarith

/-- **C.6** At full contamination (`dcr = 1`) the clean score collapses to 0. -/
theorem clean_score_zero_at_full_contamination {raw : ℝ} :
    clean_score raw 1 = 0 := by
  unfold clean_score; ring

end Verifiable.ContaminationRisk
