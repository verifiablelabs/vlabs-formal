import Mathlib

/-!
# Calibrated Reward Function

We formalize properties of the calibrated reward function:

  R*(x,a) = V(x,a) · C(x,a) - λ · H(x,a)

where:
- V(x,a) ∈ [0,1] is a verifier correctness score,
- C(x,a) ∈ [0,1] is a calibration confidence,
- H(x,a) ∈ [0,1] is a hackability risk,
- λ ≥ 0 is a regularization parameter.

We prove:
1. R* is bounded in [-λ, 1].
2. R* is monotone increasing in V and C.
3. R* is monotone decreasing in H.
4. If two answers share V and C but differ in hackability, the more hackable answer
   receives a strictly lower reward.
-/

noncomputable section

/-- The calibrated reward function R*(V, C, H, lam) = V * C - lam * H. -/
def calibratedReward (V C H lam : ℝ) : ℝ := V * C - lam * H

/-! ## Part 1: Boundedness -/

/-- The calibrated reward is at least -λ. Only the non-negativity of V, C and the
upper bound H ≤ 1 are needed (together with λ ≥ 0). -/
theorem calibratedReward_lower_bound
    {V C H lam : ℝ}
    (hV0 : 0 ≤ V) (hC0 : 0 ≤ C)
    (hH1 : H ≤ 1)
    (hlam : 0 ≤ lam) :
    -lam ≤ calibratedReward V C H lam := by
  unfold calibratedReward; nlinarith [mul_le_mul_of_nonneg_left hH1 hlam]

/-- The calibrated reward is at most 1. Only V ≤ 1, C ∈ [0,1], H ≥ 0, and λ ≥ 0
are needed. -/
theorem calibratedReward_upper_bound
    {V C H lam : ℝ}
    (hV1 : V ≤ 1)
    (hC0 : 0 ≤ C) (hC1 : C ≤ 1)
    (hH0 : 0 ≤ H)
    (hlam : 0 ≤ lam) :
    calibratedReward V C H lam ≤ 1 := by
  exact sub_le_self _ (by positivity) |>.trans (mul_le_one₀ hV1 hC0 hC1)

/-- R* is bounded in [-λ, 1], assuming V, C, H ∈ [0,1] and λ ≥ 0. -/
theorem calibratedReward_bounded
    {V C H lam : ℝ}
    (hV0 : 0 ≤ V) (hV1 : V ≤ 1)
    (hC0 : 0 ≤ C) (hC1 : C ≤ 1)
    (hH0 : 0 ≤ H) (hH1 : H ≤ 1)
    (hlam : 0 ≤ lam) :
    calibratedReward V C H lam ∈ Set.Icc (-lam) 1 :=
  ⟨calibratedReward_lower_bound hV0 hC0 hH1 hlam,
   calibratedReward_upper_bound hV1 hC0 hC1 hH0 hlam⟩

/-! ## Part 2: Monotonicity in V and C -/

/-- R* is monotone increasing in V (with C, H, λ fixed). -/
theorem calibratedReward_mono_V
    {V₁ V₂ C H lam : ℝ}
    (hC0 : 0 ≤ C)
    (hVle : V₁ ≤ V₂) :
    calibratedReward V₁ C H lam ≤ calibratedReward V₂ C H lam := by
  unfold calibratedReward; nlinarith [mul_le_mul_of_nonneg_right hVle hC0]

/-- R* is monotone increasing in C (with V, H, λ fixed). -/
theorem calibratedReward_mono_C
    {V C₁ C₂ H lam : ℝ}
    (hV0 : 0 ≤ V)
    (hCle : C₁ ≤ C₂) :
    calibratedReward V C₁ H lam ≤ calibratedReward V C₂ H lam :=
  sub_le_sub_right (mul_le_mul_of_nonneg_left hCle hV0) _

/-! ## Part 3: Monotone decreasing in H -/

/-- R* is monotone decreasing in H (with V, C, λ fixed). -/
theorem calibratedReward_anti_H
    {V C H₁ H₂ lam : ℝ}
    (hlam : 0 ≤ lam)
    (hHle : H₁ ≤ H₂) :
    calibratedReward V C H₂ lam ≤ calibratedReward V C H₁ lam :=
  sub_le_sub_left (mul_le_mul_of_nonneg_left hHle hlam) _

/-! ## Part 4: Higher hackability ⟹ strictly lower reward -/

/-- If two answers have equal V and C but H₁ > H₂, answer 1 gets strictly lower reward.
Note: this requires λ > 0 (strict positivity). -/
theorem calibratedReward_strict_anti_H
    {V C H₁ H₂ lam : ℝ}
    (hlampos : 0 < lam)
    (hHlt : H₂ < H₁) :
    calibratedReward V C H₁ lam < calibratedReward V C H₂ lam :=
  sub_lt_sub_left (mul_lt_mul_of_pos_left hHlt hlampos) _

end
