"""Property-based parity tests for ``formal_spec.formulas.difficulty_update``.

Mirrors theorems in
``formal/VerifiableLabsFormal/AdaptiveDifficulty.lean``:
``fixedPoint_iff_solve_rate_eq``, ``stability_nonexpansive``,
``stability_strict``.

The Lean proofs are stated for an arbitrary L-Lipschitz antitone solve
rate ``s : ℝ → ℝ``. These tests fix a one-parameter family
``s(d) = s* − m·(d − d*)`` (antitone for m > 0, L-Lipschitz with L = m)
and pick η so that ``η·m < 1`` — this satisfies the Lean hypotheses
exactly.
"""

from __future__ import annotations

import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from verifiable_labs_envs.formal_spec.formulas import difficulty_update

TOL = 1e-9


# ---------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------
positive_floats = st.floats(min_value=1e-3, max_value=1.0, allow_nan=False, allow_infinity=False)
real_floats = st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False)


def _make_solve_rate(s_star: float, d_star: float, m: float):
    """Antitone, L=m-Lipschitz solve rate with fixed point at d_star.

    ``s(d) = s* − m · (d − d*)`` ⇒ ``s(d*) = s*`` and ``s`` is strictly
    decreasing in ``d``.
    """
    def s(d: float) -> float:
        return s_star - m * (d - d_star)
    return s


# =====================================================================
# fixedPoint_iff_solve_rate_eq
# =====================================================================
@given(eta=positive_floats, s_star=real_floats, d_star=real_floats,
       m=positive_floats)
def test_difficulty_fixed_point_when_s_equals_s_star(eta, s_star, d_star, m):
    """Mirrors ``fixedPoint_iff_solve_rate_eq`` (⇐ direction):

    if ``s(d*) = s_star``, then ``difficulty_update(η, s_star, s(d*), d*) = d*``.
    """
    s = _make_solve_rate(s_star, d_star, m)
    d_next = difficulty_update(eta, s_star, s(d_star), d_star)
    assert math.isclose(d_next, d_star, abs_tol=1e-9, rel_tol=1e-9)


@given(eta=positive_floats, s_star=real_floats, d_star=real_floats,
       m=positive_floats,
       offset=st.floats(min_value=0.01, max_value=10.0, allow_nan=False, allow_infinity=False))
def test_difficulty_not_fixed_point_when_s_differs(eta, s_star, d_star, m, offset):
    """Mirrors ``fixedPoint_iff_solve_rate_eq`` (⇒ direction):

    at any ``d ≠ d*``, the next step moves *away* from ``d`` (toward d*),
    so ``d`` is not a fixed point.
    """
    s = _make_solve_rate(s_star, d_star, m)
    d_off = d_star + offset
    d_next = difficulty_update(eta, s_star, s(d_off), d_off)
    # s(d_off) = s_star - m*offset < s_star, so update decreases d:
    assert d_next < d_off


# =====================================================================
# stability_nonexpansive  (under η·L < 1, L = m)
# =====================================================================
@given(s_star=real_floats, d_star=real_floats,
       m=positive_floats,
       offset=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
       eta_scale=st.floats(min_value=0.01, max_value=0.99, allow_nan=False, allow_infinity=False))
def test_difficulty_stability_nonexpansive(s_star, d_star, m, offset, eta_scale):
    """Mirrors ``stability_nonexpansive``:

    Under antitone L-Lipschitz s and ``η·L < 1``, ``|d' − d*| ≤ |d − d*|``.
    Choose η = eta_scale / m so that η·m = eta_scale ∈ (0, 1).
    """
    eta = eta_scale / m
    s = _make_solve_rate(s_star, d_star, m)
    d = d_star + offset
    d_next = difficulty_update(eta, s_star, s(d), d)
    assert abs(d_next - d_star) <= abs(d - d_star) + TOL


# =====================================================================
# stability_strict  (off the fixed point)
# =====================================================================
@given(s_star=real_floats, d_star=real_floats,
       m=positive_floats,
       offset=st.floats(min_value=0.05, max_value=10.0, allow_nan=False, allow_infinity=False),
       eta_scale=st.floats(min_value=0.05, max_value=0.95, allow_nan=False, allow_infinity=False))
def test_difficulty_stability_strict(s_star, d_star, m, offset, eta_scale):
    """Mirrors ``stability_strict``: strict contraction for ``d ≠ d*``."""
    eta = eta_scale / m
    s = _make_solve_rate(s_star, d_star, m)
    d = d_star + offset  # offset > 0 ⇒ d ≠ d*
    d_next = difficulty_update(eta, s_star, s(d), d)
    # The exact contraction factor is (1 − η·m) = (1 − eta_scale).
    expected_factor = 1.0 - eta_scale
    assert abs(d_next - d_star) < abs(d - d_star)
    assert math.isclose(
        abs(d_next - d_star),
        expected_factor * abs(d - d_star),
        rel_tol=1e-7,
        abs_tol=1e-9,
    )


# =====================================================================
# Domain enforcement
# =====================================================================
def test_difficulty_eta_must_be_positive():
    """Lean theorems all assume ``η > 0``; the mirror raises on η ≤ 0."""
    with pytest.raises(ValueError):
        difficulty_update(0.0, 0.5, 0.4, 1.0)
    with pytest.raises(ValueError):
        difficulty_update(-0.1, 0.5, 0.4, 1.0)
