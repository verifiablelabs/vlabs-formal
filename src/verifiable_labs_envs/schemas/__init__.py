"""SDK-safe shared schemas (subset).

Ships only :mod:`.splits` — the contamination split taxonomy + policy that
``formal_spec.contamination_splits`` re-exports. The canonical, full
``schemas`` package (contract, results, assurance card) lives in the public
SDK (``vlabs-sdk``) until the split flips.
"""

from __future__ import annotations

from .splits import Split, SplitPolicyError, is_trainable, validate_split_policy

__all__ = [
    "Split",
    "SplitPolicyError",
    "is_trainable",
    "validate_split_policy",
]
