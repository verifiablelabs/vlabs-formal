"""Contamination-adjusted VGS — mirrors ``CleanVGS.lean``.

Module **D** of the contamination-resistant evaluation track. The
contamination-adjusted Verifiable Generalization Score is

    clean_vgs(raw_vgs, dcr, beta) = raw_vgs·(1 − dcr) − beta·dcr,

with ``raw_vgs ∈ [0, 1]``, ``dcr ∈ [0, 1]`` the data-contamination-risk score,
and ``beta ≥ 0`` a contamination penalty weight.

The properties are machine-verified in Lean 4 (namespace
``Verifiable.CleanVGS``); this is the property-tested Python mirror. The
relevant theorems are:

* ``clean_vgs_le_raw_vgs`` — the clean VGS never exceeds the raw VGS.
* ``clean_vgs_monotone_raw`` — monotone (nondecreasing) in ``raw_vgs``.
* ``clean_vgs_antitone_dcr`` — antitone (nonincreasing) in ``dcr``.
* ``clean_vgs_penalizes_full_contamination`` — collapses to ``-beta`` at
  ``dcr = 1``.
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


def clean_vgs(raw_vgs: float, dcr: float, beta: float) -> float:
    """Contamination-adjusted VGS ``raw_vgs·(1 − dcr) − beta·dcr``.

    Mirrors ``Verifiable.CleanVGS.clean_vgs``.

    Args:
        raw_vgs: raw Verifiable Generalization Score in ``[0, 1]``.
        dcr: data-contamination-risk score in ``[0, 1]``.
        beta: contamination penalty weight, ``≥ 0``.

    Returns:
        The contamination-adjusted VGS, which never exceeds ``raw_vgs``
        (Lean ``clean_vgs_le_raw_vgs``) and equals ``-beta`` at ``dcr = 1``
        (Lean ``clean_vgs_penalizes_full_contamination``).

    Raises:
        ValueError: if ``raw_vgs``/``dcr`` are non-finite or outside ``[0, 1]``,
            or ``beta`` is non-finite or negative.
    """
    _check_unit("raw_vgs", raw_vgs)
    _check_unit("dcr", dcr)
    _check_nonneg("beta", beta)
    return raw_vgs * (1.0 - dcr) - beta * dcr


__all__ = ["clean_vgs"]
