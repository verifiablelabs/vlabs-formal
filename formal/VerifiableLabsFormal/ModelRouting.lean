import Mathlib

/-!
# Model Routing Utility

We formalize a model routing utility function:

  U_m(x) = Q_m(x) - γ · Cost_m(x) - δ · Latency_m(x) - ρ · Risk_m(x)

where all terms are bounded real numbers, and prove three properties:

1. The selected model (argmax) has utility at least as high as any other available model.
2. If a cheaper model has equal quality, latency and risk, it is preferred when γ > 0.
3. If utility estimates have error at most ε, then the selected model is within 2ε of
   optimal true utility.
-/

noncomputable section

open scoped Real

/-- Model routing utility: U_m = Q_m - γ · Cost_m - δ · Latency_m - ρ · Risk_m -/
def routingUtility (Q Cost Latency Risk γ δ ρ : ℝ) : ℝ :=
  Q - γ * Cost - δ * Latency - ρ * Risk

/-- Given a nonempty finite set of models, the selected model is one that maximises utility. -/
def selectedModel {M : Type*} [DecidableEq M] (models : Finset M) (hne : models.Nonempty)
    (U : M → ℝ) : M :=
  (models.exists_max_image U hne).choose

lemma selectedModel_mem {M : Type*} [DecidableEq M] (models : Finset M) (hne : models.Nonempty)
    (U : M → ℝ) : selectedModel models hne U ∈ models :=
  (models.exists_max_image U hne).choose_spec.1

lemma selectedModel_max {M : Type*} [DecidableEq M] (models : Finset M) (hne : models.Nonempty)
    (U : M → ℝ) : ∀ m ∈ models, U m ≤ U (selectedModel models hne U) :=
  (models.exists_max_image U hne).choose_spec.2

/-! ## Property 1: Selected model has maximal utility -/

/-
The selected model has utility at least as high as any other available model.
-/
theorem selected_model_optimal {M : Type*} [DecidableEq M]
    (models : Finset M) (hne : models.Nonempty) (U : M → ℝ)
    (m : M) (hm : m ∈ models) :
    U m ≤ U (selectedModel models hne U) := by
  -- By definition of `selectedModel`, we know that `U (selectedModel models hne U)` is the maximum value of `U` over `models`.
  apply selectedModel_max models hne U m hm

/-! ## Property 2: Cheaper model preferred when γ > 0 -/

/-
If two models have equal quality, latency, and risk, but model a is cheaper than model b,
    then model a has strictly higher utility when γ > 0.
-/
theorem cheaper_model_preferred
    (Q_a Q_b Cost_a Cost_b Lat_a Lat_b Risk_a Risk_b γ δ ρ : ℝ)
    (hQ : Q_a = Q_b) (hLat : Lat_a = Lat_b) (hRisk : Risk_a = Risk_b)
    (hCost : Cost_a < Cost_b) (hγ : γ > 0) :
    routingUtility Q_b Cost_b Lat_b Risk_b γ δ ρ <
    routingUtility Q_a Cost_a Lat_a Risk_a γ δ ρ := by
  unfold routingUtility;
  simp [ * ]

/-! ## Property 3: Near-optimality under estimation error -/

/-
If the estimated utility Û_m differs from the true utility U_m by at most ε for every model,
    then the model selected by the estimated utility achieves true utility within 2ε of the
    true optimal.
-/
theorem near_optimal_under_error {M : Type*} [DecidableEq M]
    (models : Finset M) (hne : models.Nonempty)
    (U_true U_est : M → ℝ) (ε : ℝ)
    (herr : ∀ m ∈ models, |U_est m - U_true m| ≤ ε)
    (m_star : M) (hm_star : m_star ∈ models) :
    U_true m_star - U_true (selectedModel models hne U_est) ≤ 2 * ε := by
  linarith [ abs_le.mp ( herr m_star hm_star ), abs_le.mp ( herr ( selectedModel models hne U_est ) ( selectedModel_mem models hne U_est ) ), selectedModel_max models hne U_est m_star hm_star ]

end