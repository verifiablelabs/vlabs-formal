"""Property-based parity tests for ``formal_spec.generated_after_freeze``.

Mirrors ``formal/VerifiableLabsFormal/GeneratedAfterFreeze.lean`` (module B):
``generated_after_freeze_not_in_training``,
``post_freeze_hidden_eval_clean_for_model``.

These are honest *per-checkpoint conditional* statements, not global
contamination guarantees.
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from verifiable_labs_envs.formal_spec.generated_after_freeze import (
    EvalScenario,
    Model,
    generated_after_freeze_not_in_training,
)

times = st.floats(min_value=0.0, max_value=1e6, allow_nan=False, allow_infinity=False)


# --- B.1 generated_after_freeze_not_in_training ---
# Under the Lean hypotheses (generated_at > freeze and cutoff <= freeze), the
# scenario is clean. We model the explicit membership predicate: a scenario can
# only truthfully be "in training data" when generated_at <= training_cutoff.
@given(times, times, times)
def test_generated_after_freeze_is_clean_under_explicit_cutoff(
    cutoff, freeze, gen
):
    model = Model(training_cutoff=cutoff, freeze_time=freeze)
    scenario = EvalScenario(generated_at=gen)
    # Honest membership fact consistent with the Lean hContains assumption.
    in_training = gen <= cutoff
    if gen > freeze and cutoff <= freeze:
        # Lean theorem: provably clean (not in training data).
        assert generated_after_freeze_not_in_training(
            model, scenario, in_training
        ) is True
        # And the consistent membership fact agrees: it cannot be in training.
        assert in_training is False


# --- B.1 explicit happy path: clearly post-freeze with cutoff at freeze ---
def test_post_freeze_scenario_clean_explicit():
    model = Model(training_cutoff=100.0, freeze_time=100.0)
    scenario = EvalScenario(generated_at=150.0)
    assert generated_after_freeze_not_in_training(model, scenario, True) is True


# --- B.2 post_freeze_hidden_eval_clean_for_model: outside the hypotheses the
# helper honestly reports the caller-supplied membership fact ---
@given(st.booleans())
def test_helper_reports_membership_when_hypotheses_fail(in_training):
    # cutoff > freeze breaks the freeze hypothesis -> no guarantee; the helper
    # falls back to `not in_training_data`.
    model = Model(training_cutoff=200.0, freeze_time=100.0)
    scenario = EvalScenario(generated_at=150.0)  # > freeze but cutoff > freeze
    assert generated_after_freeze_not_in_training(
        model, scenario, in_training
    ) == (not in_training)


def test_pre_freeze_scenario_not_guaranteed_clean():
    # generated_at <= freeze: hypothesis fails, helper reflects membership.
    model = Model(training_cutoff=50.0, freeze_time=100.0)
    scenario = EvalScenario(generated_at=80.0)
    assert generated_after_freeze_not_in_training(model, scenario, True) is False
    assert generated_after_freeze_not_in_training(model, scenario, False) is True
