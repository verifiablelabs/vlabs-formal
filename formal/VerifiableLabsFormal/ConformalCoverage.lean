import Mathlib

/-!
# Split Conformal Reward Calibration

We formalize the finite-sample coverage guarantee of split conformal prediction
applied to reward calibration.

## Setup
- `n` calibration residuals `eᵢ = |R_trueᵢ - R_hatᵢ|` for `i = 1, …, n`
- Conformal quantile `q` = `⌈(n+1)(1-α)⌉`-th smallest calibration residual (1-indexed)
- Prediction interval: `[R_hat_new - q, R_hat_new + q]`

## Main Result
Under exchangeability of calibration and test residuals:
  `P(R_true_new ∈ [R_hat_new - q, R_hat_new + q]) ≥ 1 - α`

## Proof Structure
1. **Order statistic counting**: at least `k+1` values `≤` the `k`-th order statistic
2. **Leave-one-out monotonicity**: removing a value `≤ q` only increases the order stat
3. **Leave-one-out coverage**: at least `k+1` of `n+1` values satisfy the coverage condition
4. **Ceiling bound**: `⌈(n+1)(1-α)⌉₊/(n+1) ≥ 1-α`
5. **Main theorem**: combining coverage and ceiling bound

The exchangeability assumption is modeled combinatorially: each of the `n+1` indices is
equally likely to be the test point (uniform random test index). Coverage `≥ 1-α` is
equivalent to: at least `⌈(n+1)(1-α)⌉` of the `n+1` values satisfy the interval condition.
-/

noncomputable section

open Finset

attribute [local instance] Classical.propDecidable

/-! ## Definitions -/

/-- The conformal quantile level: `⌈(n+1)(1-α)⌉₊`. -/
def conformalLevel (n : ℕ) (α : ℝ) : ℕ := ⌈((n + 1 : ℝ) * (1 - α))⌉₊

/-- The set of values `q` in the range of `vals` such that at least `k+1` indices
    have their value `≤ q`. The `k`-th order statistic (0-indexed) is the minimum
    of this set. -/
def orderStatSet {m : ℕ} (vals : Fin m → ℝ) (k : ℕ) : Finset ℝ :=
  (Finset.univ.image vals).filter
    (fun q => k + 1 ≤ (Finset.univ.filter (fun i => vals i ≤ q)).card)

/-
The set `orderStatSet` is nonempty when `k < m`.
-/
lemma orderStatSet_nonempty {m : ℕ} (vals : Fin m → ℝ) (k : ℕ) (hk : k < m) :
    (orderStatSet vals k).Nonempty := by
  obtain ⟨q, hq⟩ : ∃ q ∈ univ.image vals, ∀ x ∈ univ.image vals, x ≤ q := by
    exact ⟨ Finset.max' ( Finset.image vals Finset.univ ) ⟨ _, Finset.mem_image_of_mem _ ( Finset.mem_univ ⟨ 0, by linarith ⟩ ) ⟩, Finset.max'_mem _ _, fun x hx => Finset.le_max' _ _ hx ⟩;
  use q;
  simp_all +decide [ orderStatSet ]

/-- The `k`-th order statistic (0-indexed): the smallest value `q` in the range
    of `vals` such that at least `k+1` values are `≤ q`. -/
def orderStat {m : ℕ} (vals : Fin m → ℝ) (k : ℕ) (hk : k < m) : ℝ :=
  (orderStatSet vals k).min' (orderStatSet_nonempty vals k hk)

/-! ## Core lemmas -/

/-- The order statistic belongs to the order stat set. -/
lemma orderStat_mem {m : ℕ} (vals : Fin m → ℝ) (k : ℕ) (hk : k < m) :
    orderStat vals k hk ∈ orderStatSet vals k :=
  Finset.min'_mem _ _

/-
The order statistic belongs to the range of `vals`.
-/
lemma orderStat_mem_range {m : ℕ} (vals : Fin m → ℝ) (k : ℕ) (hk : k < m) :
    ∃ i : Fin m, vals i = orderStat vals k hk := by
  exact Finset.mem_image.mp ( Finset.mem_filter.mp ( orderStat_mem vals k hk ) |>.1 ) |> Exists.imp fun i hi => hi.2

/-
**Counting lemma**: at least `k+1` values of `vals` are `≤` the `k`-th order
    statistic (0-indexed). This follows directly from the definition.
-/
theorem count_le_orderStat {m : ℕ} (vals : Fin m → ℝ) (k : ℕ) (hk : k < m) :
    k + 1 ≤ (Finset.univ.filter (fun i : Fin m => vals i ≤ orderStat vals k hk)).card := by
  exact Finset.mem_filter.mp ( orderStat_mem vals k hk ) |>.2

