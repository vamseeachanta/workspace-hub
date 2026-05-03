from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "portability" / "verify-engineering-baselines.sh"
GUIDE_DOC = REPO_ROOT / "docs" / "engineering" / "portability" / "smoke-verification-guide.md"


def _fake_validator(path: Path, *, tool: str, status: str = "PASS", version: str = "1.0") -> Path:
    path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "verdict=''\n"
        "while [[ $# -gt 0 ]]; do\n"
        "  case \"$1\" in --verdict) verdict=\"$2\"; shift 2 ;; *) shift ;; esac\n"
        "done\n"
        "mkdir -p \"$(dirname \"$verdict\")\"\n"
        f"cat > \"$verdict\" <<'YAML'\n"
        f"tool: {tool}\n"
        f"overall_verdict: {status}\n"
        f"version: {version}\n"
        f"error_summary: {'simulated-failure' if status == 'FAIL' else ''}\n"
        "YAML\n"
        f"exit {0 if status == 'PASS' else 1}\n"
    )
    path.chmod(0o755)
    return path


def _run_verify(*args: str, env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        ["bash", str(VERIFY_SCRIPT), *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_unified_runner_passes_when_openfoam_and_blender_validators_pass(tmp_path: Path) -> None:
    openfoam = _fake_validator(tmp_path / "openfoam.sh", tool="openfoam", version="v2312")
    blender = _fake_validator(tmp_path / "blender.sh", tool="blender", version="4.1.1")
    report_dir = tmp_path / "reports"

    result = _run_verify(
        "--report-dir",
        str(report_dir),
        env_overrides={"OPENFOAM_BASELINE_VALIDATOR": str(openfoam), "BLENDER_BASELINE_VALIDATOR": str(blender), "SMOKE_HOSTNAME": "dev-secondary"},
    )

    assert result.returncode == 0, result.stderr
    verdict = yaml.safe_load((report_dir / "consolidated-verdict.yaml").read_text())
    assert verdict["overall_verdict"] == "PASS"
    assert verdict["machine"] == "dev-secondary"
    assert [tool["name"] for tool in verdict["tools"]] == ["openfoam", "blender"]
    assert [tool["status"] for tool in verdict["tools"]] == ["PASS", "PASS"]
    assert "openfoam" in result.stdout
    assert "blender" in result.stdout


def test_unified_runner_propagates_single_tool_failure(tmp_path: Path) -> None:
    openfoam = _fake_validator(tmp_path / "openfoam.sh", tool="openfoam", version="v2312")
    blender = _fake_validator(tmp_path / "blender.sh", tool="blender", status="FAIL", version="4.1.1")
    report_dir = tmp_path / "reports"

    result = _run_verify(
        "--report-dir",
        str(report_dir),
        env_overrides={"OPENFOAM_BASELINE_VALIDATOR": str(openfoam), "BLENDER_BASELINE_VALIDATOR": str(blender)},
    )

    assert result.returncode == 1
    verdict = yaml.safe_load((report_dir / "consolidated-verdict.yaml").read_text())
    assert verdict["overall_verdict"] == "FAIL"
    blender_entry = next(tool for tool in verdict["tools"] if tool["name"] == "blender")
    assert blender_entry["status"] == "FAIL"
    assert blender_entry["error_summary"] == "simulated-failure"


def test_unified_runner_supports_single_tool_json_output(tmp_path: Path) -> None:
    openfoam = _fake_validator(tmp_path / "openfoam.sh", tool="openfoam", version="v2312")
    report_dir = tmp_path / "reports"

    result = _run_verify(
        "--tool",
        "openfoam",
        "--report-dir",
        str(report_dir),
        "--json",
        env_overrides={"OPENFOAM_BASELINE_VALIDATOR": str(openfoam)},
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["overall_verdict"] == "PASS"
    assert [tool["name"] for tool in payload["tools"]] == ["openfoam"]
    assert not (report_dir / "blender-verdict.yaml").exists()


def test_unified_runner_rejects_unknown_tool(tmp_path: Path) -> None:
    result = _run_verify("--tool", "paraview", "--report-dir", str(tmp_path))

    assert result.returncode == 2
    assert "unknown tool" in result.stderr.lower()


def test_smoke_verification_guide_documents_reports_and_drift_detection() -> None:
    text = GUIDE_DOC.read_text()
    assert "verify-engineering-baselines.sh" in text
    assert "consolidated-verdict.yaml" in text
    assert "OpenFOAM" in text
    assert "Blender" in text
    assert "drift" in text.lower()
