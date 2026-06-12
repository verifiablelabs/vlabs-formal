"""Contamination-adjusted score — mirrors ``ContaminationRisk.lean``.

Module **C** of the contamination-resistant evaluation track. Given a raw
score ``raw ∈ [0, 1]`` and a data-contamination-risk score ``dcr ∈ [0, 1]``,
the contamination-adjusted (clean) score is ``clean_score = raw·(1 − dcr)``.

The mathematical properties of ``clean_score`` are machine-verified in Lean 4
(namespace ``Verifiable.ContaminationRisk``); this is the property-tested
Python mirror. The relevant theorems are:

* ``clean_score_bounds`` — the clean score stays in ``[0, 1]``.
* ``clean_score_le_raw`` — the clean score never exceeds the raw score.
* ``clean_score_monotone_raw`` — monotone (nondecreasing) in ``raw``.
* ``clean_score_antitone_dcr`` — antitone (nonincreasing) in ``dcr``.
* ``clean_score_zero_at_full_contamination`` — collapses to 0 at ``dcr = 1``.
"""

from __future__ import annotations

import math


def _check_unit(name: str, x: float) -> None:
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite, got {x!r}")
    if not (0.0 <= x <= 1.0):
        raise ValueError(f"{name} must be in [0, 1], got {x!r}")


def clean_score(raw: float, dcr: float) -> float:
    """Contamination-adjusted score ``raw·(1 − dcr)``.

    Mirrors ``Verifiable.ContaminationRisk.clean_score``.

    Args:
        raw: raw score in ``[0, 1]``.
        dcr: data-contamination-risk score in ``[0, 1]``.

    Returns:
        The contamination-adjusted score, which lies in ``[0, 1]`` and never
        exceeds ``raw`` (Lean ``clean_score_bounds`` / ``clean_score_le_raw``).

    Raises:
        ValueError: if ``raw`` or ``dcr`` is non-finite or outside ``[0, 1]``.
    """
    _check_unit("raw", raw)
    _check_unit("dcr", dcr)
    return raw * (1.0 - dcr)


__all__ = ["clean_score"]
