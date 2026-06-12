"""Property-based parity tests for ``formal_spec.clean_vgs``.

Mirrors ``formal/VerifiableLabsFormal/CleanVGS.lean`` (module D):
``clean_vgs_le_raw_vgs``, ``clean_vgs_monotone_raw``,
``clean_vgs_antitone_dcr``, ``clean_vgs_penalizes_full_contamination``.
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from verifiable_labs_envs.formal_spec.clean_vgs import clean_vgs

EPS = 1e-9

unit = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
beta_s = st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)


# --- D.1 clean_vgs_le_raw_vgs ---
@given(unit, unit, beta_s)
def test_clean_vgs_le_raw_vgs(raw_vgs, dcr, beta):
    assert clean_vgs(raw_vgs, dcr, beta) <= raw_vgs + EPS


# --- D.2 clean_vgs_monotone_raw ---
@given(unit, unit, unit, beta_s)
def test_clean_vgs_monotone_raw(r1, r2, dcr, beta):
    lo, hi = sorted((r1, r2))
    assert clean_vgs(lo, dcr, beta) <= clean_vgs(hi, dcr, beta) + EPS


# --- D.3 clean_vgs_antitone_dcr ---
@given(unit, unit, unit, beta_s)
def test_clean_vgs_antitone_dcr(raw_vgs, d1, d2, beta):
    lo, hi = sorted((d1, d2))
    assert clean_vgs(raw_vgs, hi, beta) <= clean_vgs(raw_vgs, lo, beta) + EPS


# --- D.4 clean_vgs_penalizes_full_contamination ---
@given(unit, beta_s)
def test_clean_vgs_penalizes_full_contamination(raw_vgs, beta):
    assert abs(clean_vgs(raw_vgs, 1.0, beta) - (-beta)) <= EPS


# --- domain validation ---
@pytest.mark.parametrize(
    "raw_vgs, dcr, beta",
    [(-0.01, 0.5, 0.5), (1.01, 0.5, 0.5), (0.5, -0.01, 0.5),
     (0.5, 1.01, 0.5), (0.5, 0.5, -0.01), (0.5, 0.5, float("inf")),
     (float("nan"), 0.5, 0.5)],
)
def test_clean_vgs_rejects_out_of_range(raw_vgs, dcr, beta):
    with pytest.raises(ValueError):
        clean_vgs(raw_vgs, dcr, beta)
