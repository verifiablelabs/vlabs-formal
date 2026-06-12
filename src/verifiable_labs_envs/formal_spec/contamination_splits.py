"""Contamination split policy — mirrors ``ContaminationSplits.lean``.

Module **A** of the contamination-resistant evaluation track. The split
taxonomy (``Split``) and the runtime policy (``validate_split_policy``,
``is_trainable``) already ship in the public SDK at
``verifiable_labs_envs.schemas.splits``. This formal_spec module re-exposes
them next to the other property-tested mirrors so the Lean cross-reference is
discoverable from one place — it does **not** duplicate the logic.

The policy invariants are machine-verified in Lean 4 (namespace
``Verifiable.ContaminationSplits``); the Python contract is property-tested
against them. The relevant theorems are:

* ``hidden_eval_not_trainable`` — a HiddenEval scenario is never trainable.
* ``hidden_eval_not_public_release`` — a HiddenEval scenario is never public.
* ``public_release_not_hidden`` — a public-release scenario is not HiddenEval.
"""

from __future__ import annotations

from verifiable_labs_envs.schemas.splits import (
    Split,
    SplitPolicyError,
    is_trainable,
    validate_split_policy,
)

__all__ = [
    "Split",
    "SplitPolicyError",
    "is_trainable",
    "validate_split_policy",
]
