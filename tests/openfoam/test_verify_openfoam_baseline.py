from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "openfoam" / "verify-openfoam-baseline.sh"
RUNNER_SCRIPT = REPO_ROOT / "scripts" / "openfoam" / "run-openfoam-tutorials.sh"
WORKFLOW_DOC = REPO_ROOT / "docs" / "engineering" / "portability" / "openfoam-v2312-baseline-workflow.md"
MANIFEST_DOC = REPO_ROOT / "examples" / "openfoam" / "cavity-v2312" / "README.md"
CHECKLIST_DOC = REPO_ROOT / "docs" / "engineering" / "portability" / "ENGINEERING_DELIVERY_CHECKLIST.md"
DOCS_INDEX = REPO_ROOT / "docs" / "README.md"
PYPROJECT = REPO_ROOT / "pyproject.toml"

REQUIRED_MANIFEST_HEADINGS = [
    "# OpenFOAM cavity v2312 smoke manifest",
    "## Purpose",
    "## Copy commands",
    "## Run commands",
    "## Expected artifacts",
]


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


def test_verify_script_fails_when_bashrc_missing(tmp_path: Path) -> None:
    verdict_path = tmp_path / "missing.yaml"

    result = _run_verify(
        "--verdict",
        str(verdict_path),
        env_overrides={"OPENFOAM_BASHRC_PATHS": "/missing/a:/missing/b"},
    )

    assert result.returncode != 0
    assert "ERROR: OpenFOAM bashrc not found" in result.stderr
    assert "/missing/a" in result.stderr
    assert "/missing/b" in result.stderr
    assert verdict_path.exists(), "failure verdict should still be written"

    verdict = yaml.safe_load(verdict_path.read_text())
    assert verdict["overall_verdict"] == "FAIL"
    assert verdict["error_type"] == "missing-bashrc"
    assert verdict["attempted_bashrc_paths"] == ["/missing/a", "/missing/b"]


def test_verify_script_rejects_invalid_benchmark_value(tmp_path: Path) -> None:
    verdict_path = tmp_path / "invalid-benchmark.yaml"

    result = _run_verify(
        "--benchmark",
        "badcase",
        "--verdict",
        str(verdict_path),
    )

    assert result.returncode != 0
    assert "unsupported benchmark" in result.stderr.lower()
    assert "pitzDaily" in result.stderr


def test_verify_script_surfaces_runner_failure(tmp_path: Path) -> None:
    fake_bashrc = tmp_path / "openfoam2312.sh"
    fake_bashrc.write_text("export WM_PROJECT_DIR=/fake/tutorials\nexport WM_PROJECT_VERSION=v2312\n")
    fake_runner = tmp_path / "fake-runner.sh"
    fake_runner.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "echo 'runner exploded' >&2\n"
        "exit 7\n"
    )
    fake_runner.chmod(0o755)
    verdict_path = tmp_path / "runner-fail.yaml"

    result = _run_verify(
        "--verdict",
        str(verdict_path),
        env_overrides={
            "OPENFOAM_BASHRC_PATHS": str(fake_bashrc),
            "OPENFOAM_TUTORIAL_RUNNER_PATH": str(fake_runner),
            "OPENFOAM_VERSION_COMMAND": "printf 'OpenFOAM-v2312\\n'",
            "OPENFOAM_HOSTNAME": "dev-secondary",
        },
    )

    assert result.returncode != 0
    assert "runner exploded" in result.stderr
    verdict = yaml.safe_load(verdict_path.read_text())
    assert verdict["overall_verdict"] == "FAIL"
    assert verdict["error_type"] == "runner-failure"
    assert "runner exploded" in verdict["error_message"]


