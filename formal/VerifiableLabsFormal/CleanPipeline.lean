import Mathlib
import VerifiableLabsFormal.ContaminationSplits
import VerifiableLabsFormal.GeneratedAfterFreeze
import VerifiableLabsFormal.ContaminationRisk
import VerifiableLabsFormal.CleanVGS
import VerifiableLabsFormal.GeneralizationGap
import VerifiableLabsFormal.CleanPromotionGate

/-!
# CleanPipeline

Module **G** of the contamination-resistant evaluation track.

This module composes the clean promotion gate (module F) into a single
soundness theorem: acceptance by the clean gate entails *all* of the
contamination-adjusted guarantees simultaneously.  In particular, acceptance is
not implied by public benchmark improvement alone — it requires clean,
contamination-adjusted generalization under bounded risk.
-/

namespace Verifiable.CleanPipeline

open Verifiable.CleanPromotionGate

/-- **G** Soundness of clean-pipeline acceptance.

If a candidate update is accepted by the clean promotion gate, then:
* `clean_vgs` improved by at least `tau`;
* the hack-risk increase is bounded by `eps_h`;
* the contamination-risk (`dcr`) increase is bounded by `eps_d`;
* `ood` did not regress beyond `eps_o`;
* `calibration` did not regress beyond `eps_c`;
* `cost` is bounded by `eps_k` and `latency` by `eps_l`;
* no regression flag is set. -/
theorem clean_pipeline_acceptance_sound {old new : CleanMetrics}
    {tol : CleanTolerances} (h : CleanAcceptUpdate old new tol) :
    new.clean_vgs ≥ old.clean_vgs + tol.tau ∧
    new.hack_risk ≤ old.hack_risk + tol.eps_h ∧
    new.dcr ≤ old.dcr + tol.eps_d ∧
    new.ood ≥ old.ood - tol.eps_o ∧
    new.calibration ≥ old.calibration - tol.eps_c ∧
    new.cost ≤ old.cost + tol.eps_k ∧
    new.latency ≤ old.latency + tol.eps_l ∧
    new.regression = false := by
  obtain ⟨h1, h2, h3, h4, h5, h6, h7, h8⟩ := h
  exact ⟨h1, h2, h5, h4, h3, h6, h7, h8⟩

end Verifiable.CleanPipeline
