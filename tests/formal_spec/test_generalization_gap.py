"""Property-based parity tests for ``formal_spec.generalization_gap``.

Mirrors ``formal/VerifiableLabsFormal/GeneralizationGap.lean`` (module E):
``positive_gap_implies_hidden_underperforms``,
``large_gap_implies_hidden_underperforms``, ``zero_gap_iff_equal``,
``gap_bounded``, ``reject_on_large_gap_sound``.
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from verifiable_labs_envs.formal_spec.generalization_gap import gap, large_gap

EPS = 1e-9

unit = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
nonneg = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


# --- E.1 positive_gap_implies_hidden_underperforms ---
@given(unit, unit)
def test_positive_gap_implies_hidden_underperforms(public_score, hidden_score):
    if gap(public_score, hidden_score) > EPS:
        assert hidden_score < public_score


# --- E.2 large_gap_implies_hidden_underperforms (predicate) ---
@given(unit, unit, nonneg)
def test_large_gap_implies_hidden_underperforms(public_score, hidden_score, tau):
    if large_gap(public_score, hidden_score, tau):
        assert hidden_score < public_score


# --- E.3 zero_gap_iff_equal ---
@given(unit, unit)
def test_zero_gap_iff_equal(public_score, hidden_score):
    is_zero = abs(gap(public_score, hidden_score)) <= EPS
    is_equal = abs(public_score - hidden_score) <= EPS
    assert is_zero == is_equal


# --- E.4 gap_bounded ---
@given(unit, unit)
def test_gap_bounded(public_score, hidden_score):
    g = gap(public_score, hidden_score)
    assert -1.0 - EPS <= g <= 1.0 + EPS


# --- E.5 reject_on_large_gap_sound ---
@given(unit, unit, nonneg)
def test_reject_on_large_gap_sound(public_score, hidden_score, tau):
    # The reject predicate is exactly large_gap; a reject implies underperformance.
    rejected = large_gap(public_score, hidden_score, tau)
    if rejected:
        assert hidden_score < public_score


def test_large_gap_is_strict_above_tau():
    # gap exactly equal to tau is NOT large (strict >). Use exactly
    # representable values so gap == 0.25 holds bit-for-bit.
    assert gap(0.75, 0.5) == 0.25
    assert large_gap(0.75, 0.5, 0.25) is False
    assert large_gap(0.75, 0.5, 0.125) is True


# --- domain validation ---
@pytest.mark.parametrize(
    "public_score, hidden_score, tau",
    [(-0.01, 0.5, 0.0), (1.01, 0.5, 0.0), (0.5, -0.01, 0.0),
     (0.5, 1.01, 0.0), (0.5, 0.5, -0.01), (0.5, 0.5, float("inf"))],
)
def test_large_gap_rejects_out_of_range(public_score, hidden_score, tau):
    with pytest.raises(ValueError):
        large_gap(public_score, hidden_score, tau)
