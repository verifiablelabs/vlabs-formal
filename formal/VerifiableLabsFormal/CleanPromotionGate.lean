import Mathlib

/-!
# CleanPromotionGate

Module **F** of the contamination-resistant evaluation track.

A *clean promotion gate* accepts a candidate checkpoint update only when its
contamination-adjusted metrics improve / stay within tolerance across eight
conditions.  We prove the per-condition extraction lemmas and that a sequence of
accepted updates is monotone nondecreasing in `clean_vgs`, growing by at least
`tau` per accepted step.
-/

namespace Verifiable.CleanPromotionGate

/-- Contamination-adjusted metrics of a checkpoint. -/
structure CleanMetrics where
  clean_vgs : ℝ
  hack_risk : ℝ
  calibration : ℝ
  ood : ℝ
  dcr : ℝ
  cost : ℝ
  latency : ℝ
  regression : Bool

/-- Nonnegative tolerances for the gate. -/
structure CleanTolerances where
  tau : ℝ
  eps_h : ℝ
  eps_c : ℝ
  eps_o : ℝ
  eps_d : ℝ
  eps_k : ℝ
  eps_l : ℝ
  tau_nonneg : 0 ≤ tau
  eps_h_nonneg : 0 ≤ eps_h
  eps_c_nonneg : 0 ≤ eps_c
  eps_o_nonneg : 0 ≤ eps_o
  eps_d_nonneg : 0 ≤ eps_d
  eps_k_nonneg : 0 ≤ eps_k
  eps_l_nonneg : 0 ≤ eps_l

/-- The eight-condition clean acceptance predicate. -/
def CleanAcceptUpdate (old new : CleanMetrics) (tol : CleanTolerances) : Prop :=
  new.clean_vgs ≥ old.clean_vgs + tol.tau ∧
  new.hack_risk ≤ old.hack_risk + tol.eps_h ∧
  new.calibration ≥ old.calibration - tol.eps_c ∧
  new.ood ≥ old.ood - tol.eps_o ∧
  new.dcr ≤ old.dcr + tol.eps_d ∧
  new.cost ≤ old.cost + tol.eps_k ∧
  new.latency ≤ old.latency + tol.eps_l ∧
  new.regression = false

/-- **F.1** An accepted update improves clean VGS by at least `tau`. -/
theorem accepted_update_improves_clean_vgs {old new : CleanMetrics}
    {tol : CleanTolerances} (h : CleanAcceptUpdate old new tol) :
    new.clean_vgs ≥ old.clean_vgs + tol.tau := h.1

/-- **F.2** An accepted update bounds the hack-risk increase. -/
theorem accepted_update_bounds_hack_risk {old new : CleanMetrics}
    {tol : CleanTolerances} (h : CleanAcceptUpdate old new tol) :
    new.hack_risk ≤ old.hack_risk + tol.eps_h := h.2.1

/-- **F.3** An accepted update bounds the contamination-risk increase. -/
theorem accepted_update_bounds_dcr {old new : CleanMetrics}
    {tol : CleanTolerances} (h : CleanAcceptUpdate old new tol) :
    new.dcr ≤ old.dcr + tol.eps_d := h.2.2.2.2.1

/-- **F.4** An accepted update sets no regression flag. -/
theorem accepted_update_no_regression {old new : CleanMetrics}
    {tol : CleanTolerances} (h : CleanAcceptUpdate old new tol) :
    new.regression = false := h.2.2.2.2.2.2.2

/-- **F.5** A sequence of accepted updates is monotone nondecreasing in clean
VGS. -/
theorem accepted_sequence_clean_vgs_monotone
    (seq : ℕ → CleanMetrics) (tol : CleanTolerances)
    (h : ∀ i, CleanAcceptUpdate (seq i) (seq (i + 1)) tol) :
    Monotone (fun n => (seq n).clean_vgs) := by
  apply monotone_nat_of_le_succ
  intro n
  have hstep := (h n).1
  have htau := tol.tau_nonneg
  show (seq n).clean_vgs ≤ (seq (n + 1)).clean_vgs
  linarith

/-- **F.6** After `n` accepted updates, clean VGS has grown by at least
`n * tau`. -/
theorem accepted_sequence_clean_vgs_growth
    (seq : ℕ → CleanMetrics) (tol : CleanTolerances)
    (h : ∀ i, CleanAcceptUpdate (seq i) (seq (i + 1)) tol) (n : ℕ) :
    (seq n).clean_vgs ≥ (seq 0).clean_vgs + n * tol.tau := by
  induction n with
  | zero => simp
  | succ k ih =>
    have hstep := (h k).1
    push_cast at ih ⊢
    nlinarith [ih, hstep]

end Verifiable.CleanPromotionGate
