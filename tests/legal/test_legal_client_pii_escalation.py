"""Behavioural test for the main-branch escalation step (#3775, Task 1).

The structural tests in test_legal_client_pii_gate_workflow.py assert that the
workflow *says* the right things. This file EXECUTES the step's shell body
against a stubbed `gh` and asserts what it *does* — which outcome exits non-zero,
which one opens an issue, and which one stays silent.

That distinction is not academic: two string-matching assertions in the sibling
file survived mutation (`--quiet` and `exit 1` both appear more than once in the
job), which is precisely the vacuous-guard failure mode in
.claude/rules/guards-must-discriminate.md. These tests kill those mutants by
running the code.

No client identifiers anywhere — the step never sees file content, only counts
and a digest from the scanner's JSON report.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

REPO_ROOT = Path(__file__).resolve().parents[2]
WF_PATH = REPO_ROOT / ".github" / "workflows" / "legal-client-pii-gate.yml"

pytestmark = pytest.mark.skipif(
    shutil.which("jq") is None or shutil.which("bash") is None,
    reason="needs bash + jq (both present on ubuntu-latest runners)",
)

GH_STUB = """#!/usr/bin/env bash
echo "$*" >> "$GH_LOG"
case "$1 $2" in
  "issue list") cat "$EXISTING_FIXTURE" ;;
  "issue view") printf 'preamble\\n<!-- pii-fingerprint: %s -->\\n' "$PREV_FP" ;;
