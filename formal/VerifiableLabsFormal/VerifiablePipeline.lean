import VerifiableLabsFormal.CalibratedReward
import VerifiableLabsFormal.VGS
import VerifiableLabsFormal.AdaptiveDifficulty
import VerifiableLabsFormal.VerifierInvariance
import VerifiableLabsFormal.ConformalCoverage
import VerifiableLabsFormal.ModelRouting

/-!
# Verifiable Pipeline Composition Theorem

We compose six independently proved modules into a unified pipeline for Verifiable Labs:

1. **Calibrated Reward** (`calibratedReward`): R*(V, C, H, λ) = V·C − λ·H
2. **Verifiable Generalization Score** (`VGS`): G·C·R·D − λ·H − μ·K − ν·L
3. **Adaptive Difficulty** (`difficultyUpdate`): d_{t+1} = d_t + η(s_t − s*)
4. **Verifier Invariance** (`VerifierInvariant`): V(x,a) = V(T_X x, T_A a)
5. **Split Conformal Coverage**: P(R_true ∈ [R̂ − q, R̂ + q]) ≥ 1 − α
6. **Model Routing** (`routingUtility` / `selectedModel`): U_m = Q − γ·Cost − δ·Lat − ρ·Risk

## Pipeline Output

We define `VerifiablePipelineOutput` bundling the pipeline's key outputs, and prove
nine composition properties showing that end-to-end guarantees follow from the
module-level guarantees.
-/

noncomputable section

/-! ## Pipeline output structure -/

/-- A structured output from the verifiable pipeline. -/
structure VerifiablePipelineOutput (M : Type*) where
  /-- The calibrated reward R*(V,C,H,λ) = V·C − λ·H. -/
  reward : ℝ
  /-- Lower bound of the conformal prediction interval for the reward. -/
  confidence_lower : ℝ
  /-- Upper bound of the conformal prediction interval for the reward. -/
  confidence_upper : ℝ
  /-- Next difficulty level from the adaptive update. -/
  difficulty_next : ℝ
  /-- Hackability risk H ∈ [0,1]. -/
  hackability_risk : ℝ
  /-- The model selected by the routing utility. -/
  selected_model : M
  /-- The Verifiable Generalization Score. -/
  generalization_score : ℝ

/-- Construct a `VerifiablePipelineOutput` from the module-level computations. -/
def mkPipelineOutput {M : Type*} [DecidableEq M]
    (V C H lam : ℝ)
    (R_hat q : ℝ)
    (η s_star s_t d_t : ℝ)
    (G Cv R D K L mu nu : ℝ)
    (models : Finset M) (hne : models.Nonempty) (U : M → ℝ) :
    VerifiablePipelineOutput M :=
  { reward := calibratedReward V C H lam
    confidence_lower := R_hat - q
    confidence_upper := R_hat + q
    difficulty_next := difficultyUpdate η s_star s_t d_t
    hackability_risk := H
    selected_model := selectedModel models hne U
    generalization_score := VGS G Cv R D H K L lam mu nu }

/-! ## Property 1: Pipeline reward is bounded in [-λ, 1] -/

/-- The pipeline reward (calibrated reward) lies in [-λ, 1]. -/
theorem pipeline_reward_bounded
    {V C H lam : ℝ}
    (hV0 : 0 ≤ V) (hV1 : V ≤ 1)
    (hC0 : 0 ≤ C) (hC1 : C ≤ 1)
    (hH0 : 0 ≤ H) (hH1 : H ≤ 1)
    (hlam : 0 ≤ lam) :
    calibratedReward V C H lam ∈ Set.Icc (-lam) 1 :=
  calibratedReward_bounded hV0 hV1 hC0 hC1 hH0 hH1 hlam

/-! ## Property 2: Increasing V cannot decrease pipeline reward -/

/-- Increasing verifier correctness V cannot decrease the pipeline reward. -/
theorem pipeline_reward_mono_V
    {V₁ V₂ C H lam : ℝ}
    (hC0 : 0 ≤ C)
    (hVle : V₁ ≤ V₂) :
    calibratedReward V₁ C H lam ≤ calibratedReward V₂ C H lam :=
  calibratedReward_mono_V hC0 hVle

/-! ## Property 3: Increasing C cannot decrease pipeline reward -/

