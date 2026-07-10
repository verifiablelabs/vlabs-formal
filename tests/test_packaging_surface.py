from __future__ import annotations

from pathlib import Path
import tomllib

import vlabs_formal


def test_distribution_has_canonical_import_and_formal_assets() -> None:
    root = Path(vlabs_formal.formal_root())
    assert root.joinpath("lakefile.toml").is_file()
    assert root.joinpath("lean-toolchain").is_file()
    lean_files = sorted(root.joinpath("VerifiableLabsFormal").glob("*.lean"))
    assert len(lean_files) == 16
    assert all("sorry" not in path.read_text(encoding="utf-8") for path in lean_files)
    assert vlabs_formal.__version__ == "0.0.1"


def test_wheel_configuration_never_publishes_the_sdk_namespace() -> None:
    project_root = Path(__file__).resolve().parents[1]
    config = tomllib.loads(project_root.joinpath("pyproject.toml").read_text())
    wheel = config["tool"]["hatch"]["build"]["targets"]["wheel"]
    assert wheel["packages"] == ["src/vlabs_formal"]
    assert all(
        not target.startswith("verifiable_labs_envs")
        for target in wheel.get("force-include", {}).values()
    )
