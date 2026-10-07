"""Authorized implementation must not depend on a second plan-approval event."""
from pathlib import Path
import sys
import subprocess
import shutil
import os

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/governance"))
from workflow_decision import _operation


def test_substantial_implementation_uses_task_authority():
    result = _operation({"operation_kind": "edit"}, ["src/service.py"],
                        {"substantial-change"}, "originating-user-task")
    assert result["risk_class"] == "substantial"
    assert result["action_boundary"] == "verify-task-authority"
    assert "APPROVAL_REQUIRED" not in result["reason_codes"]
    assert result["authorization_assessment"] == "unverified-reference"


def test_consequential_effect_still_needs_matching_authority():
    result = _operation({"operation_kind": "execute"}, [],
                        {"publication"}, "originating-user-task")
    assert result["action_boundary"] == "approval-required"


def test_substantial_scope_without_task_authority_still_needs_context():
    result = _operation({"operation_kind": "edit"}, ["src/service.py"],
                        {"substantial-change"}, None)
    assert result["action_boundary"] == "needs-context"
    assert result["authorization_assessment"] == "missing"


def test_canonical_policy_explicitly_removes_separate_plan_gate():
    text = (ROOT / "config/agents/SHARED_SOUL.md").read_text(encoding="utf-8")
    assert "No separate user approval of a plan is required before implementation" in text
    assert "Explicit approval of the concrete current plan" not in text


def test_primary_harness_does_not_require_substantial_plan_approval():
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "task request authorizes implementation" in text


def test_retired_marker_consumers_do_not_block_without_a_marker(tmp_path):
    bash = shutil.which("bash")
    if sys.platform == "win32":
        native = Path(os.environ["ProgramFiles"]) / "Git/bin/bash.exe"
        assert native.is_file(), "Native Git Bash is required for Windows hook tests"
        bash = str(native)
    for relative, args, payload in [
        (".claude/hooks/plan-approval-gate.sh", [],
         '{"tool_name":"Write","tool_input":{"file_path":"src/service.py"}}'),
        ("scripts/enforcement/require-plan-approval.sh", ["--strict"], ""),
    ]:
        result = subprocess.run([bash, str(ROOT / relative), *args], cwd=tmp_path,
                                input=payload, text=True, capture_output=True)
        assert result.returncode == 0
        assert '"decision":"block"' not in result.stdout
        assert "retired" in (result.stdout + result.stderr).lower()


def test_retired_server_gate_does_not_fetch_github_authority(monkeypatch, capsys):
    sys.path.insert(0, str(ROOT / "scripts/workflow"))
    import plan_approval_gate_check as gate
    monkeypatch.setenv("PLAN_APPROVAL_GATE_ENABLED", "1")
    def forbidden(*args, **kwargs):
        raise AssertionError("Retired gate must not fetch approval labels")
    monkeypatch.setattr(gate, "gh_json", forbidden)
    assert gate.main(["--enabled"]) == 0
    assert "retired" in capsys.readouterr().out.lower()
