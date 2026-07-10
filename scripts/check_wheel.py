"""Fail if a wheel omits canonical assets or collides with the SDK namespace."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path


def main(path: str) -> int:
    wheel = Path(path)
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    required = {
        "vlabs_formal/__init__.py",
        "vlabs_formal/formal_spec/__init__.py",
        "vlabs_formal/schemas/__init__.py",
        "vlabs_formal/lean/lakefile.toml",
        "vlabs_formal/lean/lake-manifest.json",
        "vlabs_formal/lean/lean-toolchain",
    }
    missing = sorted(required - names)
    namespace_collisions = sorted(
        name for name in names if name.startswith("verifiable_labs_envs/")
    )
    lean_files = [name for name in names if name.endswith(".lean")]
    if (
        missing
        or namespace_collisions
        or len(lean_files) != 16
        or any("/.lake/" in name for name in names)
    ):
        print(
            f"invalid wheel: missing={missing}, collisions={namespace_collisions}, "
            f"lean_files={len(lean_files)}, "
            f"vendored_lake={any('/.lake/' in name for name in names)}",
            file=sys.stderr,
        )
        return 1
    print(
        f"OK: {wheel.name} contains only the vlabs_formal namespace "
        "and 16 Lean modules"
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_wheel.py DIST.whl")
    raise SystemExit(main(sys.argv[1]))
