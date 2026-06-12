import Mathlib

noncomputable section

/-!
# Adaptive Difficulty Update

We formalize the adaptive difficulty update rule:

  d_{t+1} = d_t + η (s_t - s*)

where:
- d_t ∈ ℝ is difficulty at time t
- s_t ∈ [0,1] is observed solve rate
- s* ∈ (0,1) is target solve rate
- η > 0 is the learning rate

We prove:
1. A fixed point d* of the update satisfies s(d*) = s*.
2. Existence of such a fixed point when s is continuous and strictly decreasing
   with appropriate range (via IVT).
3. Local stability: the update is non-expansive (and strictly contracting for d ≠ d*)
   when s is antitone, Lipschitz, and η is sufficiently small.
-/

/-- The adaptive difficulty update rule. -/
def difficultyUpdate (η s_star s_t d_t : ℝ) : ℝ :=
  d_t + η * (s_t - s_star)

/-
**Fixed point characterization**: d* is a fixed point of the update rule
if and only if s(d*) = s*, provided η > 0.
-/
theorem fixedPoint_iff_solve_rate_eq (η : ℝ) (hη : η > 0) (s : ℝ → ℝ)
    (s_star d_star : ℝ) :
    difficultyUpdate η s_star (s d_star) d_star = d_star ↔ s d_star = s_star := by
  constructor <;> intro h <;> unfold difficultyUpdate at * <;> nlinarith

/-
**Existence of fixed point**: If s is continuous and strictly decreasing,
and there exist points a < b with s(a) > s* > s(b), then there exists
a fixed point d* ∈ (a, b) with s(d*) = s*.
-/
theorem exists_fixedPoint (s : ℝ → ℝ) (hs_cont : Continuous s)
    (s_star : ℝ) (a b : ℝ) (hab : a < b)
    (ha : s_star < s a) (hb : s b < s_star) :
    ∃ d_star ∈ Set.Ioo a b, s d_star = s_star := by
  apply_rules [ intermediate_value_Ioo', hs_cont.continuousOn ];
  · linarith;
  · constructor <;> linarith

/-
**Stability (non-expansive)**: If s is antitone and L-Lipschitz with η * L < 1,
then the update is non-expansive around the fixed point d*, i.e.,
|d_{t+1} - d*| ≤ |d_t - d*|.
-/
theorem stability_nonexpansive (s : ℝ → ℝ) (hs_anti : Antitone s)
    (L : ℝ)
    (hs_lip : ∀ x y : ℝ, |s x - s y| ≤ L * |x - y|)
    (η : ℝ) (hη : η > 0) (hηL : η * L < 1)
    (s_star d_star : ℝ) (hfp : s d_star = s_star)
    (d : ℝ) :
    |difficultyUpdate η s_star (s d) d - d_star| ≤ |d - d_star| := by
  cases abs_cases ( d - d_star ) <;> cases abs_cases ( s d - s d_star ) <;> simp +decide [ *, abs_le, sub_eq_add_neg, difficultyUpdate ];
  · constructor <;> cases abs_cases ( d + -d_star ) <;> nlinarith [ hs_anti ( show d ≥ d_star by linarith ) ];
  · constructor <;> cases abs_cases ( d + -d_star ) <;> nlinarith [ abs_le.mp ( hs_lip d d_star ) ];
  · constructor <;> cases abs_cases ( d + -d_star ) <;> nlinarith [ abs_le.mp ( hs_lip d d_star ) ];
  · constructor <;> cases abs_cases ( d + -d_star ) <;> nlinarith [ hs_anti ( show d ≤ d_star from by linarith ), hs_lip d d_star ]

/-
**Strict stability**: If s is strictly antitone and L-Lipschitz with η * L < 1,
then the update is strictly contracting for d ≠ d*, i.e.,
|d_{t+1} - d*| < |d_t - d*|.
-/
theorem stability_strict (s : ℝ → ℝ) (hs_anti : StrictAnti s)
    (L : ℝ)
    (hs_lip : ∀ x y : ℝ, |s x - s y| ≤ L * |x - y|)
    (η : ℝ) (hη : η > 0) (hηL : η * L < 1)
    (s_star d_star : ℝ) (hfp : s d_star = s_star)
    (d : ℝ) (hd : d ≠ d_star) :
    |difficultyUpdate η s_star (s d) d - d_star| < |d - d_star| := by
  unfold difficultyUpdate;
  cases abs_cases ( d + η * ( s d - s_star ) - d_star ) <;> cases abs_cases ( d - d_star ) <;> cases lt_or_gt_of_ne hd <;> nlinarith [ hs_anti <| ‹_›, abs_le.mp ( hs_lip d d_star ) ]

end