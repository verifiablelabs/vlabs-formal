"""Invariance / shortcut-detection harness — mirrors
``formal/VerifiableLabsFormal/VerifierInvariance.lean``.

The Lean theorem ``invariant_preserves_correct`` says: if a verifier
``V : X → A → Bool`` is invariant under a transformation pair
``(T_X, T_A)`` and ``V(x, a) = True``, then ``V(T_X(x), T_A(a)) = True``.
The contrapositive ``shortcut_violates_invariance`` is the basis of
this harness: any disagreement between ``V(x, a)`` and ``V(T_X(x),
T_A(a))`` is a shortcut, and the empirical *violation rate* across a
battery of transformations is our v0 estimator for the hackability
parameter ``H`` that appears in ``calibrated_reward`` and ``vgs``.

Honest disclaimer (echoed in the docstring of ``check_invariance``):
the violation-rate estimator is **only as informative as the
transformation battery supplied**. A battery that misses the
hack-relevant symmetry will under-report H. This is not a soundness
problem with the Lean theorem — it is a completeness limitation of the
harness, and the production calibration pipeline treats H accordingly.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import TypeVar

X = TypeVar("X")
A = TypeVar("A")


# A single (T_X, T_A) pair, optionally tagged with a name for the report.
Transform = tuple[Callable[[X], X], Callable[[A], A]]
NamedTransform = tuple[str, Transform]


@dataclass(frozen=True)
class TransformStats:
    """Per-transform tally for the invariance report."""

    name: str
    instances_checked: int
    flips: int

    @property
    def flip_rate(self) -> float:
        if self.instances_checked == 0:
            return 0.0
        return self.flips / self.instances_checked


@dataclass(frozen=True)
class InvarianceReport:
    """Aggregate result of one ``check_invariance`` run.

    * ``per_transform`` — ordered, one entry per supplied transform.
    * ``total_checks`` — total (instance × transform) pairs evaluated.
    * ``total_flips``  — total count of disagreements
      ``V(x, a) ≠ V(T_X(x), T_A(a))``.
    * ``violation_rate`` — ``total_flips / total_checks`` (0 if empty).
    """

    per_transform: tuple[TransformStats, ...]
    total_checks: int
    total_flips: int

    @property
    def violation_rate(self) -> float:
        if self.total_checks == 0:
            return 0.0
        return self.total_flips / self.total_checks


def check_invariance(
    verifier: Callable[[X, A], bool],
    transforms: Sequence[NamedTransform] | Mapping[str, Transform],
    instances: Iterable[tuple[X, A]],
) -> InvarianceReport:
    """Estimate empirical invariance-violation rate of ``verifier``.

    Implements the contrapositive of
    ``invariant_preserves_correct`` / ``shortcut_violates_invariance``
    from ``formal/VerifiableLabsFormal/VerifierInvariance.lean``:
    for every ``(x, a)`` with ``verifier(x, a) == True``, apply each
    ``(T_X, T_A)`` and record whether the verifier still accepts the
    transformed pair. A *flip* (``True`` → ``False``) is evidence the
    verifier relies on a feature it should be invariant to — a
    shortcut.

    Instances for which the verifier already returns ``False`` are
    silently skipped (the Lean theorem only constrains the
    accepted-input branch).

    Args:
        verifier: callable ``(x, a) → bool``.
        transforms: either a mapping ``name → (T_X, T_A)`` or a
            sequence of ``(name, (T_X, T_A))`` tuples. Ordering is
            preserved in the report.
        instances: iterable of ``(x, a)`` inputs to probe.

    Returns:
        An ``InvarianceReport`` with per-transform flip counts and the
        overall violation rate.

    .. warning::
        This is a **v0 estimator for the hackability parameter ``H``**.
        It is only as informative as the supplied transformation
        battery — a battery that omits the relevant symmetry will
        under-report shortcuts. The Lean proof is sound; this harness
        is intentionally permissive about what counts as a transform
        so that callers can plug in domain-specific batteries.
    """
    if isinstance(transforms, Mapping):
        ordered_transforms: list[NamedTransform] = list(transforms.items())  # type: ignore[arg-type]
    else:
        ordered_transforms = list(transforms)

    seen_names: set[str] = set()
    for name, _pair in ordered_transforms:
        if not isinstance(name, str) or not name:
            raise ValueError(f"transform name must be a non-empty str, got {name!r}")
        if name in seen_names:
            raise ValueError(f"duplicate transform name {name!r}")
        seen_names.add(name)

    instances_list = list(instances)

    per_transform_counts: dict[str, list[int]] = {n: [0, 0] for n, _ in ordered_transforms}
    # per_transform_counts[name] = [instances_checked, flips]

    total_checks = 0
    total_flips = 0

    for x, a in instances_list:
        if not verifier(x, a):
            # Lean theorem only constrains the V(x,a)=True branch.
            continue
        for name, (t_x, t_a) in ordered_transforms:
            x_prime = t_x(x)
            a_prime = t_a(a)
            still_accepts = verifier(x_prime, a_prime)
            per_transform_counts[name][0] += 1
            total_checks += 1
            if not still_accepts:
                per_transform_counts[name][1] += 1
                total_flips += 1

    per_transform = tuple(
        TransformStats(name=n, instances_checked=c, flips=f)
        for n, (c, f) in (
            (n, per_transform_counts[n]) for n, _ in ordered_transforms
        )
    )

    return InvarianceReport(
        per_transform=per_transform,
        total_checks=total_checks,
        total_flips=total_flips,
    )


__all__ = [
    "Transform",
    "NamedTransform",
    "TransformStats",
    "InvarianceReport",
    "check_invariance",
]
