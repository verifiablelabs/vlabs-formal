"""Contamination split taxonomy + policy (SDK-safe mirror of the Lean track).

Mirrors ``formal/VerifiableLabsFormal/ContaminationSplits.lean``. The Lean
side machine-verifies the three policy invariants; this is the public Python
contract the platform enforces at runtime. Kept dependency-free so it imports
without the formal_spec mirror.
"""

from __future__ import annotations

from enum import StrEnum


class Split(StrEnum):
    """Where a generated scenario may be used.

    * ``TRAIN`` — usable for optimization, never for the hidden gate.
    * ``VALIDATION`` — threshold tuning, not the final hidden gate.
    * ``HIDDEN_EVAL`` — serious hidden scoring; never trainable, never public.
    * ``PUBLIC_DEMO`` — may be public; never used for serious hidden scoring.
    """

    TRAIN = "train"
    VALIDATION = "validation"
    HIDDEN_EVAL = "hidden_eval"
    PUBLIC_DEMO = "public_demo"


class SplitPolicyError(ValueError):
    """Raised when a (split, train_allowed, public_release) tuple violates the
    machine-verified contamination policy."""


def is_trainable(split: Split, train_allowed: bool) -> bool:
    """A split is trainable only if it is not a hidden eval AND the flag set."""
    if split is Split.HIDDEN_EVAL:
        return False
    return train_allowed


def validate_split_policy(
    split: Split, *, train_allowed: bool, public_release_allowed: bool
) -> None:
    """Enforce the three invariants proved in ContaminationSplits.lean.

    * ``hidden_eval_not_trainable`` — HiddenEval can never be trainable.
    * ``hidden_eval_not_public_release`` — HiddenEval can never be public.
    * ``public_release_not_hidden`` — a public-release item is not a hidden
      eval (enforced by construction here: HiddenEval + public is rejected).

    Raises :class:`SplitPolicyError` on any violation.
    """
    if split is Split.HIDDEN_EVAL and train_allowed:
        raise SplitPolicyError("hidden_eval cannot be trainable")
    if split is Split.HIDDEN_EVAL and public_release_allowed:
        raise SplitPolicyError("hidden_eval cannot be public_release")
    if split is Split.PUBLIC_DEMO and not public_release_allowed:
        # PublicDemo that forbids public release is contradictory config.
        raise SplitPolicyError("public_demo must allow public_release")
