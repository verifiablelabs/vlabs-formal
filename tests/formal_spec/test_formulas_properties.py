"""Property-based parity tests for ``formal_spec.formulas``.

Each test asserts a property proved (or trivially implied) in
``formal/VerifiableLabsFormal/CalibratedReward.lean``,
``VGS.lean``, and ``ModelRouting.lean``. The Lean theorem name(s)
mirrored by each test are recorded in the docstring.
"""

from __future__ import annotations

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from verifiable_labs_envs.formal_spec.formulas import (
    calibrated_reward,
    routing_utility,
    select_model,
    vgs,
)

# ---------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------
unit_floats = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
nonneg_floats = st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)
positive_floats = st.floats(min_value=1e-6, max_value=10.0, allow_nan=False, allow_infinity=False)
TOL = 1e-9


# =====================================================================
# CalibratedReward.lean
# =====================================================================
@given(v=unit_floats, c=unit_floats, h=unit_floats, lam=nonneg_floats)
def test_calibrated_reward_bounded(v, c, h, lam):
    """Mirrors ``calibratedReward_bounded`` (R* ∈ [−λ, 1])."""
    r = calibrated_reward(v, c, h, lam)
    assert r >= -lam - TOL
    assert r <= 1.0 + TOL


@given(v1=unit_floats, v2=unit_floats, c=unit_floats, h=unit_floats, lam=nonneg_floats)
def test_calibrated_reward_mono_V(v1, v2, c, h, lam):
    """Mirrors ``calibratedReward_mono_V`` (V₁ ≤ V₂ ⇒ R*(V₁) ≤ R*(V₂))."""
    assume(v1 <= v2)
    assert calibrated_reward(v1, c, h, lam) <= calibrated_reward(v2, c, h, lam) + TOL


@given(v=unit_floats, c1=unit_floats, c2=unit_floats, h=unit_floats, lam=nonneg_floats)
def test_calibrated_reward_mono_C(v, c1, c2, h, lam):
    """Mirrors ``calibratedReward_mono_C`` (C₁ ≤ C₂ ⇒ R*(C₁) ≤ R*(C₂) when V ≥ 0)."""
    assume(c1 <= c2)
    assert calibrated_reward(v, c1, h, lam) <= calibrated_reward(v, c2, h, lam) + TOL


@given(v=unit_floats, c=unit_floats, h1=unit_floats, h2=unit_floats, lam=nonneg_floats)
def test_calibrated_reward_anti_H(v, c, h1, h2, lam):
    """Mirrors ``calibratedReward_anti_H`` (H₁ ≤ H₂ ⇒ R*(H₂) ≤ R*(H₁) when λ ≥ 0)."""
    assume(h1 <= h2)
    assert calibrated_reward(v, c, h2, lam) <= calibrated_reward(v, c, h1, lam) + TOL


@given(v=unit_floats, c=unit_floats, h1=unit_floats, h2=unit_floats,
       lam=st.floats(min_value=1e-4, max_value=10.0, allow_nan=False, allow_infinity=False))
def test_calibrated_reward_strict_anti_H(v, c, h1, h2, lam):
    """Mirrors ``calibratedReward_strict_anti_H`` (λ > 0 ∧ H₁ < H₂ ⇒ R*(H₂) < R*(H₁))."""
    assume(h2 - h1 > 1e-3)
    r1 = calibrated_reward(v, c, h1, lam)
    r2 = calibrated_reward(v, c, h2, lam)
    assert r2 < r1


@pytest.mark.parametrize(
    "bad_input",
    [
        (-0.1, 0.5, 0.5, 0.5),  # v < 0
        (1.1, 0.5, 0.5, 0.5),   # v > 1
        (0.5, -0.1, 0.5, 0.5),  # c < 0
        (0.5, 0.5, 1.1, 0.5),   # h > 1
        (0.5, 0.5, 0.5, -0.1),  # lam < 0
        (float("inf"), 0.5, 0.5, 0.5),  # v not finite
    ],
)
def test_calibrated_reward_domain_errors(bad_input):
    """Domain hypotheses (Lean theorem preconditions) are enforced, not clamped."""
    with pytest.raises(ValueError):
        calibrated_reward(*bad_input)


# =====================================================================
# VGS.lean
# =====================================================================
@given(
    g=unit_floats, c=unit_floats, r=unit_floats, d=unit_floats,
    h=unit_floats, k=unit_floats, lat=unit_floats,
    lam=nonneg_floats, mu=nonneg_floats, nu=nonneg_floats,
)
def test_vgs_bounded(g, c, r, d, h, k, lat, lam, mu, nu):
    """Mirrors ``VGS_bounded`` (VGS ∈ [−(λ+μ+ν), 1])."""
    score = vgs(g, c, r, d, h, k, lat, lam, mu, nu)
    assert score >= -(lam + mu + nu) - TOL
    assert score <= 1.0 + TOL