def test_verify_script_normalizes_final_yaml_contract(tmp_path: Path) -> None:
    fake_bashrc = tmp_path / "openfoam2312.sh"
    fake_bashrc.write_text("export WM_PROJECT_DIR=/fake/tutorials\nexport WM_PROJECT_VERSION=v2312\n")
    raw_verdict = tmp_path / "raw.yaml"
    fake_runner = tmp_path / "fake-runner.sh"
    fake_runner.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"cat > {raw_verdict} <<'YAML'\n"
        "generated_at: 2026-04-21T00:00:00Z\n"
        "machine: dev-secondary\n"
        "openfoam_version: v2312\n"
        "overall_verdict: PASS\n"
        "tutorials:\n"
        "  - name: cavity\n"
        "    status: PASS\n"
        "    time_directories: 11\n"
        "YAML\n"
    )
    fake_runner.chmod(0o755)
    verdict_path = tmp_path / "final.yaml"

    result = _run_verify(
        "--verdict",
        str(verdict_path),
        env_overrides={
            "OPENFOAM_BASHRC_PATHS": str(fake_bashrc),
            "OPENFOAM_TUTORIAL_RUNNER_PATH": str(fake_runner),
            "OPENFOAM_VERSION_COMMAND": "printf 'OpenFOAM-v2312\\n'",
            "OPENFOAM_HOSTNAME": "dev-secondary",
            "OPENFOAM_RAW_VERDICT_PATH": str(raw_verdict),
        },
    )

    assert result.returncode == 0, result.stderr
    verdict = yaml.safe_load(verdict_path.read_text())
    assert set(verdict) == {
        "generated_at",
        "machine",
        "resolved_bashrc_path",
        "fork",
        "version",
        "verification_method",
        "overall_verdict",
        "tutorials",
    }
    assert verdict["fork"] == "ESI/OpenFOAM.com"
    assert verdict["version"] == "v2312"
    assert verdict["overall_verdict"] == "PASS"
    assert verdict["tutorials"] == [
        {"name": "cavity", "status": "PASS", "time_directories": 11}
    ]


def test_manifest_instructions_do_not_commit_case_data() -> None:
    assert MANIFEST_DOC.exists()
    text = MANIFEST_DOC.read_text()
    for heading in REQUIRED_MANIFEST_HEADINGS:
        assert heading in text
    assert not any(path.is_dir() for path in MANIFEST_DOC.parent.iterdir() if path.name != "README.md")


def test_workflow_doc_covers_traceable_issue_requirements() -> None:
    assert WORKFLOW_DOC.exists()
    text = WORKFLOW_DOC.read_text()
    for required in [
        "ESI/OpenFOAM.com v2312",
        "/usr/lib/openfoam/openfoam2312/etc/bashrc",
        "/opt/openfoam2312/etc/bashrc",
        "logs/engineering/openfoam-baseline/latest-verdict.yaml",
        "cavity",
        "pitzDaily",
        "damBreak",
        "Requirement traceability",
    ]:
        assert required in text

    checklist_text = CHECKLIST_DOC.read_text()
    assert "openfoam-v2312-baseline-workflow.md" in checklist_text

    docs_index = DOCS_INDEX.read_text()
    assert "openfoam-v2312-baseline-workflow.md" in docs_index


def test_pytest_harness_covers_validator_contract() -> None:
    assert VERIFY_SCRIPT.exists()
    assert RUNNER_SCRIPT.exists()
    assert "openfoam" in PYPROJECT.read_text()
    contents = Path(__file__).read_text()
    assert "@pytest.mark.openfoam" in contents
    assert "test_verify_script_fails_when_bashrc_missing" in contents
    assert "test_verify_script_rejects_invalid_benchmark_value" in contents


@pytest.mark.openfoam
def test_verify_script_succeeds_and_emits_schema_valid_verdict_on_real_host(tmp_path: Path) -> None:
    available_paths = [
        path for path in [
            Path("/usr/lib/openfoam/openfoam2312/etc/bashrc"),
            Path("/opt/openfoam2312/etc/bashrc"),
        ]
        if path.exists()
    ]
    if not available_paths:
        pytest.skip("OpenFOAM runtime not available on this host")

    verdict_path = tmp_path / "real-host.yaml"
    result = _run_verify("--verdict", str(verdict_path))

    assert result.returncode == 0, result.stderr
    verdict = yaml.safe_load(verdict_path.read_text())
    assert verdict["overall_verdict"] == "PASS"
    assert verdict["machine"]
    assert verdict["resolved_bashrc_path"] in [str(path) for path in available_paths]
    assert verdict["fork"] == "ESI/OpenFOAM.com"
    assert verdict["version"] == "v2312"
    assert verdict["tutorials"]
