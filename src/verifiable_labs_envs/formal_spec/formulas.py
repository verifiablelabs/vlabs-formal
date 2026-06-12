"""Pure-function Python mirrors of the formulas verified in Lean 4.

Every public symbol below cites the Lean module + theorem(s) it mirrors.
Domain hypotheses are enforced eagerly with ``ValueError`` — out-of-range
inputs are **not** silently clamped (the Lean theorems take these as
preconditions, so any production caller that wants the proved property
must respect them).

The functions in this module are intentionally minimal — they mirror
the *mathematical specification*, not the production calibration or
routing implementations in
``src/verifiable_labs_envs/process_reward/calibration.py`` and
``src/verifiable_labs_envs/training/adaptive_difficulty.py``. Property
tests in ``tests/formal_spec/`` exercise these mirrors against the
Lean-proved invariants.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


# ---------------------------------------------------------------------
# Domain enforcement
# ---------------------------------------------------------------------
def _check_unit(name: str, x: float) -> None:
    """Raise ``ValueError`` unless ``x ∈ [0, 1]`` and finite."""
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite, got {x!r}")
    if x < 0.0 or x > 1.0:
        raise ValueError(f"{name} must lie in [0, 1], got {x!r}")


def _check_nonneg(name: str, x: float) -> None:
    """Raise ``ValueError`` unless ``x ≥ 0`` and finite."""
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite, got {x!r}")
    if x < 0.0:
        raise ValueError(f"{name} must be ≥ 0, got {x!r}")


def _check_positive(name: str, x: float) -> None:
    """Raise ``ValueError`` unless ``x > 0`` and finite."""
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite, got {x!r}")
    if x <= 0.0:
        raise ValueError(f"{name} must be > 0, got {x!r}")


# ---------------------------------------------------------------------
# Calibrated reward — formal/VerifiableLabsFormal/CalibratedReward.lean
# ---------------------------------------------------------------------
def calibrated_reward(v: float, c: float, h: float, lam: float) -> float:
    """Calibrated reward ``R* = V·C − λ·H``.

    Mirrors the Lean definition ``calibratedReward`` and the theorems
    ``calibratedReward_bounded`` (R* ∈ [−λ, 1] for V,C,H ∈ [0,1] and λ ≥ 0),
    ``calibratedReward_mono_V``, ``calibratedReward_mono_C``,
    ``calibratedReward_anti_H``, and ``calibratedReward_strict_anti_H``
    (strict anti-monotonicity in H when λ > 0).

    Args:
        v:   value V ∈ [0, 1].
        c:   confidence C ∈ [0, 1].
        h:   hackability estimate H ∈ [0, 1].
        lam: penalty weight λ ≥ 0.

    Raises:
        ValueError: if any input violates its domain hypothesis.
    """
    _check_unit("v", v)
    _check_unit("c", c)
    _check_unit("h", h)
    _check_nonneg("lam", lam)
    return v * c - lam * h


# ---------------------------------------------------------------------
# Verifiable Generalization Score — formal/VerifiableLabsFormal/VGS.lean
# ---------------------------------------------------------------------
def vgs(
    g: float,
    c: float,
    r: float,
    d: float,
    h: float,
    k: float,
    lat: float,
    lam: float,
    mu: float,
    nu: float,
) -> float:
    """Verifiable Generalization Score ``VGS = G·C·R·D − λH − μK − νL``.

    Mirrors the Lean definition ``VGS`` and the theorems
    ``VGS_bounded`` (in [−(λ+μ+ν), 1]), ``VGS_mono_{G,C,R,D}``,
    ``VGS_anti_{H,K,L}``, and ``VGS_strict_mono_G`` (strict increase in G
    when C,R,D > 0).

    Args:
        g, c, r, d: quality terms, each in [0, 1].
        h, k, lat:  penalty terms (Lean's H, K, L — ``lat`` for latency,
                    avoids ambiguous bare ``l``). Each in [0, 1].
        lam, mu, nu: penalty weights, each ≥ 0.

    Raises:
        ValueError: if any input violates its domain hypothesis.
    """
    for name, x in (("g", g), ("c", c), ("r", r), ("d", d), ("h", h), ("k", k), ("lat", lat)):
        _check_unit(name, x)
    for name, x in (("lam", lam), ("mu", mu), ("nu", nu)):
        _check_nonneg(name, x)
    return g * c * r * d - lam * h - mu * k - nu * lat


# ---------------------------------------------------------------------
# Adaptive difficulty — formal/VerifiableLabsFormal/AdaptiveDifficulty.lean
# ---------------------------------------------------------------------
def difficulty_update(eta: float, s_star: float, s_t: float, d_t: float) -> float:
    """One step of the adaptive difficulty update ``d' = d + η·(s − s*)``.

    Mirrors the Lean definition ``difficultyUpdate``. The Lean theorems
    ``fixedPoint_iff_solve_rate_eq``, ``exists_fixedPoint``,
    ``stability_nonexpansive``, and ``stability_strict`` characterise the
    fixed-point behaviour under antitone, L-Lipschitz solve rate with
    η·L < 1 — those properties are property-tested in
    ``tests/formal_spec/test_difficulty_properties.py``.

    Args:
        eta:    step size η > 0.
        s_star: target solve rate ∈ ℝ (commonly in [0, 1]).
        s_t:    observed solve rate at the current step.
        d_t:    current difficulty.

    Raises:
        ValueError: if η ≤ 0 or any input is not finite.
    """
    _check_positive("eta", eta)
    for name, x in (("s_star", s_star), ("s_t", s_t), ("d_t", d_t)):
        if not math.isfinite(x):
            raise ValueError(f"{name} must be finite, got {x!r}")
    return d_t + eta * (s_t - s_star)


# ---------------------------------------------------------------------
# Model routing — formal/VerifiableLabsFormal/ModelRouting.lean
# ---------------------------------------------------------------------
def routing_utility(
    q: float,
    cost: float,
    latency: float,
    risk: float,
    gamma: float,
    delta: float,
    rho: float,
) -> float:
    """Routing utility ``U = Q − γ·Cost − δ·Latency − ρ·Risk``.

    Mirrors the Lean definition ``routingUtility``. The theorems
    ``selected_model_optimal``, ``cheaper_model_preferred``, and
    ``near_optimal_under_error`` require γ, δ, ρ ≥ 0; those preconditions
    are enforced here.

    Args:
        q:                  quality estimate Q (any real).
        cost, latency, risk: non-negative cost/latency/risk terms.
        gamma, delta, rho:  non-negative trade-off weights.

    Raises:
        ValueError: if any tradeoff weight or non-negative term is
            negative or non-finite.
    """
    for name, x in (("q", q),):
        if not math.isfinite(x):
            raise ValueError(f"{name} must be finite, got {x!r}")
    for name, x in (
        ("cost", cost),
        ("latency", latency),
        ("risk", risk),
        ("gamma", gamma),
        ("delta", delta),
        ("rho", rho),
    ):
        _check_nonneg(name, x)
    return q - gamma * cost - delta * latency - rho * risk


@dataclass(frozen=True)
class _Candidate:
    """Internal representation of one routing candidate."""

    id: str
    utility: float


def select_model(
    candidates: Sequence[tuple[str, float] | _Candidate],
) -> str:
    """Return the model ``id`` maximising routing utility.

    Mirrors the Lean ``selectedModel`` definition + ``selected_model_optimal``
    theorem. Argmax over the supplied candidates; ties are broken
    deterministically by lexicographic minimum of ``id`` (matching the
    Lean ``Finset.min'`` tie-break for ``DecidableEq M``).

    Args:
        candidates: iterable of ``(id: str, utility: float)`` pairs. Must
            contain at least one element (Lean's ``selectedModel``
            requires ``models.Nonempty``).

    Returns:
        The ``id`` of the candidate with the maximum utility (lex tie-break).

    Raises:
        ValueError: on empty input, non-finite utility, or duplicate ids.
    """
    items: list[_Candidate] = []
    seen: set[str] = set()
    for item in candidates:
        if isinstance(item, _Candidate):
            cid, u = item.id, item.utility
        else:
            cid, u = item
        if not isinstance(cid, str):
            raise ValueError(f"candidate id must be str, got {cid!r}")
        if not math.isfinite(u):
            raise ValueError(f"candidate {cid!r} utility must be finite, got {u!r}")
        if cid in seen:
            raise ValueError(f"duplicate candidate id {cid!r}")
        seen.add(cid)
        items.append(_Candidate(cid, float(u)))
    if not items:
        raise ValueError("select_model requires a non-empty candidate list")
    # max-of (utility, then lex min of id by negating sort key on id):
    return min(items, key=lambda c: (-c.utility, c.id)).id
