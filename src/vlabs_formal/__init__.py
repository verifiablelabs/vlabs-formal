"""Canonical package surface for the Verifiable Labs formal track."""
from __future__ import annotations

from pathlib import Path


__version__ = "0.0.1"


def formal_root() -> Path:
    """Return the directory containing ``lakefile.toml`` and the Lean modules.

    Wheels bundle the development under ``vlabs_formal/lean``. A source
    checkout falls back to the repository's top-level ``formal/`` directory.
    """
    packaged = Path(__file__).resolve().with_name("lean")
    if packaged.is_dir():
        return packaged
    checkout = Path(__file__).resolve().parents[2] / "formal"
    if checkout.is_dir():
        return checkout
    raise FileNotFoundError("vlabs-formal Lean assets are missing from this installation")


__all__ = ["__version__", "formal_root"]