/-
If `q` is in the range and `q < orderStat`, then fewer than `k+1` values are `≤ q`.
-/
lemma count_lt_of_lt_orderStat {m : ℕ} (vals : Fin m → ℝ) (k : ℕ) (hk : k < m)
    (q : ℝ) (hq : q ∈ Finset.univ.image vals) (hlt : q < orderStat vals k hk) :
    (Finset.univ.filter (fun i : Fin m => vals i ≤ q)).card < k + 1 := by
  contrapose! hlt;
  exact Finset.min'_le _ q ( Finset.mem_filter.mpr ⟨ hq, hlt ⟩ )

/-
Removing an index only decreases the count of values `≤ q`.
-/
lemma count_remove_le {n : ℕ} (vals : Fin (n + 1) → ℝ) (i : Fin (n + 1)) (q : ℝ) :
    (Finset.univ.filter (fun j : Fin n => vals (i.succAbove j) ≤ q)).card ≤
    (Finset.univ.filter (fun j : Fin (n + 1) => vals j ≤ q)).card := by
  have h_inj : Finset.card (Finset.image (fun j => Fin.succAbove i j) (Finset.filter (fun j => vals (Fin.succAbove i j) ≤ q) Finset.univ)) ≤ Finset.card (Finset.filter (fun j => vals j ≤ q) Finset.univ) := by
    exact Finset.card_le_card fun x hx => by aesop;
  rwa [ Finset.card_image_of_injective _ fun x y hxy => by simpa [ Fin.succAbove_ne ] using hxy ] at h_inj

/-! ## Leave-one-out monotonicity -/

/-
**Leave-one-out monotonicity**: Removing a value `≤` the `k`-th order statistic
    can only increase (or preserve) the `k`-th order statistic.
-/
lemma orderStat_le_remove {n : ℕ} (vals : Fin (n + 1) → ℝ) (k : ℕ) (hk : k < n)
    (i : Fin (n + 1))
    (hi : vals i ≤ orderStat vals k (by omega)) :
    orderStat vals k (by omega) ≤ orderStat (vals ∘ i.succAbove) k hk := by
  contrapose! hi with h_contra
  generalize_proofs at *;
  -- By definition of orderStat, we know that orderStat (vals ∘ i.succAbove) k hk is in the range of (vals ∘ i.succAbove).
  obtain ⟨j, hj⟩ : ∃ j : Fin n, vals (i.succAbove j) = orderStat (vals ∘ i.succAbove) k hk := by
    convert orderStat_mem_range ( vals ∘ i.succAbove ) k hk using 1;
  -- By definition of orderStat, we know that orderStat (vals ∘ i.succAbove) k hk is in the range of (vals ∘ i.succAbove), so we can apply count_lt_of_lt_orderStat.
  have h_count_lt : (Finset.univ.filter (fun l : Fin (n + 1) => vals l ≤ orderStat (vals ∘ i.succAbove) k hk)).card < k + 1 := by
    apply_rules [ count_lt_of_lt_orderStat ];
    exact hj ▸ Finset.mem_image_of_mem _ ( Finset.mem_univ _ );
  exact absurd h_count_lt ( not_lt_of_ge ( le_trans ( count_le_orderStat _ _ _ ) ( count_remove_le _ _ _ ) ) )

/-! ## Leave-one-out coverage -/

/-
**Leave-one-out coverage lemma**: For any `n+1` values and any `k < n`,
    at least `k+1` of the `n+1` indices `i` satisfy
    `vals i ≤ orderStat(vals without i, k)`.

    Under exchangeability (uniform random test index), this gives coverage
    `≥ (k+1)/(n+1)`.
-/
theorem loo_coverage {n : ℕ} (vals : Fin (n + 1) → ℝ) (k : ℕ) (hk : k < n) :
    k + 1 ≤ (Finset.univ.filter (fun i : Fin (n + 1) =>
      vals i ≤ orderStat (vals ∘ i.succAbove) k hk)).card := by
  -- Let $q_all = orderStat vals k (by omega)$.
  set q_all := orderStat vals k (by omega) with hq_all;
  -- By count_le_orderStat, S := {i : Fin (n+1) | vals i ≤ q_all} has card ≥ k+1.
  have hS_card : (Finset.univ.filter (fun i : Fin (n + 1) => vals i ≤ q_all)).card ≥ k + 1 := by
    exact count_le_orderStat vals k ( by linarith );
  refine' le_trans hS_card ( Finset.card_mono _ );
  intro i hi; exact (by
  exact Finset.mem_filter.mpr ⟨ Finset.mem_univ _, le_trans ( Finset.mem_filter.mp hi |>.2 ) ( orderStat_le_remove vals k hk i ( Finset.mem_filter.mp hi |>.2 ) ) ⟩)

