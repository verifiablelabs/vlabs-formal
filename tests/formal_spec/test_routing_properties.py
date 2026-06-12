"""Property-based parity tests for ``formal_spec.formulas.select_model`` and
``routing_utility``.

Mirrors theorems in ``formal/VerifiableLabsFormal/ModelRouting.lean``:
``selected_model_optimal``, ``cheaper_model_preferred``,
``near_optimal_under_error``.
"""

from __future__ import annotations

from hypothesis import assume, given
from hypothesis import strategies as st

from verifiable_labs_envs.formal_spec.formulas import (
    routing_utility,
    select_model,
)

TOL = 1e-9


# ---------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------
@st.composite
def panel_of_models(draw, min_n=2, max_n=8):
    """Produce a list of (id, true_utility) for a synthetic routing panel."""
    n = draw(st.integers(min_value=min_n, max_value=max_n))
    ids = [f"m_{i:02d}" for i in range(n)]
    utilities = draw(
        st.lists(
            st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False),
            min_size=n,
            max_size=n,
        )
    )
    return list(zip(ids, utilities, strict=True))


# =====================================================================
# selected_model_optimal
# =====================================================================
@given(panel=panel_of_models())
def test_routing_argmax_is_optimal(panel):
    """Mirrors ``selected_model_optimal``: select_model achieves the max."""
    sel = select_model(panel)
    sel_u = next(u for cid, u in panel if cid == sel)
    for _cid, u in panel:
        assert u <= sel_u + TOL


# =====================================================================
# cheaper_model_preferred  (γ > 0, equal quality / latency / risk)
# =====================================================================
@given(
    q=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    latency=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    risk=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    cost_a=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    cost_b=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    gamma=st.floats(min_value=1e-3, max_value=10.0, allow_nan=False, allow_infinity=False),
    delta=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    rho=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
)
def test_routing_cheaper_model_preferred(q, latency, risk, cost_a, cost_b, gamma, delta, rho):
    """Mirrors ``cheaper_model_preferred``: γ > 0 ∧ cost_a < cost_b ⇒
    select_model prefers the cheaper one when q, latency, risk equal."""
    assume(cost_b - cost_a > 1e-3)
    u_a = routing_utility(q, cost_a, latency, risk, gamma, delta, rho)
    u_b = routing_utility(q, cost_b, latency, risk, gamma, delta, rho)
    assert u_a > u_b
    sel = select_model([("a", u_a), ("b", u_b)])
    assert sel == "a"


# =====================================================================
# near_optimal_under_error  (2ε bound on regret)
# =====================================================================
@given(
    panel=panel_of_models(min_n=2, max_n=6),
    eps=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    noise=st.data(),
)
def test_routing_2eps_near_optimal_under_eps_bounded_error(panel, eps, noise):
    """Mirrors ``near_optimal_under_error``:

    If estimated utility is within ε of the true utility for every model,
    the model selected on estimates is at most 2ε worse than the true
    optimum.
    """
    perturbed: list[tuple[str, float]] = []
    for cid, u in panel:
        delta = noise.draw(
            st.floats(
                min_value=-eps,
                max_value=eps,
                allow_nan=False,
                allow_infinity=False,
            )
        )
        perturbed.append((cid, u + delta))

    sel = select_model(perturbed)
    true_u_sel = next(u for cid, u in panel if cid == sel)
    true_best = max(u for _, u in panel)
    regret = true_best - true_u_sel
    # The Lean bound is 2ε; we allow a tiny float-arithmetic slack.
    assert regret <= 2 * eps + 1e-9


@given(panel=panel_of_models())
def test_routing_lex_tie_break_is_deterministic(panel):
    """Permuting the input order must not change the selected model."""
    sel_original = select_model(panel)
    reversed_panel = list(reversed(panel))
    sel_reversed = select_model(reversed_panel)
    assert sel_original == sel_reversed
