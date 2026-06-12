"""Property-based parity tests for ``formal_spec.contamination_risk``.

Mirrors ``formal/VerifiableLabsFormal/ContaminationRisk.lean`` (module C):
``clean_score_bounds``, ``clean_score_le_raw``,
``clean_score_eq_raw_iff_zero_dcr_or_zero_raw``, ``clean_score_monotone_raw``,
``clean_score_antitone_dcr``, ``clean_score_zero_at_full_contamination``.
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from verifiable_labs_envs.formal_spec.contamination_risk import clean_score

EPS = 1e-9

unit = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


# --- C.1 clean_score_bounds ---
@given(unit, unit)
def test_clean_score_bounds(raw, dcr):
    s = clean_score(raw, dcr)
    assert -EPS <= s <= 1.0 + EPS


# --- C.2 clean_score_le_raw ---
@given(unit, unit)
def test_clean_score_le_raw(raw, dcr):
    assert clean_score(raw, dcr) <= raw + EPS


# --- C.3 clean_score_eq_raw_iff_zero_dcr_or_zero_raw ---
# The Lean statement is an exact algebraic iff (raw == 0 or dcr == 0). Ported to
# floats we test the two directions on well-separated inputs to avoid the
# inherently fuzzy near-zero band where `raw*dcr` is sub-tolerance.
@given(unit, unit)
def test_clean_score_eq_raw_when_zero_dcr_or_zero_raw(raw, dcr):
    # Reverse direction: raw == 0 or dcr == 0  =>  clean == raw (exactly).
    assert clean_score(0.0, dcr) == 0.0
    assert clean_score(raw, 0.0) == raw


@given(
    st.floats(min_value=0.1, max_value=1.0, allow_nan=False),
    st.floats(min_value=0.1, max_value=1.0, allow_nan=False),
)
def test_clean_score_strictly_below_raw_when_both_positive(raw, dcr):
    # Forward direction (contrapositive): raw > 0 and dcr > 0  =>  clean < raw.
    assert clean_score(raw, dcr) < raw


# --- C.4 clean_score_monotone_raw ---
@given(unit, unit, unit)
def test_clean_score_monotone_raw(r1, r2, dcr):
    lo, hi = sorted((r1, r2))
    assert clean_score(lo, dcr) <= clean_score(hi, dcr) + EPS


# --- C.5 clean_score_antitone_dcr ---
@given(unit, unit, unit)
def test_clean_score_antitone_dcr(raw, d1, d2):
    lo, hi = sorted((d1, d2))
    assert clean_score(raw, hi) <= clean_score(raw, lo) + EPS


# --- C.6 clean_score_zero_at_full_contamination ---
@given(unit)
def test_clean_score_zero_at_full_contamination(raw):
    assert abs(clean_score(raw, 1.0)) <= EPS


# --- domain validation ---
@pytest.mark.parametrize(
    "raw, dcr",
    [(-0.01, 0.5), (1.01, 0.5), (0.5, -0.01), (0.5, 1.01),
     (float("nan"), 0.5), (0.5, float("inf"))],
)
def test_clean_score_rejects_out_of_range(raw, dcr):
    with pytest.raises(ValueError):
        clean_score(raw, dcr)
