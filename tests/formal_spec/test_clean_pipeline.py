"""Property-based parity tests for ``formal_spec.clean_pipeline``.

Mirrors ``formal/VerifiableLabsFormal/CleanPipeline.lean`` (module G):
``clean_pipeline_acceptance_sound`` — gate acceptance entails ALL the
contamination-adjusted guarantees simultaneously, not public-score improvement
alone.
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from verifiable_labs_envs.formal_spec.clean_pipeline import (
    clean_pipeline_acceptance,
)
from verifiable_labs_envs.formal_spec.clean_promotion_gate import (
    CleanMetrics,
    CleanTolerances,
)

unit = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
signed = st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False)
nonneg = st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)


def _metrics(**overrides) -> CleanMetrics:
    base = dict(
        raw_vgs=0.5, dcr=0.1, clean_vgs=0.5, public_score=0.8, hidden_score=0.7,
        ood_score=0.7, hack_risk=0.1, calibration=0.9, cost=1.0, latency=1.0,
        regression=False,
    )
    base.update(overrides)
    return CleanMetrics(**base)


@st.composite
def clean_metrics(draw) -> CleanMetrics:
    return CleanMetrics(
        raw_vgs=draw(unit), dcr=draw(unit), clean_vgs=draw(signed),
        public_score=draw(unit), hidden_score=draw(unit), ood_score=draw(signed),
        hack_risk=draw(signed), calibration=draw(signed), cost=draw(nonneg),
        latency=draw(nonneg), regression=draw(st.booleans()),
    )


@st.composite
def tolerances(draw) -> CleanTolerances:
    return CleanTolerances(
        tau=draw(nonneg), eps_h=draw(nonneg), eps_c=draw(nonneg),
        eps_o=draw(nonneg), eps_d=draw(nonneg), eps_k=draw(nonneg),
        eps_l=draw(nonneg),
    )


# --- G: acceptance ⇔ all composed guarantees hold ---
@given(clean_metrics(), clean_metrics(), tolerances())
def test_acceptance_entails_all_guarantees(old, new, tol):
    decision, guarantees = clean_pipeline_acceptance(tol, old, new)
    assert guarantees.all_hold() == decision.accepted


@given(clean_metrics(), clean_metrics(), tolerances())
def test_accept_implies_every_individual_guarantee(old, new, tol):
    decision, g = clean_pipeline_acceptance(tol, old, new)
    if decision.accepted:
        assert g.clean_vgs_improved
        assert g.hack_risk_bounded
        assert g.dcr_bounded
        assert g.ood_not_regressed
        assert g.calibration_not_regressed
        assert g.cost_bounded
        assert g.latency_bounded
        assert g.no_regression


def test_public_improvement_alone_does_not_imply_acceptance():
    # The candidate improves public_score dramatically but does NOT improve
    # clean_vgs — acceptance must still fail. This is the headline G claim.
    tol = CleanTolerances()
    old = _metrics(public_score=0.5, clean_vgs=0.5)
    new = _metrics(public_score=0.99, clean_vgs=0.5)  # no clean_vgs gain
    decision, guarantees = clean_pipeline_acceptance(tol, old, new)
    assert decision.accepted is False
    assert guarantees.all_hold() is False
    assert guarantees.clean_vgs_improved is False


def test_happy_path_all_guarantees_hold():
    tol = CleanTolerances()
    old = _metrics()
    new = _metrics(clean_vgs=0.6)
    decision, guarantees = clean_pipeline_acceptance(tol, old, new)
    assert decision.accepted is True
    assert guarantees.all_hold() is True
