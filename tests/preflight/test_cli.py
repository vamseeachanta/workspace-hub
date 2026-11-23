from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_fixture_writes_artifacts_and_defaults_to_json(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "scripts.preflight.hermes_preflight",
            "--target",
            "ace-linux-2",
            "--fixture",
            str(FIXTURES / "reachable.txt"),
            "--artifacts-dir",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "1"
    assert payload["summary"]["machine_ready"] is True
    assert list(tmp_path.glob("*.json"))
    assert list(tmp_path.glob("*.md"))


def test_cli_strict_returns_one_for_warnings(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "scripts.preflight.hermes_preflight",
            "--target",
            "ace-linux-2",
            "--fixture",
            str(FIXTURES / "auth-invalid.txt"),
            "--artifacts-dir",
            str(tmp_path),
            "--strict",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "gho_" not in result.stdout
