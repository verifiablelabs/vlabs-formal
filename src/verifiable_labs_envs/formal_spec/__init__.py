"""Python mirror of the machine-verified Lean 4 specification in ``formal/``.

This package implements, in pure Python, the formulas, the 7-condition
self-improvement gate, and the invariance-violation harness whose
mathematical properties are proved in
``formal/VerifiableLabsFormal/``.

The Python implementation is *property-tested* against the Lean
specification (see ``tests/formal_spec/``); it is **not** itself
formally verified. When documenting downstream behaviour, do not
describe this code, the SDK, or the hosted API as "formally verified".
The only verified artefact is the Lean source. The approved wording is
in the project ``README.md`` under "Formally verified guarantees".

Lean cross-reference:

* ``formulas``  ↔ ``CalibratedReward.lean`` + ``VGS.lean`` +
  ``AdaptiveDifficulty.lean`` + ``ModelRouting.lean``
* ``gate``      ↔ ``SelfImprovementGate.lean``
* ``invariance``↔ ``VerifierInvariance.lean``

Contamination-resistant clean-gate track (modules A–G):

* ``contamination_risk``  ↔ ``ContaminationRisk.lean``
* ``clean_vgs``           ↔ ``CleanVGS.lean``
* ``generalization_gap``  ↔ ``GeneralizationGap.lean``
* ``contamination_splits``↔ ``ContaminationSplits.lean``
* ``generated_after_freeze``↔ ``GeneratedAfterFreeze.lean``
* ``clean_promotion_gate``↔ ``CleanPromotionGate.lean``
* ``clean_pipeline``      ↔ ``CleanPipeline.lean``
"""

from .clean_pipeline import (
    CleanPipelineGuarantees,
    clean_pipeline_acceptance,
)
from .clean_promotion_gate import (
    REASON_CALIBRATION_REGRESSED,
    REASON_CLEAN_VGS_NOT_IMPROVED,
    REASON_COST_INCREASED,
    REASON_DCR_INCREASED,
    REASON_HACK_RISK_INCREASED,
    REASON_LATENCY_INCREASED,
    REASON_OOD_REGRESSED,
    REASON_REGRESSION_FLAGGED,
    CleanGateDecision,
    CleanMetrics,
    CleanTolerances,
    accept_clean_update,
)
from .clean_vgs import clean_vgs
from .contamination_risk import clean_score
from .contamination_splits import (
    Split,
    SplitPolicyError,
    is_trainable,
    validate_split_policy,
)
from .formulas import (
    calibrated_reward,
    difficulty_update,
    routing_utility,
    select_model,
    vgs,
)
from .gate import (
    GateDecision,
    ModelMetrics,
    Tolerances,
    accept_update,
)
from .generalization_gap import (
    gap,
    large_gap,
)
from .generated_after_freeze import (
    EvalScenario,
    Model,
    generated_after_freeze_not_in_training,
)
from .invariance import (
    InvarianceReport,
    check_invariance,
)

__all__ = [
    "calibrated_reward",
    "vgs",
    "difficulty_update",
    "routing_utility",
    "select_model",
    "ModelMetrics",
    "Tolerances",
    "GateDecision",
    "accept_update",
    "InvarianceReport",
    "check_invariance",
    # Contamination-resistant clean-gate track (modules A–G)
    "clean_score",
    "clean_vgs",
    "gap",
    "large_gap",
    "Split",
    "SplitPolicyError",
    "is_trainable",
    "validate_split_policy",
    "Model",
    "EvalScenario",
    "generated_after_freeze_not_in_training",
    "CleanMetrics",
    "CleanTolerances",
    "CleanGateDecision",
    "accept_clean_update",
    "REASON_CLEAN_VGS_NOT_IMPROVED",
    "REASON_HACK_RISK_INCREASED",
    "REASON_CALIBRATION_REGRESSED",
    "REASON_OOD_REGRESSED",
    "REASON_DCR_INCREASED",
    "REASON_COST_INCREASED",
    "REASON_LATENCY_INCREASED",
    "REASON_REGRESSION_FLAGGED",
    "CleanPipelineGuarantees",
    "clean_pipeline_acceptance",
]
