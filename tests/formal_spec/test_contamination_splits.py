"""Property-based parity tests for ``formal_spec.contamination_splits``.

Mirrors ``formal/VerifiableLabsFormal/ContaminationSplits.lean`` (module A):
``hidden_eval_not_trainable``, ``hidden_eval_not_public_release``,
``public_release_not_hidden`` (plus the split-disjointness lemmas).
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from verifiable_labs_envs.formal_spec.contamination_splits import (
    Split,
    SplitPolicyError,
    is_trainable,
    validate_split_policy,
)

splits = st.sampled_from(list(Split))
flags = st.booleans()


# --- A.1 hidden_eval_not_trainable ---
@given(flags)
def test_hidden_eval_not_trainable(train_allowed):
    # is_trainable forces False for HiddenEval regardless of the flag.
    assert is_trainable(Split.HIDDEN_EVAL, train_allowed) is False


@given(flags)
def test_hidden_eval_train_allowed_rejected_by_policy(public_release_allowed):
    with pytest.raises(SplitPolicyError):
        validate_split_policy(
            Split.HIDDEN_EVAL,
            train_allowed=True,
            public_release_allowed=public_release_allowed,
        )


# --- A.2 hidden_eval_not_public_release ---
def test_hidden_eval_not_public_release():
    with pytest.raises(SplitPolicyError):
        validate_split_policy(
            Split.HIDDEN_EVAL, train_allowed=False, public_release_allowed=True
        )


# --- A.3 public_release_not_hidden ---
@given(splits)
def test_public_release_not_hidden(split):
    # If a split validates with public_release=True, it cannot be HIDDEN_EVAL.
    try:
        validate_split_policy(
            split, train_allowed=False, public_release_allowed=True
        )
    except SplitPolicyError:
        return  # policy rejected this combination; nothing to assert
    assert split is not Split.HIDDEN_EVAL


# --- trainable taxonomy: only non-hidden splits with the flag are trainable ---
@given(splits, flags)
def test_is_trainable_matches_taxonomy(split, train_allowed):
    expected = (split is not Split.HIDDEN_EVAL) and train_allowed
    assert is_trainable(split, train_allowed) == expected


# --- a valid hidden-eval policy (not trainable, not public) is accepted ---
def test_valid_hidden_eval_policy_accepted():
    # Should not raise.
    validate_split_policy(
        Split.HIDDEN_EVAL, train_allowed=False, public_release_allowed=False
    )


def test_raw_hidden_eval_string_cannot_bypass_enum_identity_checks():
    with pytest.raises(TypeError, match="split must be a Split"):
        is_trainable("hidden_eval", True)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="split must be a Split"):
        validate_split_policy(  # type: ignore[arg-type]
            "hidden_eval", train_allowed=True, public_release_allowed=True
        )


@pytest.mark.parametrize("flag", [0, 1, "false", None])
def test_policy_flags_require_exact_booleans(flag):
    with pytest.raises(TypeError, match="train_allowed must be a bool"):
        is_trainable(Split.TRAIN, flag)
    with pytest.raises(TypeError, match="train_allowed must be a bool"):
        validate_split_policy(
            Split.TRAIN, train_allowed=flag, public_release_allowed=False
        )
    with pytest.raises(TypeError, match="public_release_allowed must be a bool"):
        validate_split_policy(
            Split.TRAIN, train_allowed=False, public_release_allowed=flag
        )