/-- Increasing calibration confidence C cannot decrease the pipeline reward. -/
theorem pipeline_reward_mono_C
    {V C₁ C₂ H lam : ℝ}
    (hV0 : 0 ≤ V)
    (hCle : C₁ ≤ C₂) :
    calibratedReward V C₁ H lam ≤ calibratedReward V C₂ H lam :=
  calibratedReward_mono_C hV0 hCle

/-! ## Property 4: Increasing H cannot increase pipeline reward -/

/-- Increasing hackability risk H cannot increase the pipeline reward. -/
theorem pipeline_reward_anti_H
    {V C H₁ H₂ lam : ℝ}
    (hlam : 0 ≤ lam)
    (hHle : H₁ ≤ H₂) :
    calibratedReward V C H₂ lam ≤ calibratedReward V C H₁ lam :=
  calibratedReward_anti_H hlam hHle

/-! ## Property 5: Verifier invariance preserves correctness -/

/-- If verifier invariance holds, transformed correct answers remain correct. -/
theorem pipeline_verifier_invariance_preserves
    {X A : Type*}
    (V : X → A → Bool) (T_X : X → X) (T_A : A → A)
    (hinv : VerifierInvariant V T_X T_A)
    (x : X) (a : A) (hcorrect : V x a = true) :
    V (T_X x) (T_A a) = true :=
  invariant_preserves_correct V T_X T_A hinv x a hcorrect

/-! ## Property 6: Conformal reward interval coverage ≥ 1-α -/

/-- Under conformal assumptions, the reward interval has coverage at least 1-α. -/
theorem pipeline_conformal_coverage {n : ℕ} (hn : 0 < n)
    (R_true R_hat : Fin (n + 1) → ℝ)
    (α : ℝ)
    (hα_nontrivial : conformalLevel n α ≤ n) :
    let e := fun i => |R_true i - R_hat i|
    let k := conformalLevel n α - 1
    1 - α ≤
      ((Finset.univ.filter (fun i : Fin (n + 1) =>
        let q_i := orderStat (e ∘ i.succAbove) k (by omega)
        R_hat i - q_i ≤ R_true i ∧ R_true i ≤ R_hat i + q_i)).card : ℝ) / (↑n + 1) :=
  split_conformal_reward_coverage hn R_true R_hat α hα_nontrivial

/-! ## Property 7: Adaptive difficulty local stability under ηL < 1 -/

/-- Under ηL < 1 with s antitone and L-Lipschitz, the adaptive difficulty step is
    non-expansive around the fixed point (locally stable). -/
theorem pipeline_difficulty_stable
    (s : ℝ → ℝ)
    (hs_anti : Antitone s)
    (L : ℝ)
    (hs_lip : ∀ x y : ℝ, |s x - s y| ≤ L * |x - y|)
    (η : ℝ) (hη : η > 0) (hηL : η * L < 1)
    (s_star d_star : ℝ) (hfp : s d_star = s_star)
    (d : ℝ) :
    |difficultyUpdate η s_star (s d) d - d_star| ≤ |d - d_star| :=
  stability_nonexpansive s hs_anti L hs_lip η hη hηL s_star d_star hfp d

/-! ## Property 8: Model routing 2ε-near-optimality -/

/-- Under bounded utility estimation error ε, the selected model is 2ε-near-optimal. -/
theorem pipeline_routing_near_optimal {M : Type*} [DecidableEq M]
    (models : Finset M) (hne : models.Nonempty)
    (U_true U_est : M → ℝ) (ε : ℝ)
    (herr : ∀ m ∈ models, |U_est m - U_true m| ≤ ε)
    (m_star : M) (hm_star : m_star ∈ models) :
    U_true m_star - U_true (selectedModel models hne U_est) ≤ 2 * ε :=
  near_optimal_under_error models hne U_true U_est ε herr m_star hm_star

/-! ## Property 9: VGS strictly increases with held-out generalization -/

/-- If calibration C, robustness R, and difficulty fit D are positive,
    increasing held-out generalization G strictly increases the pipeline
    generalization score (VGS). -/
theorem pipeline_generalization_strict_mono
    {G₁ G₂ C R D H K L lam mu nu : ℝ}
    (hC : 0 < C) (hR : 0 < R) (hD : 0 < D)
    (hlt : G₁ < G₂) :
    VGS G₁ C R D H K L lam mu nu < VGS G₂ C R D H K L lam mu nu :=
  VGS_strict_mono_G hC hR hD hlt

end
