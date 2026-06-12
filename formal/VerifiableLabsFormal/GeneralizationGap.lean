import Mathlib

/-!
# GeneralizationGap

Module **E** of the contamination-resistant evaluation track.

The public-hidden generalization gap is `gap pub hidden = pub - hidden`
(here `pub` denotes the public score; `public` is a reserved Lean keyword).
A *large gap* relative to a threshold `tau` is `gap pub hidden > tau`.

We prove that a positive (resp. large) gap implies the hidden score
underperforms the public score, characterize a zero gap, bound the gap on
`[0,1]` inputs, and show a reject-on-large-gap rule is sound.
-/

namespace Verifiable.GeneralizationGap

/-- The public-hidden generalization gap (`pub` = public score). -/
def gap (pub hidden : ℝ) : ℝ := pub - hidden

/-- A large gap relative to threshold `tau`. -/
def large_gap (pub hidden tau : ℝ) : Prop := gap pub hidden > tau

/-- **E.1** A positive gap means the hidden score underperforms the public
score. -/
theorem positive_gap_implies_hidden_underperforms {pub hidden : ℝ}
    (h : gap pub hidden > 0) : hidden < pub := by
  unfold gap at h; linarith

/-- **E.2** A large gap (with nonnegative threshold) means the hidden score
underperforms the public score. -/
theorem large_gap_implies_hidden_underperforms {pub hidden tau : ℝ}
    (htau : 0 ≤ tau) (h : gap pub hidden > tau) : hidden < pub := by
  unfold gap at h; linarith

/-- **E.3** The gap is zero exactly when the two scores are equal. -/
theorem zero_gap_iff_equal {pub hidden : ℝ} :
    gap pub hidden = 0 ↔ pub = hidden := by
  unfold gap
  constructor <;> intro h <;> linarith

/-- **E.4** On `[0,1]` inputs the gap lies in `[-1,1]`. -/
theorem gap_bounded {pub hidden : ℝ}
    (hp0 : 0 ≤ pub) (hp1 : pub ≤ 1) (hh0 : 0 ≤ hidden) (hh1 : hidden ≤ 1) :
    -1 ≤ gap pub hidden ∧ gap pub hidden ≤ 1 := by
  unfold gap
  constructor <;> linarith

/-- **E.5** Rejecting an update precisely when the gap is large (with
nonnegative threshold) is sound: a rejected update genuinely has the hidden
score underperforming the public score. -/
theorem reject_on_large_gap_sound {pub hidden tau : ℝ}
    (htau : 0 ≤ tau) (hreject : large_gap pub hidden tau) : hidden < pub :=
  large_gap_implies_hidden_underperforms htau hreject

end Verifiable.GeneralizationGap
