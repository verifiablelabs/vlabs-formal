"""Clean-pipeline composition — mirrors ``CleanPipeline.lean``.

Module **G** of the contamination-resistant evaluation track. The Lean theorem
``clean_pipeline_acceptance_sound`` proves that acceptance by the clean
promotion gate entails *all* of the contamination-adjusted guarantees
simultaneously — in particular, acceptance is **not** implied by public
benchmark improvement alone; it requires clean, contamination-adjusted
generalization under bounded risk.

This module is a thin compose helper over ``clean_promotion_gate``: it runs the
gate and, on acceptance, returns the bundle of guarantees the Lean soundness
theorem certifies hold together. Cross-reference (namespace
``Verifiable.CleanPipeline``): ``clean_pipeline_acceptance_sound``.
"""

from __future__ import annotations

from dataclasses import dataclass

from .clean_promotion_gate import (
    CleanGateDecision,
    CleanMetrics,
    CleanTolerances,
    accept_clean_update,
)


@dataclass(frozen=True)
class CleanPipelineGuarantees:
    """The conjunction of guarantees entailed by a clean-gate acceptance.

    Mirrors the eight-way conjunction proved in
    ``Verifiable.CleanPipeline.clean_pipeline_acceptance_sound``. Every field is
    ``True`` exactly when the gate accepted (they are the per-condition facts).
    """

    clean_vgs_improved: bool
    hack_risk_bounded: bool
    dcr_bounded: bool
    ood_not_regressed: bool
    calibration_not_regressed: bool
    cost_bounded: bool
    latency_bounded: bool
    no_regression: bool

    def all_hold(self) -> bool:
        """Whether every composed guarantee holds (i.e. the gate accepted)."""
        return all(
            (
                self.clean_vgs_improved,
                self.hack_risk_bounded,
                self.dcr_bounded,
                self.ood_not_regressed,
                self.calibration_not_regressed,
                self.cost_bounded,
                self.latency_bounded,
                self.no_regression,
            )
        )


def clean_pipeline_acceptance(
    tol: CleanTolerances,
    old: CleanMetrics,
    new: CleanMetrics,
) -> tuple[CleanGateDecision, CleanPipelineGuarantees]:
    """Run the clean gate and expose the composed soundness bundle.

    Mirrors ``Verifiable.CleanPipeline.clean_pipeline_acceptance_sound``: when
    the gate accepts, every contamination-adjusted guarantee holds
    simultaneously. The returned ``CleanPipelineGuarantees.all_hold()`` is
    ``True`` iff ``decision.accepted`` is ``True``.

    Args:
        tol: tolerance budget.
        old: previous-checkpoint metrics.
        new: candidate-checkpoint metrics.

    Returns:
        A pair ``(decision, guarantees)``. ``guarantees`` records each
        per-condition fact; on acceptance every fact is ``True``.
    """
    decision = accept_clean_update(tol, old, new)
    guarantees = CleanPipelineGuarantees(
        clean_vgs_improved=new.clean_vgs >= old.clean_vgs + tol.tau,
        hack_risk_bounded=new.hack_risk <= old.hack_risk + tol.eps_h,
        dcr_bounded=new.dcr <= old.dcr + tol.eps_d,
        ood_not_regressed=new.ood_score >= old.ood_score - tol.eps_o,
        calibration_not_regressed=new.calibration >= old.calibration - tol.eps_c,
        cost_bounded=new.cost <= old.cost + tol.eps_k,
        latency_bounded=new.latency <= old.latency + tol.eps_l,
        no_regression=not new.regression,
    )
    return decision, guarantees


__all__ = [
    "CleanPipelineGuarantees",
    "clean_pipeline_acceptance",
]
