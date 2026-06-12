"""Public-hidden generalization gap — mirrors ``GeneralizationGap.lean``.

Module **E** of the contamination-resistant evaluation track. The
public-hidden generalization gap is ``gap = public_score − hidden_score``; a
*large gap* relative to a threshold ``tau ≥ 0`` is ``gap > tau``.

The properties are machine-verified in Lean 4 (namespace
``Verifiable.GeneralizationGap``); this is the property-tested Python mirror.
The relevant theorems are:

* ``positive_gap_implies_hidden_underperforms`` — ``gap > 0 ⇒ hidden < public``.
* ``large_gap_implies_hidden_underperforms`` — for ``tau ≥ 0``,
  ``gap > tau ⇒ hidden < public``.
* ``reject_on_large_gap_sound`` — rejecting precisely when ``large_gap`` holds
  is sound: a rejected update genuinely has the hidden score underperforming.
"""

from __future__ import annotations

import math


def _check_unit(name: str, x: float) -> None:
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite, got {x!r}")
    if not (0.0 <= x <= 1.0):
        raise ValueError(f"{name} must be in [0, 1], got {x!r}")


def _check_nonneg(name: str, x: float) -> None:
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite, got {x!r}")
    if x < 0.0:
        raise ValueError(f"{name} must be ≥ 0, got {x!r}")


def gap(public_score: float, hidden_score: float) -> float:
    """Public-hidden generalization gap ``public_score − hidden_score``.

    Mirrors ``Verifiable.GeneralizationGap.gap`` (``pub - hidden``).

    Args:
        public_score: public-benchmark score in ``[0, 1]``.
        hidden_score: hidden-eval score in ``[0, 1]``.

    Returns:
        The gap, which lies in ``[-1, 1]`` for unit inputs (Lean
        ``gap_bounded``). A positive gap implies the hidden score underperforms
        (Lean ``positive_gap_implies_hidden_underperforms``).

    Raises:
        ValueError: if either score is non-finite or outside ``[0, 1]``.
    """
    _check_unit("public_score", public_score)
    _check_unit("hidden_score", hidden_score)
    return public_score - hidden_score


def large_gap(public_score: float, hidden_score: float, tau: float) -> bool:
    """Whether the generalization gap exceeds ``tau`` (the reject predicate).

    Mirrors ``Verifiable.GeneralizationGap.large_gap``. A ``True`` result is a
    sound reason to reject: it implies ``hidden_score < public_score`` (Lean
    ``reject_on_large_gap_sound``).

    Args:
        public_score: public-benchmark score in ``[0, 1]``.
        hidden_score: hidden-eval score in ``[0, 1]``.
        tau: nonnegative gap threshold.

    Returns:
        ``True`` iff ``gap(public_score, hidden_score) > tau``.

    Raises:
        ValueError: if either score is outside ``[0, 1]``, or ``tau`` is
            non-finite or negative.
    """
    _check_nonneg("tau", tau)
    return gap(public_score, hidden_score) > tau


__all__ = ["gap", "large_gap"]