@given(
    g1=unit_floats, g2=unit_floats,
    c=unit_floats, r=unit_floats, d=unit_floats,
    h=unit_floats, k=unit_floats, lat=unit_floats,
    lam=nonneg_floats, mu=nonneg_floats, nu=nonneg_floats,
)
def test_vgs_mono_G(g1, g2, c, r, d, h, k, lat, lam, mu, nu):
    """Mirrors ``VGS_mono_G``."""
    assume(g1 <= g2)
    a = vgs(g1, c, r, d, h, k, lat, lam, mu, nu)
    b = vgs(g2, c, r, d, h, k, lat, lam, mu, nu)
    assert a <= b + TOL


@given(
    g=unit_floats, c=unit_floats, r=unit_floats, d=unit_floats,
    h1=unit_floats, h2=unit_floats, k=unit_floats, lat=unit_floats,
    lam=nonneg_floats, mu=nonneg_floats, nu=nonneg_floats,
)
def test_vgs_anti_H(g, c, r, d, h1, h2, k, lat, lam, mu, nu):
    """Mirrors ``VGS_anti_H``."""
    assume(h1 <= h2)
    assert vgs(g, c, r, d, h2, k, lat, lam, mu, nu) <= vgs(g, c, r, d, h1, k, lat, lam, mu, nu) + TOL


@given(
    g1=st.floats(min_value=0.0, max_value=0.95, allow_nan=False, allow_infinity=False),
    g2=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    c=st.floats(min_value=0.05, max_value=1.0, allow_nan=False, allow_infinity=False),
    r=st.floats(min_value=0.05, max_value=1.0, allow_nan=False, allow_infinity=False),
    d=st.floats(min_value=0.05, max_value=1.0, allow_nan=False, allow_infinity=False),
    h=unit_floats, k=unit_floats, lat=unit_floats,
    lam=nonneg_floats, mu=nonneg_floats, nu=nonneg_floats,
)
def test_vgs_strict_mono_G(g1, g2, c, r, d, h, k, lat, lam, mu, nu):
    """Mirrors ``VGS_strict_mono_G`` (C,R,D > 0 ∧ G₁ < G₂ ⇒ VGS(G₁) < VGS(G₂))."""
    assume(g2 - g1 > 1e-3)
    a = vgs(g1, c, r, d, h, k, lat, lam, mu, nu)
    b = vgs(g2, c, r, d, h, k, lat, lam, mu, nu)
    assert a < b


def test_vgs_domain_errors():
    """Out-of-range inputs raise ValueError."""
    with pytest.raises(ValueError):
        vgs(-0.1, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.1, 0.1, 0.1)
    with pytest.raises(ValueError):
        vgs(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -0.1, 0.1, 0.1)


# =====================================================================
# ModelRouting.lean
# =====================================================================
@given(
    q=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    cost1=nonneg_floats, cost2=nonneg_floats,
    latency=nonneg_floats, risk=nonneg_floats,
    gamma=nonneg_floats, delta=nonneg_floats, rho=nonneg_floats,
)
def test_routing_utility_anti_cost(q, cost1, cost2, latency, risk, gamma, delta, rho):
    """Lower cost ⇒ higher utility (proved inside ``cheaper_model_preferred``)."""
    assume(cost1 <= cost2)
    u1 = routing_utility(q, cost1, latency, risk, gamma, delta, rho)
    u2 = routing_utility(q, cost2, latency, risk, gamma, delta, rho)
    assert u2 <= u1 + TOL


@given(
    q=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    cost=nonneg_floats,
    latency=nonneg_floats, risk1=nonneg_floats, risk2=nonneg_floats,
    gamma=nonneg_floats, delta=nonneg_floats, rho=nonneg_floats,
)
def test_routing_utility_anti_risk(q, cost, latency, risk1, risk2, gamma, delta, rho):
    """Lower risk ⇒ higher utility (consistent with ``routingUtility`` definition)."""
    assume(risk1 <= risk2)
    u1 = routing_utility(q, cost, latency, risk1, gamma, delta, rho)
    u2 = routing_utility(q, cost, latency, risk2, gamma, delta, rho)
    assert u2 <= u1 + TOL


def test_select_model_returns_argmax():
    """Smoke test mirroring ``selected_model_optimal``."""
    candidates = [("a", 0.3), ("b", 0.9), ("c", 0.5)]
    assert select_model(candidates) == "b"


def test_select_model_lex_tie_break():
    """Ties broken by lex-min id (matches ``Finset.min'`` style)."""
    candidates = [("z", 0.5), ("b", 0.5), ("aaa", 0.5)]
    assert select_model(candidates) == "aaa"


def test_select_model_empty_raises():
    """Lean ``selectedModel`` requires ``models.Nonempty``."""
    with pytest.raises(ValueError):
        select_model([])


def test_select_model_duplicate_id_raises():
    """Mirrors the Lean ``Finset`` non-duplication invariant."""
    with pytest.raises(ValueError):
        select_model([("a", 0.5), ("a", 0.7)])
