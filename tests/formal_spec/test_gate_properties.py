"""Property-based parity tests for ``formal_spec.gate``.

Mirrors ``formal/VerifiableLabsFormal/SelfImprovementGate.lean``:
* ``AcceptUpdate`` predicate (7 conditions, exact Lean order)
* ``accepted_sequence_mono_VGS`` (any accepted sequence is monotone
  non-decreasing in VGS)
* ``accepted_sequence_VGS_lower_bound``
  (after n acceptances, ``VGS_n ≥ VGS_0 + n·τ``)
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from verifiable_labs_envs.formal_spec.gate import (
    REASON_CALIBRATION_DROPPED,
    REASON_COST_EXCEEDED,
    REASON_HACK_RISK_EXCEEDED,
    REASON_LATENCY_EXCEEDED,
    REASON_OOD_DROPPED,
    REASON_REGRESSION_FLAG_SET,
    REASON_VGS_GAIN_BELOW_TAU,
    ModelMetrics,
    Tolerances,
    accept_update,
)

TOL = 1e-9


# ---------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------
real_floats = st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False)
nonneg_floats = st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)


@st.composite
def metrics(draw):
    return ModelMetrics(
        vgs=draw(real_floats),
        hack_risk=draw(real_floats),
        calibration=draw(real_floats),
        ood=draw(real_floats),
        cost=draw(nonneg_floats),
        latency=draw(nonneg_floats),
        regression=False,
    )


def _default_tol(tau: float = 0.01) -> Tolerances:
    return Tolerances(tau=tau)


# =====================================================================
# Spec: positive controls — random valid update with healthy headroom
# =====================================================================
@given(old=metrics(), bump=st.floats(min_value=0.05, max_value=1.0, allow_nan=False, allow_infinity=False))
def test_gate_accepts_clean_improving_update(old, bump):
    """Sanity: an update that strictly improves VGS (and changes nothing else) is accepted."""
    new = ModelMetrics(
        vgs=old.vgs + bump,
        hack_risk=old.hack_risk,
        calibration=old.calibration,
        ood=old.ood,
        cost=old.cost,
        latency=old.latency,
        regression=False,
    )
    d = accept_update(_default_tol(tau=0.01), old, new)
    assert d.accepted
    assert d.reasons == ()


# =====================================================================
# accepted_sequence_mono_VGS  +  accepted_sequence_VGS_lower_bound
# =====================================================================
@given(
    vgs0=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    bumps=st.lists(
        st.floats(min_value=0.0, max_value=0.3, allow_nan=False, allow_infinity=False),
        min_size=1, max_size=20,
    ),
    tau=st.floats(min_value=0.0, max_value=0.05, allow_nan=False, allow_infinity=False),
)
def test_gate_accepted_sequence_monotone_and_n_tau_bound(vgs0, bumps, tau):
    """Mirrors ``accepted_sequence_mono_VGS`` and
    ``accepted_sequence_VGS_lower_bound``."""
    tol = Tolerances(tau=tau)
    current = ModelMetrics(
        vgs=vgs0, hack_risk=0.1, calibration=0.9, ood=0.7,
        cost=1.0, latency=1.0, regression=False,
    )
    accepted_history = [current]
    for bump in bumps:
        # Force an accept by giving the new metrics exactly tau + bump
        # of VGS headroom and leaving every other field unchanged.
        candidate = ModelMetrics(
            vgs=current.vgs + tau + bump,
            hack_risk=current.hack_risk,
            calibration=current.calibration,
            ood=current.ood,
            cost=current.cost,
            latency=current.latency,
            regression=False,
        )
        d = accept_update(tol, current, candidate)
        assert d.accepted, d.reasons
        accepted_history.append(candidate)
        current = candidate

    # Monotone non-decreasing in VGS
    for i in range(1, len(accepted_history)):
        assert accepted_history[i].vgs >= accepted_history[i - 1].vgs - TOL

    # VGS_n ≥ VGS_0 + n·τ
    n = len(bumps)
    assert accepted_history[-1].vgs >= vgs0 + n * tau - 1e-7


# =====================================================================
# Each of the 7 reject reasons must fire independently
# =====================================================================
def _baseline_old() -> ModelMetrics:
    return ModelMetrics(
        vgs=0.50, hack_risk=0.10, calibration=0.90, ood=0.70,
        cost=1.00, latency=1.00, regression=False,
    )


def _baseline_new(**overrides) -> ModelMetrics:
    base = dict(
        vgs=0.60, hack_risk=0.10, calibration=0.90, ood=0.70,
        cost=1.00, latency=1.00, regression=False,
    )
    base.update(overrides)
    return ModelMetrics(**base)


def _default_tols() -> Tolerances:
    return Tolerances(
        tau=0.01, eps_h=0.02, eps_c=0.02, eps_o=0.02, eps_k=0.5, eps_l=0.5,
    )


def test_gate_reject_vgs_gain_below_tau():
    new = _baseline_new(vgs=0.504)  # delta 0.004 < tau 0.01
    d = accept_update(_default_tols(), _baseline_old(), new)
    assert not d.accepted
    assert REASON_VGS_GAIN_BELOW_TAU in d.reasons


def test_gate_reject_hack_risk_exceeded():
    new = _baseline_new(hack_risk=0.20)  # +0.10 > eps_h 0.02
    d = accept_update(_default_tols(), _baseline_old(), new)
    assert not d.accepted
    assert REASON_HACK_RISK_EXCEEDED in d.reasons


def test_gate_reject_calibration_dropped():
    new = _baseline_new(calibration=0.80)  # dropped 0.10 > eps_c 0.02
    d = accept_update(_default_tols(), _baseline_old(), new)
    assert not d.accepted
    assert REASON_CALIBRATION_DROPPED in d.reasons


def test_gate_reject_ood_dropped():
    new = _baseline_new(ood=0.50)  # dropped 0.20 > eps_o 0.02
    d = accept_update(_default_tols(), _baseline_old(), new)
    assert not d.accepted
    assert REASON_OOD_DROPPED in d.reasons


def test_gate_reject_cost_exceeded():
    new = _baseline_new(cost=2.0)  # +1.0 > eps_k 0.5
    d = accept_update(_default_tols(), _baseline_old(), new)
    assert not d.accepted
    assert REASON_COST_EXCEEDED in d.reasons


def test_gate_reject_latency_exceeded():
    new = _baseline_new(latency=2.5)  # +1.5 > eps_l 0.5
    d = accept_update(_default_tols(), _baseline_old(), new)
    assert not d.accepted
    assert REASON_LATENCY_EXCEEDED in d.reasons


def test_gate_reject_regression_flag_set():
    new = _baseline_new(regression=True)
    d = accept_update(_default_tols(), _baseline_old(), new)
    assert not d.accepted
    assert REASON_REGRESSION_FLAG_SET in d.reasons


# =====================================================================
# Reasons list preserves Lean field order (cosmetic but contract-relevant)
# =====================================================================
def test_gate_multiple_reasons_listed_in_lean_order():
    """Multiple simultaneous failures appear in the same order as the
    Lean ``AcceptUpdate`` definition."""
    old = _baseline_old()
    new = ModelMetrics(
        vgs=0.50,             # delta 0.0 < tau ⇒ reason 1
        hack_risk=0.30,       # +0.20 > eps_h ⇒ reason 2
        calibration=0.50,     # dropped 0.40 > eps_c ⇒ reason 3
        ood=0.50,             # dropped 0.20 > eps_o ⇒ reason 4
        cost=10.0,            # +9.0 > eps_k ⇒ reason 5
        latency=10.0,         # +9.0 > eps_l ⇒ reason 6
        regression=True,      # ⇒ reason 7
    )
    d = accept_update(_default_tols(), old, new)
    assert not d.accepted
    assert d.reasons == (
        REASON_VGS_GAIN_BELOW_TAU,
        REASON_HACK_RISK_EXCEEDED,
        REASON_CALIBRATION_DROPPED,
        REASON_OOD_DROPPED,
        REASON_COST_EXCEEDED,
        REASON_LATENCY_EXCEEDED,
        REASON_REGRESSION_FLAG_SET,
    )


# =====================================================================
# Tolerances validation (mirrors hτ ... hL nonnegativity proofs)
# =====================================================================
def test_tolerances_reject_negative():
    with pytest.raises(ValueError):
        Tolerances(tau=-0.1)
    with pytest.raises(ValueError):
        Tolerances(eps_h=-0.01)
    with pytest.raises(ValueError):
        Tolerances(eps_l=-0.0001)
