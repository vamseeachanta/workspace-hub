"""Structural contract for .github/workflows/legal-client-pii-gate.yml (#3775, Task 1).

The PR-only gate never saw a bot push. Two facts drive every assertion here:

1. `github-actions[bot]` pushes made with the default GITHUB_TOKEN — the
   kanban-reconcile "anti-loop split" — do NOT create a `push` workflow run.
   A push trigger alone is therefore BLIND to exactly the writer this issue is
   about, so a time-based trigger is load-bearing, not decoration.
2. The scan runs on a PUBLIC repo's log surface and escalates into a PUBLIC
   issue, so neither may carry a matched value OR a file path (a path can
   itself contain a client identifier).

These are property assertions on the parsed YAML: delete the behaviour and the
test goes red.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

REPO_ROOT = Path(__file__).resolve().parents[2]
WF_PATH = REPO_ROOT / ".github" / "workflows" / "legal-client-pii-gate.yml"

PR_JOB = "client-pii-gate"
MAIN_JOB = "main-branch-scan"


@pytest.fixture(scope="module")
def wf() -> dict:
    return yaml.safe_load(WF_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def raw() -> str:
    return WF_PATH.read_text(encoding="utf-8")


def triggers(wf: dict) -> dict:
    # PyYAML parses a bare `on:` key as the boolean True.
    return wf.get("on", wf.get(True))


def run_blocks(job: dict) -> list[str]:
    return [s["run"] for s in job.get("steps", []) if isinstance(s.get("run"), str)]


def scan_command(wf: dict) -> str:
    """The main-branch scan step's shell body ONLY.

    Scoped deliberately: the escalation step's issue-body prose mentions the
    scanner's flags, so asserting `"--quiet" in <whole job>` passes even after
    the flag is removed from the command. That mutation survived once already.
    """
    for step in wf["jobs"][MAIN_JOB]["steps"]:
        if step.get("id") == "scan":
            return step["run"]
    raise AssertionError("no step with id: scan in the main-branch job")


# ── it parses ─────────────────────────────────────────────────────────────────


def test_workflow_yaml_parses(wf):
    assert isinstance(wf, dict) and wf.get("name")


# ── triggers ──────────────────────────────────────────────────────────────────


def test_pull_request_trigger_survives(wf):
    pr = triggers(wf)["pull_request"]
    assert "main" in pr["branches"]
    assert set(pr["types"]) >= {"opened", "synchronize", "reopened", "edited"}


def test_push_to_main_is_scanned(wf):
    push = triggers(wf)["push"]
    assert "main" in push["branches"]


def test_a_time_based_trigger_exists(wf):
    """GITHUB_TOKEN bot pushes never fire `push`; only a clock can see them."""
    sched = triggers(wf).get("schedule")
    assert sched, "no schedule: a push trigger cannot observe GITHUB_TOKEN bot pushes"
    assert all(re.match(r"^\S+ \S+ \S+ \S+ \S+$", e["cron"]) for e in sched)


def test_schedule_does_not_collide_with_the_kanban_reconciler(wf):
    """kanban-reconcile runs */20; do not stack a full-tree scan on the same tick."""
    for entry in triggers(wf)["schedule"]:
        minute = entry["cron"].split()[0]
        assert minute not in ("*", "*/20", "0,20,40"), entry["cron"]


def test_manual_trigger_available(wf):
    assert "workflow_dispatch" in triggers(wf)


# ── the PR gate is untouched ──────────────────────────────────────────────────


def test_pr_job_still_scans_diff_and_metadata(wf):
    job = wf["jobs"][PR_JOB]
    blob = "\n".join(run_blocks(job))
    assert "--base-ref" in blob
    assert "--stdin" in blob
    assert "check-client-pii.py" in blob


def test_pr_job_condition_can_never_skip_on_a_pull_request(wf):
    """A required check that SKIPS deadlocks PRs. Its `if` must hold on PR events."""
    cond = wf["jobs"][PR_JOB].get("if")
    if cond is None:
        return
    assert "pull_request" in cond
    assert "!=" not in cond, f"a negated condition can skip the required check: {cond}"


# ── the main-branch job ───────────────────────────────────────────────────────


def test_main_job_exists_and_never_runs_on_pull_request(wf):
    job = wf["jobs"][MAIN_JOB]
    assert "pull_request" in job["if"]


def test_main_job_scans_the_whole_tracked_tree_not_a_diff(wf):
    """There is no base ref on main. A diff scan here would find nothing."""
    cmd = scan_command(wf)
    assert "--all" in cmd
    assert "--base-ref" not in cmd


def test_main_job_reuses_the_secret_and_strict_convention(wf):
    job = wf["jobs"][MAIN_JOB]
    blob = "\n".join(run_blocks(job)) + str(job)
    assert "LEGAL_CLIENT_MAP" in blob
    assert "--strict" in blob or "STRICT" in blob


# ── ANTI-LOOP: the scan must never write to the repo ──────────────────────────

_WRITE_PATTERNS = [
    r"\bgit\s+push\b",
    r"\bgit\s+commit\b",
    r"\bgit\s+add\b",
    r"\bgit\s+tag\b",
    r"peter-evans/create-pull-request",
    r"stefanzweifel/git-auto-commit",
]


def test_main_job_never_writes_to_the_repository(wf):
    """A push-triggered job that pushes recreates the loop the split prevents."""
    job = wf["jobs"][MAIN_JOB]
    blob = "\n".join(run_blocks(job)) + "\n" + "\n".join(
        str(s.get("uses", "")) for s in job["steps"]
    )
    for pat in _WRITE_PATTERNS:
        assert not re.search(pat, blob), f"main-branch scan writes to the repo: {pat}"


def test_main_job_has_no_contents_write_permission(wf):
    """Least privilege is the structural half of the anti-loop guarantee."""
    perms = wf["jobs"][MAIN_JOB].get("permissions")
    assert isinstance(perms, dict), "main-branch scan must pin its permissions"
    assert perms.get("contents") == "read"


def test_workflow_default_permissions_are_read_only(wf):
    assert wf.get("permissions", {}).get("contents") == "read"


def test_main_job_checkout_does_not_persist_credentials(wf):
    """No pushable credential in the workspace => the loop cannot start by accident."""
    for step in wf["jobs"][MAIN_JOB]["steps"]:
        if str(step.get("uses", "")).startswith("actions/checkout"):
            assert step.get("with", {}).get("persist-credentials") is False


def test_main_job_serialises_with_itself(wf):
    """Overlapping full-tree scans would race on issue create/dedup."""
    grp = wf["jobs"][MAIN_JOB].get("concurrency") or wf.get("concurrency")
    assert grp, "no concurrency group on the scheduled full-tree scan"


# ── escalation: what actually reaches a human ─────────────────────────────────


def test_escalation_opens_a_github_issue(wf):
    """A red run is a signal only if someone looks. An issue is assignable."""
    blob = "\n".join(run_blocks(wf["jobs"][MAIN_JOB]))
    assert "gh issue create" in blob


def test_escalation_deduplicates_before_creating(wf):
    """*/6h + push would otherwise open a new issue on every single run."""
    blob = "\n".join(run_blocks(wf["jobs"][MAIN_JOB]))
    assert "gh issue list" in blob
    assert blob.index("gh issue list") < blob.index("gh issue create")


def test_escalation_needs_issues_write(wf):
    assert wf["jobs"][MAIN_JOB]["permissions"].get("issues") == "write"


def test_run_fails_when_identifiers_are_present(wf):
    """The issue is the durable signal; the red run is the immediate one."""
    blob = "\n".join(run_blocks(wf["jobs"][MAIN_JOB]))
    assert re.search(r"\bexit 1\b", blob)


# ── leak safety of the escalation surface ─────────────────────────────────────


def test_main_job_scan_runs_in_quiet_mode(wf):
    """Paths reach the PUBLIC Actions log; a path can contain a client name."""
    assert "--quiet" in scan_command(wf)


def test_main_job_consumes_only_the_path_free_json_report(wf):
    assert "--report-json" in scan_command(wf)


def test_escalation_never_cats_scanner_output_anywhere(wf):
    """No `cat`/`tee` of scanner stdout/stderr into the log, summary, or issue."""
    blob = "\n".join(run_blocks(wf["jobs"][MAIN_JOB]))
    for pat in [r"\bcat\s+\"?\$?\{?RUNNER_TEMP", r"\btee\b", r"\bgit\s+diff\b"]:
        assert not re.search(pat, blob), f"scanner detail may reach a public surface: {pat}"


def test_materialised_map_is_written_but_never_read_back_to_stdout(wf, raw):
    """The secret lands in a file and is passed by PATH. Nothing may dump it."""
    for job in wf["jobs"].values():
        blob = "\n".join(run_blocks(job))
        assert not re.search(
            r"\b(cat|head|tail|base64|xxd|od|less|more)\b[^\n]*client-map\.yaml", blob
        )


def test_secret_is_only_referenced_through_env(raw):
    """`${{ secrets.* }}` interpolated into a shell body is a leak/injection risk."""
    for line in raw.splitlines():
        if "secrets.LEGAL_CLIENT_MAP" in line:
            assert re.match(r"\s*[A-Z_]+:\s*\$\{\{\s*secrets\.", line), line
