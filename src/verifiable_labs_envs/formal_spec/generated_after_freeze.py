"""Generated-after-freeze leakage helper — mirrors ``GeneratedAfterFreeze.lean``.

Module **B** of the contamination-resistant evaluation track. A checkpoint
(``Model``) is described by two timestamps — its training cutoff and its freeze
time — and an evaluation scenario (``EvalScenario``) by its generation
timestamp. The Lean theorem ``generated_after_freeze_not_in_training`` proves
that, *under the single explicit assumption that a model's training data only
contains scenarios generated at or before its training cutoff*, a scenario
generated strictly after the checkpoint's freeze time (with
``training_cutoff ≤ freeze_time``) cannot be in that checkpoint's training data.

This is an **honest per-checkpoint conditional** statement, NOT a global
contamination guarantee: it reduces leakage for one checkpoint given the stated
membership assumption; it does not claim contamination is eliminated. The
``in_training_data`` flag passed to the helper is exactly the (caller-supplied)
membership fact the Lean ``InTrainingData`` predicate abstracts over.

Cross-reference (namespace ``Verifiable.GeneratedAfterFreeze``):

* ``generated_after_freeze_not_in_training`` — the core conditional lemma.
* ``post_freeze_hidden_eval_clean_for_model`` — a post-freeze hidden eval is
  clean for that checkpoint.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def _check_finite(name: str, x: float) -> None:
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite, got {x!r}")


@dataclass(frozen=True)
class Model:
    """A frozen checkpoint, described by two timestamps.

    Mirrors the Lean ``structure Model``.

    * ``training_cutoff`` — latest timestamp present in the training data.
    * ``freeze_time`` — the checkpoint freeze time.

    Both must be finite.
    """

    training_cutoff: float
    freeze_time: float

    def __post_init__(self) -> None:
        _check_finite("training_cutoff", self.training_cutoff)
        _check_finite("freeze_time", self.freeze_time)


@dataclass(frozen=True)
class EvalScenario:
    """An evaluation scenario, described by its generation timestamp.

    Mirrors the Lean ``structure EvalScenario``. ``generated_at`` must be
    finite.
    """

    generated_at: float

    def __post_init__(self) -> None:
        _check_finite("generated_at", self.generated_at)


def generated_after_freeze_not_in_training(
    model: Model, scenario: EvalScenario, in_training_data: bool
) -> bool:
    """Per-checkpoint conditional cleanliness check.

    Mirrors ``Verifiable.GeneratedAfterFreeze.generated_after_freeze_not_in_training``.
    Returns ``True`` when the scenario is *clean* for this checkpoint, i.e. not
    in its training data.

    The Lean theorem proves that *if* training data only contains scenarios
    generated at or before the training cutoff, *then*
    ``generated_at > freeze_time`` together with
    ``training_cutoff ≤ freeze_time`` forces ``¬ in_training_data``. This helper
    reflects that exactly:

    * When the freeze hypotheses hold (``generated_at > freeze_time`` and
      ``training_cutoff ≤ freeze_time``), the scenario is clean — the theorem
      guarantees ``in_training_data`` is ``False`` under the membership
      assumption, so this returns ``True``.
    * Otherwise the conditional gives no guarantee, so cleanliness is reported
      directly as ``not in_training_data`` (the honest, caller-supplied fact).

    Args:
        model: the checkpoint under consideration.
        scenario: the evaluation scenario.
        in_training_data: the caller-supplied membership fact (mirrors the
            abstract Lean ``InTrainingData`` predicate).

    Returns:
        ``True`` iff the scenario is clean (not in training data) for this
        checkpoint.
    """
    freeze_hypotheses_hold = (
        scenario.generated_at > model.freeze_time
        and model.training_cutoff <= model.freeze_time
    )
    if freeze_hypotheses_hold:
        # Lean ``generated_after_freeze_not_in_training``: under the membership
        # assumption this scenario is provably not in training data.
        return True
    return not in_training_data


__all__ = [
    "Model",
    "EvalScenario",
    "generated_after_freeze_not_in_training",
]