/-! ## Arithmetic: ceiling bound -/

/-
`⌈(n+1)(1-α)⌉₊ / (n+1) ≥ 1 - α` for `0 ≤ α ≤ 1`.
-/
theorem conformalLevel_coverage (n : ℕ) (α : ℝ) :
    1 - α ≤ (conformalLevel n α : ℝ) / (↑n + 1) := by
  rw [ le_div_iff₀ ] <;> norm_num [ conformalLevel ];
  · linarith [ Nat.le_ceil ( ( n + 1 : ℝ ) * ( 1 - α ) ) ];
  · positivity

/-
When `0 ≤ α < 1`, the conformal level is positive.
-/
lemma conformalLevel_pos (n : ℕ) (α : ℝ) (hα1 : α < 1) :
    0 < conformalLevel n α := by
  exact Nat.ceil_pos.mpr ( mul_pos ( by positivity ) ( sub_pos.mpr hα1 ) )

/-
The conformal level is `≤ n+1` when `α ≥ 0`.
-/
lemma conformalLevel_le (n : ℕ) (α : ℝ) (hα0 : 0 ≤ α) :
    conformalLevel n α ≤ n + 1 := by
  exact Nat.ceil_le.mpr ( by norm_num; nlinarith )

/-! ## Interval characterization -/

/-
The prediction interval `[R̂ - q, R̂ + q]` contains `R_true` iff `|R_true - R̂| ≤ q`.
-/
theorem in_interval_iff_abs_le (R_true R_hat q : ℝ) :
    (R_hat - q ≤ R_true ∧ R_true ≤ R_hat + q) ↔ |R_true - R_hat| ≤ q := by
  constructor <;> intro h <;> rw [ abs_le ] at * <;> constructor <;> linarith

/-! ## Main coverage theorems -/

/-
**Split conformal marginal coverage** (combinatorial version):

For any `n+1` values and `α ∈ [0, 1]` with `⌈(n+1)(1-α)⌉ ≤ n`,
at least `⌈(n+1)(1-α)⌉` of the `n+1` indices satisfy the conformal prediction
coverage condition. Under exchangeability (where each index is equally likely
to be the test point), this gives:

  `P(R_true_new ∈ [R̂_new - q, R̂_new + q]) ≥ 1 - α`
-/
theorem split_conformal_coverage {n : ℕ} (hn : 0 < n)
    (e : Fin (n + 1) → ℝ)
    (α : ℝ)
    (hα_nontrivial : conformalLevel n α ≤ n) :
    1 - α ≤
      ((Finset.univ.filter (fun i : Fin (n + 1) =>
        e i ≤ orderStat (e ∘ i.succAbove)
          (conformalLevel n α - 1) (by omega))).card : ℝ) / (↑n + 1) := by
  refine le_trans ( conformalLevel_coverage n α ) ?_;
  gcongr;
  have := loo_coverage e ( conformalLevel n α - 1 ) ( by omega );
  omega

/-
**Split conformal reward coverage**: specializing to reward residuals
    `eᵢ = |R_trueᵢ - R̂ᵢ|`, the conformal prediction interval
    `[R̂_new - q, R̂_new + q]` achieves marginal coverage `≥ 1 - α`.

    The filter counts indices `i` for which `R_true i` lies in the interval
    `[R̂ i - q_i, R̂ i + q_i]` where `q_i` is the leave-one-out conformal quantile.
-/
theorem split_conformal_reward_coverage {n : ℕ} (hn : 0 < n)
    (R_true R_hat : Fin (n + 1) → ℝ)
    (α : ℝ)
    (hα_nontrivial : conformalLevel n α ≤ n) :
    let e := fun i => |R_true i - R_hat i|
    let k := conformalLevel n α - 1
    1 - α ≤
      ((Finset.univ.filter (fun i : Fin (n + 1) =>
        let q_i := orderStat (e ∘ i.succAbove) k (by omega)
        R_hat i - q_i ≤ R_true i ∧ R_true i ≤ R_hat i + q_i)).card : ℝ) / (↑n + 1) := by
  convert split_conformal_coverage hn ( fun i => |R_true i - R_hat i| ) α hα_nontrivial using 3;
  congr! 2;
  grind

end