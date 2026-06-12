"""Clean promotion gate — mirrors ``CleanPromotionGate.lean``.

Module **F** of the contamination-resistant evaluation track. The
``accept_clean_update`` function evaluates the eight-condition
``CleanAcceptUpdate`` predicate proved sound in Lean. Any sequence of model
updates accepted by this predicate is monotone non-decreasing in
``clean_vgs`` (Lean ``accepted_sequence_clean_vgs_monotone``) and after ``n``
acceptances satisfies ``clean_vgs_n ≥ clean_vgs_0 + n·τ`` (Lean
``accepted_sequence_clean_vgs_growth``).

This is a *specification mirror* — the production checkpoint promotion pipeline
lives elsewhere. The CLI wrapper ``vlabs-prm-eval clean-gate`` consumes eval
cards and reuses this predicate.

Cross-reference (namespace ``Verifiable.CleanPromotionGate``):

* ``accepted_update_improves_clean_vgs`` — accept ⇒ clean_vgs gain ≥ τ.
* ``accepted_update_bounds_hack_risk`` — accept ⇒ hack-risk increase bounded.
* ``accepted_update_bounds_dcr`` — accept ⇒ dcr increase bounded.
* ``accepted_update_no_regression`` — accept ⇒ no regression flag.
* ``accepted_sequence_clean_vgs_monotone`` / ``accepted_sequence_clean_vgs_growth``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------
# Domain validation helpers (local — mirrors gate.py for self-containment).
# ---------------------------------------------------------------------
def _check_finite(name: str, x: float) -> None:
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite, got {x!r}")


def _check_nonneg_finite(name: str, x: float) -> None:
    _check_finite(name, x)
    if x < 0.0:
        raise ValueError(f"{name} must be ≥ 0, got {x!r}")


# ---------------------------------------------------------------------
# CleanMetrics — Python view; superset of the Lean ``structure CleanMetrics``.
# The gate reads the eight fields the Lean predicate uses (clean_vgs,
# hack_risk, calibration, ood_score, dcr, cost, latency, regression); the
# extra provenance fields (raw_vgs, public_score, hidden_score) are carried for
# the eval-card bridge and rendering.
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class CleanMetrics:
    """Contamination-adjusted metrics of one checkpoint.

    Mirrors the Lean ``structure CleanMetrics`` for the eight gate fields and
    carries three extra provenance fields used by the CLI bridge:

    * ``raw_vgs``      — uncorrected VGS in ``[0, 1]`` (provenance).
    * ``dcr``          — data-contamination-risk score in ``[0, 1]``.
    * ``clean_vgs``    — contamination-adjusted VGS (any finite real).
    * ``public_score`` — public-benchmark score (provenance).
    * ``hidden_score`` — hidden-eval score (provenance).
    * ``ood_score``    — out-of-distribution performance.
    * ``hack_risk``    — hackability estimate H.
    * ``calibration``  — calibration metric.
    * ``cost``         — cost per audit ($, ≥ 0).
    * ``latency``      — wall-clock latency (seconds, ≥ 0).
    * ``regression``   — True iff a hard regression flag fired upstream.

    All floats must be finite; ``cost``/``latency`` must additionally be ``≥ 0``.
    """

    raw_vgs: float
    dcr: float
    clean_vgs: float
    public_score: float
    hidden_score: float
    ood_score: float
    hack_risk: float
    calibration: float
    cost: float
    latency: float
    regression: bool

    def __post_init__(self) -> None:
        for name, x in (
            ("raw_vgs", self.raw_vgs),
            ("dcr", self.dcr),
            ("clean_vgs", self.clean_vgs),
            ("public_score", self.public_score),
            ("hidden_score", self.hidden_score),
            ("ood_score", self.ood_score),
            ("hack_risk", self.hack_risk),
            ("calibration", self.calibration),
        ):
            _check_finite(name, x)
        _check_nonneg_finite("cost", self.cost)
        _check_nonneg_finite("latency", self.latency)
        if not isinstance(self.regression, bool):
            raise ValueError(
                f"regression must be a bool, got {type(self.regression).__name__}"
            )


# ---------------------------------------------------------------------
# CleanTolerances — mirrors the Lean ``structure CleanTolerances`` with its
# seven nonnegativity hypotheses.
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class CleanTolerances:
    """Per-condition slack budgets for the clean gate.

    Mirrors the Lean ``structure CleanTolerances`` including the seven
    ``*_nonneg`` proofs of non-negativity, validated eagerly here. ``eps_d`` is
    the additional contamination-risk (``dcr``) budget absent from the plain
    gate.
    """

    tau: float = 0.01
    eps_h: float = 0.02
    eps_c: float = 0.02
    eps_o: float = 0.02
    eps_d: float = 0.02
    eps_k: float = 5.0      # $ per audit
    eps_l: float = 0.5      # seconds

    def __post_init__(self) -> None:
        for name, x in (
            ("tau", self.tau),
            ("eps_h", self.eps_h),
            ("eps_c", self.eps_c),
            ("eps_o", self.eps_o),
            ("eps_d", self.eps_d),
            ("eps_k", self.eps_k),
            ("eps_l", self.eps_l),
        ):
            _check_nonneg_finite(name, x)


# ---------------------------------------------------------------------
# CleanGateDecision + accept_clean_update
# ---------------------------------------------------------------------
# Canonical names for each of the eight CleanAcceptUpdate conditions, in Lean
# field order. Tests assert each reason can fire independently; the CLI wraps
# these into a human-readable table.
REASON_CLEAN_VGS_NOT_IMPROVED = "clean_vgs_not_improved"
REASON_HACK_RISK_INCREASED = "hack_risk_increased"
REASON_CALIBRATION_REGRESSED = "calibration_regressed"
REASON_OOD_REGRESSED = "ood_regressed"
REASON_DCR_INCREASED = "dcr_increased"
REASON_COST_INCREASED = "cost_increased"
REASON_LATENCY_INCREASED = "latency_increased"
REASON_REGRESSION_FLAGGED = "regression_flagged"


@dataclass(frozen=True)
class CleanGateDecision:
    """Result of a single clean-gate evaluation.

    ``accepted`` is True iff every one of the eight Lean ``CleanAcceptUpdate``
    conditions held. ``reasons`` lists the named reasons for each failing
    condition, in Lean order; on an accept it is empty. ``metrics_delta`` maps
    each gated metric to its ``new − old`` change for rendering/auditing.
    """

    accepted: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)
    metrics_delta: dict[str, Any] = field(default_factory=dict)
    old: CleanMetrics | None = None
    new: CleanMetrics | None = None


def accept_clean_update(
    tol: CleanTolerances,
    old: CleanMetrics,
    new: CleanMetrics,
) -> CleanGateDecision:
    """Evaluate the eight-condition ``CleanAcceptUpdate`` predicate.

    Mirrors the Lean ``def CleanAcceptUpdate (old new : CleanMetrics)
    (tol : CleanTolerances) : Prop`` in its exact field order. An accepted
    update improves ``clean_vgs`` by at least ``tau``, bounds the ``hack_risk``
    and ``dcr`` increases, does not regress ``calibration``/``ood``, bounds the
    cost/latency increases, and carries no regression flag (Lean
    ``accepted_update_*`` lemmas). Composed soundness is
    ``clean_pipeline_acceptance_sound``.

    Args:
        tol: tolerance budget (must validate per ``CleanTolerances`` rules).
        old: previous-checkpoint metrics.
        new: candidate-checkpoint metrics.

    Returns:
        A ``CleanGateDecision`` with ``accepted=True`` iff every condition held;
        otherwise ``reasons`` lists each failing condition by its canonical name
        (in Lean field order).
    """
    reasons: list[str] = []

    # 1. new.clean_vgs ≥ old.clean_vgs + tol.tau
    if not (new.clean_vgs >= old.clean_vgs + tol.tau):
        reasons.append(REASON_CLEAN_VGS_NOT_IMPROVED)
    # 2. new.hack_risk ≤ old.hack_risk + tol.eps_h
    if not (new.hack_risk <= old.hack_risk + tol.eps_h):
        reasons.append(REASON_HACK_RISK_INCREASED)
    # 3. new.calibration ≥ old.calibration − tol.eps_c
    if not (new.calibration >= old.calibration - tol.eps_c):
        reasons.append(REASON_CALIBRATION_REGRESSED)
    # 4. new.ood ≥ old.ood − tol.eps_o
    if not (new.ood_score >= old.ood_score - tol.eps_o):
        reasons.append(REASON_OOD_REGRESSED)
    # 5. new.dcr ≤ old.dcr + tol.eps_d
    if not (new.dcr <= old.dcr + tol.eps_d):
        reasons.append(REASON_DCR_INCREASED)
    # 6. new.cost ≤ old.cost + tol.eps_k
    if not (new.cost <= old.cost + tol.eps_k):
        reasons.append(REASON_COST_INCREASED)
    # 7. new.latency ≤ old.latency + tol.eps_l
    if not (new.latency <= old.latency + tol.eps_l):
        reasons.append(REASON_LATENCY_INCREASED)
    # 8. new.regression = false
    if new.regression:
        reasons.append(REASON_REGRESSION_FLAGGED)

    metrics_delta: dict[str, Any] = {
        "clean_vgs": new.clean_vgs - old.clean_vgs,
        "hack_risk": new.hack_risk - old.hack_risk,
        "calibration": new.calibration - old.calibration,
        "ood_score": new.ood_score - old.ood_score,
        "dcr": new.dcr - old.dcr,
        "cost": new.cost - old.cost,
        "latency": new.latency - old.latency,
        "regression": new.regression,
    }

    return CleanGateDecision(
        accepted=not reasons,
        reasons=tuple(reasons),
        metrics_delta=metrics_delta,
        old=old,
        new=new,
    )


__all__ = [
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
]