esac
exit 0
"""


@pytest.fixture(scope="module")
def escalate_body() -> str:
    wf = yaml.safe_load(WF_PATH.read_text(encoding="utf-8"))
    for step in wf["jobs"]["main-branch-scan"]["steps"]:
        if step.get("name") == "Escalate":
            return step["run"]
    raise AssertionError("no Escalate step in the main-branch job")


class Result:
    def __init__(self, code: int, gh_calls: list[str], body: str | None, out: str,
                 summary: str = ""):
        self.code = code
        self.gh_calls = gh_calls
        self.body = body
        self.out = out
        self.summary = summary

    def called(self, prefix: str) -> bool:
        return any(c.startswith(prefix) for c in self.gh_calls)


def escalate(tmp_path: Path, escalate_body: str, *, status: str, rc: str,
             flagged: int = 0, scanned: int = 33012, fp: str = "",
             existing: str = "", prev_fp: str = "",
             write_report: bool = True) -> Result:
    work = tmp_path / f"run-{status}-{rc}-{existing or 'none'}-{fp or 'x'}"
    work.mkdir(parents=True, exist_ok=True)
    stub_dir = work / "bin"
    stub_dir.mkdir()
    gh = stub_dir / "gh"
    gh.write_text(GH_STUB, encoding="utf-8")
    gh.chmod(0o755)

    report = work / "pii-report.json"
    if write_report:
        report.write_text(
            '{"status":"%s","scanned":%d,"files_flagged":%d,"fingerprint":"%s"}\n'
            % (status, scanned, flagged, fp),
            encoding="utf-8",
        )
    fixture = work / "existing.txt"
    fixture.write_text(existing, encoding="utf-8")
    gh_log = work / "gh.log"
    gh_log.write_text("", encoding="utf-8")
    summary = work / "summary.md"
    summary.write_text("", encoding="utf-8")
    body_file = work / "pii-issue-body.md"

    env = dict(os.environ)
    env.update(
        PATH=f"{stub_dir}:{env['PATH']}",
        GH_LOG=str(gh_log), EXISTING_FIXTURE=str(fixture), PREV_FP=prev_fp,
        REPORT=str(report), BODY_FILE=str(body_file), RUNNER_TEMP=str(work),
        GITHUB_STEP_SUMMARY=str(summary),
        GH_TOKEN="stub", GH_REPO="o/r", RC=rc, EVENT="schedule",
        SHA="cafebabe1234", RUN_URL="https://example.invalid/run/1",
        LABEL="legal:client-pii", TITLE="Client identifier present in tracked files on main",
    )
    script = work / "escalate.sh"
    script.write_text(escalate_body, encoding="utf-8")
    p = subprocess.run(["bash", str(script)], capture_output=True, text=True, env=env)
    calls = [ln for ln in gh_log.read_text(encoding="utf-8").splitlines() if ln.strip()]
    body = body_file.read_text(encoding="utf-8") if body_file.exists() else None
    return Result(p.returncode, calls, body, p.stdout + p.stderr,
                  summary.read_text(encoding="utf-8"))


# ── the run must actually go red on a finding ─────────────────────────────────


def test_violations_fail_the_run(tmp_path, escalate_body):
    r = escalate(tmp_path, escalate_body, status="violations", rc="1", flagged=15, fp="aa11")
    assert r.code != 0, "a client identifier on main left the run green"


def test_clean_passes_the_run(tmp_path, escalate_body):
    r = escalate(tmp_path, escalate_body, status="clean", rc="0")
    assert r.code == 0, r.out


# ── issue lifecycle ───────────────────────────────────────────────────────────


def test_violations_open_an_issue_when_none_is_open(tmp_path, escalate_body):
    r = escalate(tmp_path, escalate_body, status="violations", rc="1", flagged=15, fp="aa11")
    assert r.called("issue create")


def test_violations_do_not_open_a_second_issue(tmp_path, escalate_body):
    r = escalate(tmp_path, escalate_body, status="violations", rc="1", flagged=15,
                 fp="aa11", existing="42", prev_fp="aa11")
    assert not r.called("issue create")


def test_unchanged_finding_stays_silent(tmp_path, escalate_body):
    """*/3h + every push: re-commenting an unchanged finding is issue spam."""
    r = escalate(tmp_path, escalate_body, status="violations", rc="1", flagged=15,
                 fp="aa11", existing="42", prev_fp="aa11")
    assert not r.called("issue comment")
    assert not r.called("issue edit")


def test_changed_finding_pings_once(tmp_path, escalate_body):
    r = escalate(tmp_path, escalate_body, status="violations", rc="1", flagged=17,
                 fp="bb22", existing="42", prev_fp="aa11")
    assert r.called("issue edit")
    assert r.called("issue comment")


def test_clean_retires_an_open_alarm(tmp_path, escalate_body):
    r = escalate(tmp_path, escalate_body, status="clean", rc="0", existing="42", prev_fp="aa11")
    assert r.called("issue close")


def test_clean_with_no_open_issue_touches_nothing(tmp_path, escalate_body):
    r = escalate(tmp_path, escalate_body, status="clean", rc="0")
    assert not r.called("issue create")
    assert not r.called("issue comment")
    assert not r.called("issue close")


# ── inconclusive is not a pass, and is not a PII alarm either ─────────────────


def test_strict_inconclusive_fails_without_filing_a_pii_issue(tmp_path, escalate_body):
    """Missing map is a provisioning defect: go red, but do not cry leak."""
    r = escalate(tmp_path, escalate_body, status="inconclusive", rc="2")
    assert r.code != 0
    assert not r.called("issue create")


def test_degraded_open_warns_without_failing(tmp_path, escalate_body):
    """No secret (fork/unconfigured): nothing was verified, but nothing is claimed."""
    r = escalate(tmp_path, escalate_body, status="inconclusive", rc="0")
    assert r.code == 0
    assert not r.called("issue create")
    assert "warning" in r.out.lower()


def test_missing_report_is_an_error_not_a_pass(tmp_path, escalate_body):
    """Scanner crashed / uv failed: absence of a finding is not a finding of none.

    Asserting only `code != 0` is NOT enough — `set -e` plus a jq failure on the
    absent file produces a non-zero exit even with the guard deleted, so that
    assertion discriminates nothing (it survived mutation). The property that
    actually distinguishes the guard is whether a HUMAN-READABLE record of the
    failure reaches the job summary, rather than an opaque jq parse error.
    """
    r = escalate(tmp_path, escalate_body, status="clean", rc="0", write_report=False)
    assert r.code != 0
    assert not r.called("issue create")
    assert r.summary.strip(), "no job-summary record — the failure is opaque to a human"
    assert "scan" in r.summary.lower()


# ── the public issue body carries counts, never paths or values ───────────────


def test_issue_body_is_rendered_with_no_unsubstituted_placeholders(tmp_path, escalate_body):
    r = escalate(tmp_path, escalate_body, status="violations", rc="1", flagged=15,
                 scanned=33012, fp="deadbeef")
    assert r.body is not None
    assert "__" not in r.body, f"placeholder left in the issue body:\n{r.body}"
    assert "15" in r.body and "33012" in r.body
    assert "deadbeef" in r.body


def test_issue_body_carries_no_filesystem_paths(tmp_path, escalate_body):
    """Everything the step knows comes from a path-free JSON report — keep it that way."""
    r = escalate(tmp_path, escalate_body, status="violations", rc="1", flagged=15, fp="aa11")
    assert str(tmp_path) not in r.body
    assert "/home/" not in r.body and "RUNNER_TEMP" not in r.body


def test_no_surface_echoes_the_runner_temp_report(tmp_path, escalate_body):
    r = escalate(tmp_path, escalate_body, status="violations", rc="1", flagged=15, fp="aa11")
    assert '"files_flagged"' not in r.out, "raw report JSON reached the log"
