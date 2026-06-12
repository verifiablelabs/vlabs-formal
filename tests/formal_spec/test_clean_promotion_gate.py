"""Property-based parity tests for ``formal_spec.clean_promotion_gate``.

Mirrors ``formal/VerifiableLabsFormal/CleanPromotionGate.lean`` (module F):
the eight-condition ``CleanAcceptUpdate`` predicate,
``accepted_update_improves_clean_vgs``, ``accepted_update_bounds_hack_risk``,
``accepted_update_bounds_dcr``, ``accepted_update_no_regression``,
``accepted_sequence_clean_vgs_monotone``, ``accepted_sequence_clean_vgs_growth``.
"""

from __future__ import annotations

from dataclasses import replace

import pytest
from hypothesis import given
from hypothesis import strategies as st

from verifiable_labs_envs.formal_spec.clean_promotion_gate import (
    REASON_CALIBRATION_REGRESSED,
    REASON_CLEAN_VGS_NOT_IMPROVED,
    REASON_COST_INCREASED,
    REASON_DCR_INCREASED,
    REASON_HACK_RISK_INCREASED,
    REASON_LATENCY_INCREASED,
    REASON_OOD_REGRESSED,
    REASON_REGRESSION_FLAGGED,
    CleanMetrics,
    CleanTolerances,
    accept_clean_update,
)

TOL = 1e-9

unit = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
signed = st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False)
nonneg = st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)


def _metrics(**overrides) -> CleanMetrics:
    base = dict(
        raw_vgs=0.5,
        dcr=0.1,
        clean_vgs=0.5,
        public_score=0.8,
        hidden_score=0.7,
        ood_score=0.7,
        hack_risk=0.1,
        calibration=0.9,
        cost=1.0,
        latency=1.0,
        regression=False,
    )
    base.update(overrides)
    return CleanMetrics(**base)


@st.composite
def clean_metrics(draw) -> CleanMetrics:
    return CleanMetrics(
        raw_vgs=draw(unit),
        dcr=draw(unit),
        clean_vgs=draw(signed),
        public_score=draw(unit),
        hidden_score=draw(unit),
        ood_score=draw(signed),
        hack_risk=draw(signed),
        calibration=draw(signed),
        cost=draw(nonneg),
        latency=draw(nonneg),
        regression=draw(st.booleans()),
    )


@st.composite
def tolerances(draw) -> CleanTolerances:
    return CleanTolerances(
        tau=draw(nonneg),
        eps_h=draw(nonneg),
        eps_c=draw(nonneg),
        eps_o=draw(nonneg),
        eps_d=draw(nonneg),
        eps_k=draw(nonneg),
        eps_l=draw(nonneg),
    )


# =====================================================================
# F.1–F.4 — accepted update entails each guarantee
# =====================================================================
@given(clean_metrics(), clean_metrics(), tolerances())
def test_accept_improves_clean_vgs(old, new, tol):
    if accept_clean_update(tol, old, new).accepted:
        assert new.clean_vgs >= old.clean_vgs + tol.tau - TOL


@given(clean_metrics(), clean_metrics(), tolerances())
def test_accept_bounds_hack_risk(old, new, tol):
    if accept_clean_update(tol, old, new).accepted:
        assert new.hack_risk <= old.hack_risk + tol.eps_h + TOL


@given(clean_metrics(), clean_metrics(), tolerances())
def test_accept_bounds_dcr(old, new, tol):
    if accept_clean_update(tol, old, new).accepted:
        assert new.dcr <= old.dcr + tol.eps_d + TOL


@given(clean_metrics(), clean_metrics(), tolerances())
def test_accept_no_regression(old, new, tol):
    if accept_clean_update(tol, old, new).accepted:
        assert new.regression is False


# =====================================================================
# Accept path: a strictly-improving candidate clears the gate
# =====================================================================
def test_clean_accept_happy_path():
    tol = CleanTolerances()
    old = _metrics()
    new = _metrics(clean_vgs=0.6, dcr=0.08, hack_risk=0.09, ood_score=0.72,
                   calibration=0.91)
    decision = accept_clean_update(tol, old, new)
    assert decision.accepted is True
    assert decision.reasons == ()
    assert decision.metrics_delta["clean_vgs"] == pytest.approx(0.1, abs=1e-9)


# =====================================================================
# Each of the eight reject reasons triggers independently
# =====================================================================
def test_reject_clean_vgs_not_improved():
    tol = CleanTolerances()
    old = _metrics()
    new = _metrics(clean_vgs=0.5)  # no gain → below tau
    decision = accept_clean_update(tol, old, new)
    assert decision.accepted is False
    assert decision.reasons == (REASON_CLEAN_VGS_NOT_IMPROVED,)


