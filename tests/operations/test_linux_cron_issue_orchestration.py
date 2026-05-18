"""TDD tests for #2740 Linux cron/GitHub-label issue orchestration."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "operations" / "linux-cron-issue-orchestrator.py"
spec = importlib.util.spec_from_file_location("linux_cron_issue_orchestrator", MODULE_PATH)
assert spec is not None
module = importlib.util.module_from_spec(spec)
sys.modules["linux_cron_issue_orchestrator"] = module
assert spec.loader is not None
spec.loader.exec_module(module)


def _issue(number: int, labels: list[str], *, updated_at: str = "2026-05-18T00:00:00Z") -> dict[str, object]:
    return {
        "number": number,
        "title": f"Issue {number}",
        "url": f"https://github.com/example/repo/issues/{number}",
        "updatedAt": updated_at,
        "labels": [{"name": label} for label in labels],
    }


def _init_clean_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)
    (path / "README.md").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _init_clean_repo_with_remote(path: Path, remote_path: Path) -> None:
    subprocess.run(["git", "init", "--bare", str(remote_path)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    _init_clean_repo(path)
    subprocess.run(["git", "branch", "-M", "main"], cwd=path, check=True)
    subprocess.run(["git", "remote", "add", "origin", str(remote_path)], cwd=path, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def test_queue_selects_by_canonical_machine_label(tmp_path: Path) -> None:
    (tmp_path / "101.md").write_text("approved", encoding="utf-8")
    issues = [
        _issue(101, ["machine:dev-primary", "agent:codex", "status:plan-approved"]),
        _issue(102, ["machine:dev-secondary", "agent:codex", "status:plan-approved"]),
    ]

    actions = module.plan_tick(issues, host_machine_label="machine:dev-primary", plan_marker_dir=tmp_path, readiness={"status": "pass"})

    assert [action["issue"] for action in actions] == [101]
    assert actions[0]["decision"] == "awaiting_lease"


def test_exactly_one_machine_and_agent_required(tmp_path: Path) -> None:
    issues = [
        _issue(201, ["agent:codex", "status:plan-approved"]),
        _issue(202, ["machine:dev-primary", "machine:dev-secondary", "agent:codex", "status:plan-approved"]),
        _issue(203, ["machine:dev-primary", "status:plan-approved"]),
        _issue(204, ["machine:dev-primary", "agent:codex", "agent:claude", "status:plan-approved"]),
    ]

    actions = module.plan_tick(issues, host_machine_label="machine:dev-primary", plan_marker_dir=tmp_path, readiness={"status": "pass"})

    by_issue = {action["issue"]: action for action in actions}
    assert by_issue[201]["decision"] == "blocked"
    assert by_issue[201]["reason"] == "expected exactly one machine label"
    assert by_issue[202]["decision"] == "blocked"
    assert by_issue[203]["reason"] == "expected exactly one agent label"
    assert by_issue[204]["decision"] == "blocked"
    assert all(action["execute_provider"] is False for action in actions)


def test_needs_plan_and_plan_review_are_report_only(tmp_path: Path) -> None:
    issues = [
        _issue(301, ["machine:dev-primary", "agent:codex", "status:needs-plan"]),
        _issue(302, ["machine:dev-primary", "agent:codex", "status:plan-review"]),
    ]

    actions = module.plan_tick(issues, host_machine_label="machine:dev-primary", plan_marker_dir=tmp_path, readiness={"status": "pass"})

    assert [action["decision"] for action in actions] == ["report_only", "report_only"]
    assert all(action["execute_provider"] is False for action in actions)
    assert {action["mode"] for action in actions} == {"planning_candidate", "review_candidate"}


def test_implementation_requires_plan_approved_and_marker(tmp_path: Path) -> None:
    (tmp_path / "402.md").write_text("approved", encoding="utf-8")
    issues = [
        _issue(401, ["machine:dev-primary", "agent:codex", "status:plan-approved"]),
        _issue(402, ["machine:dev-primary", "agent:codex", "status:plan-approved"]),
    ]

    actions = module.plan_tick(issues, host_machine_label="machine:dev-primary", plan_marker_dir=tmp_path, readiness={"status": "pass"})

    by_issue = {action["issue"]: action for action in actions}
    assert by_issue[401]["decision"] == "blocked"
    assert by_issue[401]["reason"] == "missing local plan approval marker"
    assert by_issue[402]["decision"] == "awaiting_lease"
    assert by_issue[402]["execute_provider"] is False


def test_remote_ref_lease_is_required_before_execution(tmp_path: Path) -> None:
    (tmp_path / "501.md").write_text("approved", encoding="utf-8")
    issue = _issue(501, ["machine:dev-primary", "agent:codex", "status:plan-approved"])

    without_lease = module.plan_tick([issue], host_machine_label="machine:dev-primary", plan_marker_dir=tmp_path, readiness={"status": "pass"}, lease_acquired=False)
    with_lease = module.plan_tick([issue], host_machine_label="machine:dev-primary", plan_marker_dir=tmp_path, readiness={"status": "pass"}, lease_acquired=True, worktree_clean=True)

    assert without_lease[0]["decision"] == "awaiting_lease"
    assert without_lease[0]["execute_provider"] is False
    assert without_lease[0]["lease_ref"] == "refs/heads/dispatch/leases/501-implementation"
    assert with_lease[0]["decision"] == "ready_to_execute"
    assert with_lease[0]["execute_provider"] is True


def test_dirty_readiness_blocks_worker(tmp_path: Path) -> None:
    (tmp_path / "601.md").write_text("approved", encoding="utf-8")
    issue = _issue(601, ["machine:dev-primary", "agent:codex", "status:plan-approved"])

    actions = module.plan_tick([issue], host_machine_label="machine:dev-primary", plan_marker_dir=tmp_path, readiness={"status": "fail", "failures": ["dirty workspace"]}, lease_acquired=True)

    assert actions == [
        {
            "issue": None,
            "decision": "blocked",
            "reason": "host readiness failed",
            "failures": ["dirty workspace"],
            "execute_provider": False,
        }
    ]


def test_status_comment_redacts_secrets() -> None:
    action = {
        "issue": 701,
        "decision": "blocked",
        "reason": "TELEGRAM_BOT_TOKEN=123456:ABCDEFabcdefABCDEFabcdefABCDEF; gh auth token ***; allowed_users=12345",
        "execute_provider": False,
    }

    comment = module.format_status_comment(action)

    assert "123456:ABCDEF" not in comment
    assert "***" not in comment
    assert "12345" not in comment
    assert "[REDACTED]" in comment


def test_local_no_overlap_lock_blocks_second_tick(tmp_path: Path) -> None:
    lock_path = tmp_path / "cron.lock"

    with module.no_overlap_lock(lock_path):
        assert module.try_no_overlap_lock(lock_path) is False

    assert module.try_no_overlap_lock(lock_path) is True


def test_priority_ordering_is_deterministic(tmp_path: Path) -> None:
    for issue_number in (801, 802, 803, 804):
        (tmp_path / f"{issue_number}.md").write_text("approved", encoding="utf-8")
    issues = [
        _issue(803, ["machine:dev-primary", "agent:codex", "status:plan-approved", "priority:medium"], updated_at="2026-05-18T02:00:00Z"),
        _issue(801, ["machine:dev-primary", "agent:codex", "status:plan-approved", "priority:high"], updated_at="2026-05-18T03:00:00Z"),
        _issue(804, ["machine:dev-primary", "agent:codex", "status:plan-approved"], updated_at="2026-05-18T00:00:00Z"),
        _issue(802, ["machine:dev-primary", "agent:codex", "status:plan-approved", "priority:high"], updated_at="2026-05-18T01:00:00Z"),
    ]

    actions = module.plan_tick(issues, host_machine_label="machine:dev-primary", plan_marker_dir=tmp_path, readiness={"status": "pass"})

    assert [action["issue"] for action in actions] == [802, 801, 803, 804]


def test_cli_defaults_to_dry_run_and_uses_real_readiness_and_git_cleanliness(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_clean_repo(repo_root)
    (tmp_path / "901.md").write_text("approved", encoding="utf-8")
    issues_path = tmp_path / "issues.json"
    issues_path.write_text(json.dumps([_issue(901, ["machine:dev-primary", "agent:codex", "status:plan-approved"])]), encoding="utf-8")
    readiness_path = tmp_path / "readiness.json"
    readiness_path.write_text(json.dumps({"status": "pass", "failures": []}), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--host-machine-label",
            "machine:dev-primary",
            "--plan-marker-dir",
            str(tmp_path),
            "--issues-json",
            str(issues_path),
            "--readiness-json",
            str(readiness_path),
            "--repo-root",
            str(repo_root),
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["mode"] == "dry-run"
    assert payload["actions"][0]["decision"] == "awaiting_lease"
    assert payload["actions"][0]["execute_provider"] is False
    assert "provider execution disabled" in payload["summary"]


def test_cli_blocks_when_readiness_json_fails(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_clean_repo(repo_root)
    issues_path = tmp_path / "issues.json"
    issues_path.write_text(json.dumps([_issue(902, ["machine:dev-primary", "agent:codex", "status:plan-approved"])]), encoding="utf-8")
    readiness_path = tmp_path / "readiness.json"
    readiness_path.write_text(json.dumps({"status": "fail", "failures": ["unsafe gateway"]}), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--host-machine-label",
            "machine:dev-primary",
            "--plan-marker-dir",
            str(tmp_path),
            "--issues-json",
            str(issues_path),
            "--readiness-json",
            str(readiness_path),
            "--repo-root",
            str(repo_root),
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["actions"][0]["decision"] == "blocked"
    assert payload["actions"][0]["reason"] == "host readiness failed"
    assert "unsafe gateway" in payload["actions"][0]["failures"]
    assert payload["actions"][0]["execute_provider"] is False


def test_cli_execute_fails_closed_when_readiness_json_missing(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_clean_repo(repo_root)
    (tmp_path / "904.md").write_text("approved", encoding="utf-8")
    issues_path = tmp_path / "issues.json"
    issues_path.write_text(json.dumps([_issue(904, ["machine:dev-primary", "agent:codex", "status:plan-approved"])]), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--host-machine-label",
            "machine:dev-primary",
            "--plan-marker-dir",
            str(tmp_path),
            "--issues-json",
            str(issues_path),
            "--repo-root",
            str(repo_root),
            "--execute",
            "--lease-acquired",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["actions"][0]["decision"] == "blocked"
    assert payload["actions"][0]["reason"] == "host readiness failed"
    assert payload["actions"][0]["failures"] == ["readiness evidence missing"]
    assert payload["actions"][0]["execute_provider"] is False


def test_cli_rejects_host_machine_label_not_in_registry(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_clean_repo(repo_root)
    (tmp_path / "905.md").write_text("approved", encoding="utf-8")
    issues_path = tmp_path / "issues.json"
    issues_path.write_text(json.dumps([_issue(905, ["machine:totally-made-up", "agent:codex", "status:plan-approved"])]), encoding="utf-8")
    readiness_path = tmp_path / "readiness.json"
    readiness_path.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text("machines:\n  dev-primary:\n    hostname: ace-linux-1\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--host-machine-label",
            "machine:totally-made-up",
            "--plan-marker-dir",
            str(tmp_path),
            "--issues-json",
            str(issues_path),
            "--readiness-json",
            str(readiness_path),
            "--repo-root",
            str(repo_root),
            "--registry-yaml",
            str(registry_path),
            "--execute",
            "--lease-acquired",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["actions"][0]["decision"] == "blocked"
    assert payload["actions"][0]["reason"] == "host machine label is not registered"
    assert payload["actions"][0]["host_machine_label"] == "machine:totally-made-up"
    assert payload["actions"][0]["execute_provider"] is False


def test_cli_enforces_no_overlap_lock(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_clean_repo(repo_root)
    issues_path = tmp_path / "issues.json"
    issues_path.write_text(json.dumps([]), encoding="utf-8")
    readiness_path = tmp_path / "readiness.json"
    readiness_path.write_text(json.dumps({"status": "pass"}), encoding="utf-8")
    lock_path = tmp_path / "cron.lock"

    with module.no_overlap_lock(lock_path):
        completed = subprocess.run(
            [
                sys.executable,
                str(MODULE_PATH),
                "--host-machine-label",
                "machine:dev-primary",
                "--issues-json",
                str(issues_path),
                "--readiness-json",
                str(readiness_path),
                "--repo-root",
                str(repo_root),
                "--lock-path",
                str(lock_path),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    assert completed.returncode == 75
    payload = json.loads(completed.stdout)
    assert payload["actions"][0]["decision"] == "blocked"
    assert payload["actions"][0]["reason"] == "cron tick already running"


def test_cli_blocks_dirty_or_ahead_repo_without_trusting_worktree_flag(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_clean_repo(repo_root)
    (repo_root / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    (tmp_path / "903.md").write_text("approved", encoding="utf-8")
    issues_path = tmp_path / "issues.json"
    issues_path.write_text(json.dumps([_issue(903, ["machine:dev-primary", "agent:codex", "status:plan-approved"])]), encoding="utf-8")
    readiness_path = tmp_path / "readiness.json"
    readiness_path.write_text(json.dumps({"status": "pass", "failures": []}), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--host-machine-label",
            "machine:dev-primary",
            "--plan-marker-dir",
            str(tmp_path),
            "--issues-json",
            str(issues_path),
            "--readiness-json",
            str(readiness_path),
            "--repo-root",
            str(repo_root),
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["actions"][0]["decision"] == "blocked"
    assert payload["actions"][0]["reason"] == "execution worktree is not clean"
    assert payload["actions"][0]["execute_provider"] is False


def test_cli_blocks_ahead_repo_without_dirty_files(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_clean_repo_with_remote(repo_root, tmp_path / "origin.git")
    (repo_root / "README.md").write_text("test\nahead\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-m", "ahead"], cwd=repo_root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    (tmp_path / "906.md").write_text("approved", encoding="utf-8")
    issues_path = tmp_path / "issues.json"
    issues_path.write_text(json.dumps([_issue(906, ["machine:dev-primary", "agent:codex", "status:plan-approved"])]), encoding="utf-8")
    readiness_path = tmp_path / "readiness.json"
    readiness_path.write_text(json.dumps({"status": "pass", "failures": []}), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--host-machine-label",
            "machine:dev-primary",
            "--plan-marker-dir",
            str(tmp_path),
            "--issues-json",
            str(issues_path),
            "--readiness-json",
            str(readiness_path),
            "--repo-root",
            str(repo_root),
            "--execute",
            "--lease-acquired",
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["actions"][0]["decision"] == "blocked"
    assert payload["actions"][0]["reason"] == "execution worktree is not clean"
    assert payload["actions"][0]["execute_provider"] is False


def test_documentation_preserves_safe_cron_contract() -> None:
    contract = (REPO_ROOT / "docs" / "ops" / "linux-cron-issue-orchestration.md").read_text(encoding="utf-8")
    control_plane = (REPO_ROOT / "docs" / "ops" / "telegram-hermes-multimachine-control-plane.md").read_text(encoding="utf-8")

    required_phrases = [
        "status:needs-plan` and `status:plan-review` are report-only",
        "status:plan-approved` plus `.planning/plan-approved/<issue>.md`",
        "refs/heads/dispatch/leases/<issue>-<mode>",
        "flock",
        "clean disposable per-issue worktree",
        "dry-run is the default",
        "Direct Telegram-to-machine dispatch is deferred",
        "host-local readiness evidence",
        "raw environment values, chat IDs, allowlists, and bot tokens must never be written",
        "canonical machine labels from `config/workstations/registry.yaml`",
    ]
    for phrase in required_phrases:
        assert phrase in contract

    assert "Linux cron/GitHub-label orchestration is the MVP" in control_plane
    assert "Telegram/Hermes is status and notification surface" in control_plane
