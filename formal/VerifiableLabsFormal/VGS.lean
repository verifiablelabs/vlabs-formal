import Mathlib

/-!
# Verifiable Generalization Score (VGS)

We formalize properties of the Verifiable Generalization Score:

  VGS = G · C · R · D - λ · H - μ · K - ν · L

where:
- G, C, R, D ∈ [0,1] are quality terms (held-out generalization, calibration,
  reproducibility, diversity),
- H, K, L ∈ [0,1] are penalty terms (hackability, knowledge leakage, label noise),
- λ, μ, ν ≥ 0 are regularization weights.

We prove:
1. VGS is bounded in [-(λ + μ + ν), 1].
2. VGS is monotone increasing in each of G, C, R, D.
3. VGS is monotone decreasing in each of H, K, L.
4. Increasing G strictly increases VGS when C, R, D > 0.
-/

noncomputable section

/-- The Verifiable Generalization Score. -/
def VGS (G C R D H K L lam mu nu : ℝ) : ℝ :=
  G * C * R * D - lam * H - mu * K - nu * L

/-! ## Part 1: Boundedness -/

theorem VGS_lower_bound
    {G C R D H K L lam mu nu : ℝ}
    (hG0 : 0 ≤ G) (hC0 : 0 ≤ C) (hR0 : 0 ≤ R) (hD0 : 0 ≤ D)
    (hH1 : H ≤ 1) (hK1 : K ≤ 1) (hL1 : L ≤ 1)
    (hlam : 0 ≤ lam) (hmu : 0 ≤ mu) (hnu : 0 ≤ nu) :
    -(lam + mu + nu) ≤ VGS G C R D H K L lam mu nu := by
  unfold VGS; nlinarith [ show 0 ≤ G * C * R * D by positivity ] ;

theorem VGS_upper_bound
    {G C R D H K L lam mu nu : ℝ}
    (hG1 : G ≤ 1) (hC0 : 0 ≤ C) (hC1 : C ≤ 1)
    (hR0 : 0 ≤ R) (hR1 : R ≤ 1) (hD0 : 0 ≤ D) (hD1 : D ≤ 1)
    (hH0 : 0 ≤ H) (hK0 : 0 ≤ K) (hL0 : 0 ≤ L)
    (hlam : 0 ≤ lam) (hmu : 0 ≤ mu) (hnu : 0 ≤ nu) :
    VGS G C R D H K L lam mu nu ≤ 1 := by
  unfold VGS; nlinarith [ show C * R * D ≥ 0 by positivity, show C * R * D ≤ 1 by exact mul_le_one₀ ( mul_le_one₀ hC1 hR0 hR1 ) hD0 hD1 ] ;

theorem VGS_bounded
    {G C R D H K L lam mu nu : ℝ}
    (hG0 : 0 ≤ G) (hG1 : G ≤ 1)
    (hC0 : 0 ≤ C) (hC1 : C ≤ 1)
    (hR0 : 0 ≤ R) (hR1 : R ≤ 1)
    (hD0 : 0 ≤ D) (hD1 : D ≤ 1)
    (hH0 : 0 ≤ H) (hH1 : H ≤ 1)
    (hK0 : 0 ≤ K) (hK1 : K ≤ 1)
    (hL0 : 0 ≤ L) (hL1 : L ≤ 1)
    (hlam : 0 ≤ lam) (hmu : 0 ≤ mu) (hnu : 0 ≤ nu) :
    VGS G C R D H K L lam mu nu ∈ Set.Icc (-(lam + mu + nu)) 1 :=
  ⟨VGS_lower_bound hG0 hC0 hR0 hD0 hH1 hK1 hL1 hlam hmu hnu,
   VGS_upper_bound hG1 hC0 hC1 hR0 hR1 hD0 hD1 hH0 hK0 hL0 hlam hmu hnu⟩

/-! ## Part 2: Monotone increasing in G, C, R, D -/

theorem VGS_mono_G
    {G₁ G₂ C R D H K L lam mu nu : ℝ}
    (hC0 : 0 ≤ C) (hR0 : 0 ≤ R) (hD0 : 0 ≤ D)
    (hle : G₁ ≤ G₂) :
    VGS G₁ C R D H K L lam mu nu ≤ VGS G₂ C R D H K L lam mu nu := by
  unfold VGS;
  gcongr

theorem VGS_mono_C
    {G C₁ C₂ R D H K L lam mu nu : ℝ}
    (hG0 : 0 ≤ G) (hR0 : 0 ≤ R) (hD0 : 0 ≤ D)
    (hle : C₁ ≤ C₂) :
    VGS G C₁ R D H K L lam mu nu ≤ VGS G C₂ R D H K L lam mu nu := by
  unfold VGS; nlinarith [ mul_nonneg hG0 ( mul_nonneg hR0 hD0 ) ] ;

theorem VGS_mono_R
    {G C R₁ R₂ D H K L lam mu nu : ℝ}
    (hG0 : 0 ≤ G) (hC0 : 0 ≤ C) (hD0 : 0 ≤ D)
    (hle : R₁ ≤ R₂) :
    VGS G C R₁ D H K L lam mu nu ≤ VGS G C R₂ D H K L lam mu nu := by
  unfold VGS; nlinarith [ show 0 ≤ G * C * D by positivity ] ;

theorem VGS_mono_D
    {G C R D₁ D₂ H K L lam mu nu : ℝ}
    (hG0 : 0 ≤ G) (hC0 : 0 ≤ C) (hR0 : 0 ≤ R)
    (hle : D₁ ≤ D₂) :
    VGS G C R D₁ H K L lam mu nu ≤ VGS G C R D₂ H K L lam mu nu := by
  unfold VGS; nlinarith [ mul_nonneg hG0 ( mul_nonneg hC0 hR0 ) ] ;

/-! ## Part 3: Monotone decreasing in H, K, L -/

theorem VGS_anti_H
    {G C R D H₁ H₂ K L lam mu nu : ℝ}
    (hlam : 0 ≤ lam)
    (hle : H₁ ≤ H₂) :
    VGS G C R D H₂ K L lam mu nu ≤ VGS G C R D H₁ K L lam mu nu := by
  unfold VGS; nlinarith;

theorem VGS_anti_K
    {G C R D H K₁ K₂ L lam mu nu : ℝ}
    (hmu : 0 ≤ mu)
    (hle : K₁ ≤ K₂) :
    VGS G C R D H K₂ L lam mu nu ≤ VGS G C R D H K₁ L lam mu nu := by
  unfold VGS; nlinarith;

theorem VGS_anti_L
    {G C R D H K L₁ L₂ lam mu nu : ℝ}
    (hnu : 0 ≤ nu)
    (hle : L₁ ≤ L₂) :
    VGS G C R D H K L₂ lam mu nu ≤ VGS G C R D H K L₁ lam mu nu := by
  unfold VGS; nlinarith;

/-! ## Part 4: Strict monotonicity in G when C, R, D > 0 -/

theorem VGS_strict_mono_G
    {G₁ G₂ C R D H K L lam mu nu : ℝ}
    (hC : 0 < C) (hR : 0 < R) (hD : 0 < D)
    (hlt : G₁ < G₂) :
    VGS G₁ C R D H K L lam mu nu < VGS G₂ C R D H K L lam mu nu := by
  unfold VGS; nlinarith [ mul_pos hC ( mul_pos hR hD ) ] ;

end