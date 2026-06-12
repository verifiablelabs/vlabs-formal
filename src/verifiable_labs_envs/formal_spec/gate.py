"""Self-improvement gate — mirrors ``formal/VerifiableLabsFormal/SelfImprovementGate.lean``.

The ``accept_update`` function evaluates the seven-condition ``AcceptUpdate``
predicate proved sound in Lean (theorems ``accepted_sequence_mono_VGS`` and
``accepted_sequence_VGS_lower_bound``). Any sequence of model updates
accepted by this predicate is monotone non-decreasing in VGS, and after
``n`` acceptances satisfies ``VGS_n ≥ VGS_0 + n·τ``.

This is a *specification mirror* — the production checkpoint promotion
pipeline lives elsewhere (see Phase 30.F/G). The CLI wrapper
``vlabs-prm-eval gate`` consumes eval cards and reuses this predicate.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


# ---------------------------------------------------------------------
# Domain validation helpers (local — not re-used from formulas.py to
# keep this file self-contained for downstream importers).
# ---------------------------------------------------------------------
def _check_finite(name: str, x: float) -> None:
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite, got {x!r}")


def _check_nonneg_finite(name: str, x: float) -> None:
    _check_finite(name, x)
    if x < 0.0:
        raise ValueError(f"{name} must be ≥ 0, got {x!r}")


# ---------------------------------------------------------------------
# ModelMetrics — mirrors Lean ``structure ModelMetrics``
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class ModelMetrics:
    """Metrics describing one model checkpoint.

    Mirrors the Lean ``structure ModelMetrics`` field-for-field:

    * ``vgs``         — Verifiable Generalization Score (any real).
    * ``hack_risk``   — hackability estimate H (typically in [0, 1]).
    * ``calibration`` — calibration metric (typically in [0, 1]).
    * ``ood``         — out-of-distribution performance (any real).
    * ``cost``        — cost per audit ($, ≥ 0).
    * ``latency``     — wall-clock latency (seconds, ≥ 0).
    * ``regression``  — True iff a hard regression flag fired upstream.

    All floats must be finite.
    """

    vgs: float
    hack_risk: float
    calibration: float
    ood: float
    cost: float
    latency: float
    regression: bool

    def __post_init__(self) -> None:
        for name, x in (
            ("vgs", self.vgs),
            ("hack_risk", self.hack_risk),
            ("calibration", self.calibration),
            ("ood", self.ood),
        ):
            _check_finite(name, x)
        _check_nonneg_finite("cost", self.cost)
        _check_nonneg_finite("latency", self.latency)
        if not isinstance(self.regression, bool):
            raise ValueError(
                f"regression must be a bool, got {type(self.regression).__name__}"
            )


# ---------------------------------------------------------------------
# Tolerances — mirrors Lean ``structure Tolerances`` with its
# nonnegativity hypotheses (hτ, hH, hC, hO, hK, hL).
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class Tolerances:
    """Per-condition slack budgets.

    Mirrors the Lean ``structure Tolerances`` including the
    ``hτ ... hL`` proofs of non-negativity. Validated eagerly in
    ``__post_init__``.

    Default values are intentionally conservative — callers should
    tighten or loosen each per their checkpoint-promotion policy.
    """

    tau: float = 0.01
    eps_h: float = 0.02
    eps_c: float = 0.02
    eps_o: float = 0.02
    eps_k: float = 5.0      # $ per audit
    eps_l: float = 0.5      # seconds

    def __post_init__(self) -> None:
        for name, x in (
            ("tau", self.tau),
            ("eps_h", self.eps_h),
            ("eps_c", self.eps_c),
            ("eps_o", self.eps_o),
            ("eps_k", self.eps_k),
            ("eps_l", self.eps_l),
        ):
            _check_nonneg_finite(name, x)


# ---------------------------------------------------------------------
# GateDecision + accept_update
# ---------------------------------------------------------------------
# Canonical names for each of the seven AcceptUpdate conditions, in the
# order they appear in Lean. Tests assert each reason can fire
# independently; the CLI wraps these into a human-readable table.
REASON_VGS_GAIN_BELOW_TAU = "vgs_gain_below_tau"
REASON_HACK_RISK_EXCEEDED = "hack_risk_exceeded"
REASON_CALIBRATION_DROPPED = "calibration_dropped"
REASON_OOD_DROPPED = "ood_dropped"
REASON_COST_EXCEEDED = "cost_exceeded"
REASON_LATENCY_EXCEEDED = "latency_exceeded"
REASON_REGRESSION_FLAG_SET = "regression_flag_set"


@dataclass(frozen=True)
class GateDecision:
    """Result of a single gate evaluation.

    ``accepted`` is True iff every one of the seven Lean ``AcceptUpdate``
    conditions held. ``reasons`` lists the named reasons for each
    failing condition, in Lean order. On an accept, ``reasons`` is
    empty.
    """

    accepted: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)


def accept_update(
    tol: Tolerances,
    old: ModelMetrics,
    new: ModelMetrics,
) -> GateDecision:
    """Evaluate the seven-condition ``AcceptUpdate`` predicate.

    Mirrors the Lean ``def AcceptUpdate (tol : Tolerances)
    (M_old M_new : ModelMetrics) : Prop`` in its exact field order.

    Args:
        tol: tolerance budget (must validate per ``Tolerances`` rules).
        old: previous-checkpoint metrics.
        new: candidate-checkpoint metrics.

    Returns:
        A ``GateDecision`` with ``accepted=True`` iff every condition
        held; otherwise ``reasons`` lists each failing condition by its
        canonical name (in Lean field order).
    """
    reasons: list[str] = []

    # 1. M_new.VGS ≥ M_old.VGS + tol.τ
    if not (new.vgs >= old.vgs + tol.tau):
        reasons.append(REASON_VGS_GAIN_BELOW_TAU)
    # 2. M_new.HackRisk ≤ M_old.HackRisk + tol.ε_H
    if not (new.hack_risk <= old.hack_risk + tol.eps_h):
        reasons.append(REASON_HACK_RISK_EXCEEDED)
    # 3. M_new.Calibration ≥ M_old.Calibration − tol.ε_C
    if not (new.calibration >= old.calibration - tol.eps_c):
        reasons.append(REASON_CALIBRATION_DROPPED)
    # 4. M_new.OOD ≥ M_old.OOD − tol.ε_O
    if not (new.ood >= old.ood - tol.eps_o):
        reasons.append(REASON_OOD_DROPPED)
    # 5. M_new.Cost ≤ M_old.Cost + tol.ε_K
    if not (new.cost <= old.cost + tol.eps_k):
        reasons.append(REASON_COST_EXCEEDED)
    # 6. M_new.Latency ≤ M_old.Latency + tol.ε_L
    if not (new.latency <= old.latency + tol.eps_l):
        reasons.append(REASON_LATENCY_EXCEEDED)
    # 7. M_new.Regression = false
    if new.regression:
        reasons.append(REASON_REGRESSION_FLAG_SET)

    return GateDecision(accepted=not reasons, reasons=tuple(reasons))


__all__ = [
    "ModelMetrics",
    "Tolerances",
    "GateDecision",
    "accept_update",
    "REASON_VGS_GAIN_BELOW_TAU",
    "REASON_HACK_RISK_EXCEEDED",
    "REASON_CALIBRATION_DROPPED",
    "REASON_OOD_DROPPED",
    "REASON_COST_EXCEEDED",
    "REASON_LATENCY_EXCEEDED",
    "REASON_REGRESSION_FLAG_SET",
]