def test_reject_hack_risk_increased():
    tol = CleanTolerances()
    old = _metrics()
    new = _metrics(clean_vgs=0.6, hack_risk=0.5)  # +0.4 > eps_h
    decision = accept_clean_update(tol, old, new)
    assert decision.accepted is False
    assert decision.reasons == (REASON_HACK_RISK_INCREASED,)


def test_reject_calibration_regressed():
    tol = CleanTolerances()
    old = _metrics()
    new = _metrics(clean_vgs=0.6, calibration=0.5)  # −0.4 < −eps_c
    decision = accept_clean_update(tol, old, new)
    assert decision.accepted is False
    assert decision.reasons == (REASON_CALIBRATION_REGRESSED,)


def test_reject_ood_regressed():
    tol = CleanTolerances()
    old = _metrics()
    new = _metrics(clean_vgs=0.6, ood_score=0.3)  # −0.4 < −eps_o
    decision = accept_clean_update(tol, old, new)
    assert decision.accepted is False
    assert decision.reasons == (REASON_OOD_REGRESSED,)


def test_reject_dcr_increased():
    tol = CleanTolerances()
    old = _metrics()
    new = _metrics(clean_vgs=0.6, dcr=0.5)  # +0.4 > eps_d
    decision = accept_clean_update(tol, old, new)
    assert decision.accepted is False
    assert decision.reasons == (REASON_DCR_INCREASED,)


def test_reject_cost_increased():
    tol = CleanTolerances()
    old = _metrics()
    new = _metrics(clean_vgs=0.6, cost=100.0)  # +99 > eps_k
    decision = accept_clean_update(tol, old, new)
    assert decision.accepted is False
    assert decision.reasons == (REASON_COST_INCREASED,)


def test_reject_latency_increased():
    tol = CleanTolerances()
    old = _metrics()
    new = _metrics(clean_vgs=0.6, latency=100.0)  # +99 > eps_l
    decision = accept_clean_update(tol, old, new)
    assert decision.accepted is False
    assert decision.reasons == (REASON_LATENCY_INCREASED,)


def test_reject_regression_flagged():
    tol = CleanTolerances()
    old = _metrics()
    new = _metrics(clean_vgs=0.6, regression=True)
    decision = accept_clean_update(tol, old, new)
    assert decision.accepted is False
    assert decision.reasons == (REASON_REGRESSION_FLAGGED,)


# =====================================================================
# F.5 — accepted sequence is monotone non-decreasing in clean_vgs
# F.6 — after n accepts, clean_vgs_n >= clean_vgs_0 + n*tau
# =====================================================================
@given(
    st.integers(min_value=0, max_value=12),
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=-0.5, max_value=0.5, allow_nan=False, allow_infinity=False),
)
def test_accepted_sequence_monotone_and_growth(n, tau, start):
    tol = CleanTolerances(tau=tau)
    # Build the sequence incrementally so each step's clean_vgs is *exactly*
    # the previous value plus tau (bit-for-bit), guaranteeing every step is an
    # accept regardless of float accumulation.
    seq = [_metrics(clean_vgs=start)]
    for _ in range(n):
        seq.append(_metrics(clean_vgs=seq[-1].clean_vgs + tau))
    for i in range(n):
        decision = accept_clean_update(tol, seq[i], seq[i + 1])
        assert decision.accepted is True
    # Monotone in clean_vgs.
    for i in range(n):
        assert seq[i + 1].clean_vgs >= seq[i].clean_vgs - TOL
    # Growth: clean_vgs_n >= clean_vgs_0 + n*tau.
    assert seq[n].clean_vgs >= seq[0].clean_vgs + n * tau - 1e-6


# =====================================================================
# Validation: non-finite metric is rejected at construction (mirrors gate.py)
# =====================================================================
@pytest.mark.parametrize("field", ["clean_vgs", "hack_risk", "calibration", "dcr"])
def test_clean_metrics_rejects_non_finite(field):
    with pytest.raises(ValueError):
        _metrics(**{field: float("nan")})


@pytest.mark.parametrize("field", ["cost", "latency"])
def test_clean_metrics_rejects_negative_cost_latency(field):
    with pytest.raises(ValueError):
        _metrics(**{field: -1.0})


def test_clean_tolerances_rejects_negative():
    with pytest.raises(ValueError):
        CleanTolerances(eps_d=-0.01)


def test_metrics_delta_records_all_gated_fields():
    decision = accept_clean_update(CleanTolerances(), _metrics(), _metrics(clean_vgs=0.7))
    for key in ("clean_vgs", "hack_risk", "calibration", "ood_score", "dcr",
                "cost", "latency", "regression"):
        assert key in decision.metrics_delta
    # round-trip the old/new handles
    assert decision.old is not None and decision.new is not None
    assert replace(decision.new, clean_vgs=0.7).clean_vgs == 0.7
