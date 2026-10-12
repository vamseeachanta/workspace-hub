from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts" / "enforcement" / "check-no-abs-paths.sh"
WRAPPER = REPO_ROOT / "scripts" / "enforcement" / "report-no-abs-paths.sh"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "no-abs-paths-report.yml"


def _run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env.update(kwargs.pop("env", {}))
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        **kwargs,
    )


def test_workflow_runs_guard_report_on_main_prs_and_pushes() -> None:
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    triggers = data.get("on", data.get(True))

    assert triggers["pull_request"]["branches"] == ["main"]
    assert triggers["push"]["branches"] == ["main"]
    assert data["permissions"] == {"contents": "read"}

    job = data["jobs"]["no-abs-paths-report"]
    steps = job["steps"]
    run_step = next(step for step in steps if step["name"] == "Run absolute-path guard")
    assert run_step["env"]["ABS_PATH_GUARD_MODE"] == "report-only"
    assert "scripts/enforcement/report-no-abs-paths.sh" in run_step["run"]
    assert "$RUNNER_TEMP/no-abs-paths-summary.md" in run_step["run"]
    assert "$RUNNER_TEMP/no-abs-paths-findings.txt" in run_step["run"]

    upload_step = next(step for step in steps if step["name"] == "Upload full findings list")
    assert upload_step["uses"] == "actions/upload-artifact@v4"
    assert upload_step["with"]["path"] == "${{ runner.temp }}/no-abs-paths-findings.txt"


def test_guard_baseline_ratcheting_with_temporary_files(tmp_path: Path) -> None:
    script = tmp_path / "synthetic.sh"
    marker = "/" + "m" + "nt" + "/synthetic/path"
    script.write_text(f"fixture='{marker}'\n", encoding="utf-8")
    baseline = tmp_path / "baseline.txt"
    baseline.write_text("# empty baseline\n", encoding="utf-8")

    first = _run(["bash", str(GUARD), f"--baseline={baseline}", str(script)])
    assert first.returncode == 1, first.stdout + first.stderr

    update = _run(
        ["bash", str(GUARD), f"--baseline={baseline}", "--update-baseline", str(script)]
    )
    assert update.returncode == 0, update.stdout + update.stderr

    second = _run(["bash", str(GUARD), f"--baseline={baseline}", str(script)])
    assert second.returncode == 0, second.stdout + second.stderr


def _write_fake_guard(tmp_path: Path, body: str) -> Path:
    guard = tmp_path / "fake-guard.sh"
    guard.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return guard


def _run_wrapper(
    tmp_path: Path,
    guard: Path,
    mode: str,
    *extra_args: str,
) -> tuple[subprocess.CompletedProcess[str], Path, Path]:
    summary = tmp_path / "summary.md"
    findings = tmp_path / "findings.txt"
    result = _run(
        ["bash", str(WRAPPER), str(summary), str(findings), *extra_args],
        env={
            "ABS_PATH_GUARD_SCRIPT": str(guard),
            "ABS_PATH_GUARD_MODE": mode,
            "RUNNER_TEMP": str(tmp_path),
        },
    )
    return result, summary, findings


def test_wrapper_report_only_writes_summary_and_all_findings(tmp_path: Path) -> None:
    guard = _write_fake_guard(
        tmp_path,
        """
        for i in $(seq 1 55); do
          printf 'script_%03d.sh:%d: generated finding\\n' "$i" "$i"
        done
        exit 1
        """,
    )

    result, summary, findings = _run_wrapper(tmp_path, guard, "report-only")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "New findings: 55" in summary.read_text(encoding="utf-8")
    assert len([line for line in findings.read_text(encoding="utf-8").splitlines() if line]) == 55
    assert "script_050.sh" in summary.read_text(encoding="utf-8")
    assert "script_051.sh" not in summary.read_text(encoding="utf-8")


def test_wrapper_blocking_mode_fails_on_findings(tmp_path: Path) -> None:
    guard = _write_fake_guard(
        tmp_path,
        """
        echo 'script.sh:1: generated finding'
        exit 1
        """,
    )

    result, summary, findings = _run_wrapper(tmp_path, guard, "blocking")

    assert result.returncode == 1
    assert "New findings: 1" in summary.read_text(encoding="utf-8")
    assert findings.read_text(encoding="utf-8").count("generated finding") == 1


def test_wrapper_malfunction_fails_in_both_modes(tmp_path: Path) -> None:
    missing_guard = tmp_path / "missing-guard.sh"

    for mode in ("report-only", "blocking"):
        result, summary, findings = _run_wrapper(tmp_path, missing_guard, mode)
        assert result.returncode != 0
        assert "Result: malfunction" in summary.read_text(encoding="utf-8")
        assert findings.read_text(encoding="utf-8") == ""


def test_wrapper_zero_findings_succeeds(tmp_path: Path) -> None:
    guard = _write_fake_guard(
        tmp_path,
        """
        exit 0
        """,
    )

    result, summary, findings = _run_wrapper(tmp_path, guard, "blocking")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "New findings: 0" in summary.read_text(encoding="utf-8")
    assert findings.read_text(encoding="utf-8") == ""


def test_wrapper_forwards_guard_arguments_for_malfunction_coverage(tmp_path: Path) -> None:
    result, summary, findings = _run_wrapper(
        tmp_path,
        GUARD,
        "report-only",
        "--unknown-flag-for-test",
    )

    assert result.returncode != 0
    assert "Result: malfunction" in summary.read_text(encoding="utf-8")
    assert findings.read_text(encoding="utf-8") == ""
