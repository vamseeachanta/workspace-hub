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
BASELINE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "baseline-check.yml"


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


def test_workflow_runs_guard_report_on_manual_dispatch() -> None:
    # Pull requests run only pr-fast-gate.yml (owner ruling 2026-10-28).
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    triggers = data.get("on", data.get(True))

    assert set(triggers) == {"workflow_dispatch"}
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


def test_baseline_workflow_runs_guard_report_tests() -> None:
    data = yaml.safe_load(BASELINE_WORKFLOW.read_text(encoding="utf-8"))
    step = next(
        step
        for step in data["jobs"]["test"]["steps"]
        if step["name"] == "Run shell test helper guard checks"
    )

    assert "tests/enforcement/test_no_abs_paths_ci_report.py" in step["run"]


def test_guard_baseline_ratcheting_with_temporary_files(tmp_path: Path) -> None:
    script = tmp_path / "synthetic.sh"
    marker = "/" + "m" + "nt" + "/synthetic/path"
    second_marker = "/" + "ho" + "me" + "/synthetic/path"
    script.write_text(f"fixture='{marker}'\n", encoding="utf-8")
    baseline = tmp_path / "baseline.txt"
    baseline.write_text("# empty baseline\n", encoding="utf-8")

    first = _run(["bash", str(GUARD), f"--baseline={baseline}", str(script)])
    assert first.returncode == 1, first.stdout + first.stderr

    update = _run(
        ["bash", str(GUARD), f"--baseline={baseline}", "--update-baseline", str(script)]
    )
    assert update.returncode == 0, update.stdout + update.stderr

    script.write_text(
        f"fixture='{marker}'\nsecond_fixture='{second_marker}'\n",
        encoding="utf-8",
    )

    second = _run(["bash", str(GUARD), f"--baseline={baseline}", str(script)])
    assert second.returncode == 1, second.stdout + second.stderr
    finding_lines = [line for line in second.stdout.splitlines() if line]
    assert len(finding_lines) == 1
    assert second_marker in finding_lines[0]
    assert marker not in finding_lines[0]
    assert "check-no-abs-paths: 1 NEW violation(s) (not in baseline)." in second.stderr

    report = tmp_path / "report-summary.md"
    findings = tmp_path / "report-findings.txt"
    wrapper_result = _run(
        [
            "bash",
            str(WRAPPER),
            str(report),
            str(findings),
            f"--baseline={baseline}",
            str(script),
        ],
        env={
            "ABS_PATH_GUARD_MODE": "report-only",
            "RUNNER_TEMP": str(tmp_path),
        },
    )
    assert wrapper_result.returncode == 0, wrapper_result.stdout + wrapper_result.stderr
    assert "New findings: 1" in report.read_text(encoding="utf-8")
    assert findings.read_text(encoding="utf-8").count(second_marker) == 1


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
        echo 'check-no-abs-paths: 55 NEW violation(s) (not in baseline).' >&2
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
        echo 'check-no-abs-paths: 1 NEW violation(s) (not in baseline).' >&2
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


def test_wrapper_treats_exit_1_without_count_line_as_malfunction_in_both_modes(
    tmp_path: Path,
) -> None:
    guard = _write_fake_guard(
        tmp_path,
        """
        echo 'script.sh:1: generated finding'
        exit 1
        """,
    )

    for mode in ("report-only", "blocking"):
        result, summary, findings = _run_wrapper(tmp_path, guard, mode)
        assert result.returncode == 3
        summary_text = summary.read_text(encoding="utf-8")
        assert "Result: malfunction" in summary_text
        assert "missing guard count line" in summary_text
        assert "reported count: missing" in summary_text
        assert "printed finding lines: 1" in summary_text
        assert findings.read_text(encoding="utf-8") == ""


def test_wrapper_treats_exit_1_count_mismatch_as_malfunction_in_both_modes(
    tmp_path: Path,
) -> None:
    guard = _write_fake_guard(
        tmp_path,
        """
        echo 'script.sh:1: generated finding'
        echo 'check-no-abs-paths: 2 NEW violation(s) (not in baseline).' >&2
        exit 1
        """,
    )

    for mode in ("report-only", "blocking"):
        result, summary, findings = _run_wrapper(tmp_path, guard, mode)
        assert result.returncode == 3
        summary_text = summary.read_text(encoding="utf-8")
        assert "Result: malfunction" in summary_text
        assert "guard count does not match printed findings" in summary_text
        assert "reported count: 2" in summary_text
        assert "printed finding lines: 1" in summary_text
        assert findings.read_text(encoding="utf-8") == ""


def test_wrapper_treats_exit_0_with_findings_as_malfunction(tmp_path: Path) -> None:
    guard = _write_fake_guard(
        tmp_path,
        """
        echo 'script.sh:1: generated finding'
        exit 0
        """,
    )

    result, summary, findings = _run_wrapper(tmp_path, guard, "report-only")

    assert result.returncode == 3
    summary_text = summary.read_text(encoding="utf-8")
    assert "Result: malfunction" in summary_text
    assert "guard exited clean but printed findings" in summary_text
    assert "printed finding lines: 1" in summary_text
    assert findings.read_text(encoding="utf-8") == ""


def test_wrapper_treats_empty_tracked_file_list_as_malfunction(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts" / "enforcement"
    script_dir.mkdir(parents=True)
    (script_dir / "report-no-abs-paths.sh").write_text(
        WRAPPER.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (script_dir / "check-no-abs-paths.sh").write_text(
        GUARD.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    init = subprocess.run(
        ["git", "init"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    assert init.returncode == 0, init.stdout + init.stderr

    summary = tmp_path / "empty-summary.md"
    findings = tmp_path / "empty-findings.txt"
    result = subprocess.run(
        [
            "bash",
            str(script_dir / "report-no-abs-paths.sh"),
            str(summary),
            str(findings),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "ABS_PATH_GUARD_MODE": "report-only",
            "RUNNER_TEMP": str(tmp_path),
        },
    )

    assert result.returncode == 3, result.stdout + result.stderr
    summary_text = summary.read_text(encoding="utf-8")
    assert "Result: malfunction" in summary_text
    assert "tracked shell/python file list is empty" in summary_text
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
