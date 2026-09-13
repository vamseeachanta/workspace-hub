"""Operation decisions remain advisory across providers and untrusted inputs."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/governance"))
import workflow_decision as wd


def request():
    return {
        "schema_version": "1", "provider": "codex", "operation_kind": "edit",
        "scope": {"repository_id": "fixture/repo", "task_id": "issue:1",
                  "operation_id": "fix-typo", "bounded": True},
        "changed_paths": ["docs/example.md"], "effects": ["local-reversible"],
        "authorization_reference": "session:user-message:1",
    }


def test_routine_authority_is_only_a_reference():
    result = wd.assess(request())
    assert result == {
        "risk_class": "routine-reversible",
        "authorization_assessment": "unverified-reference",
        "action_boundary": "conditional-routine", "metric_advice": "not-requested",
        "reuse_assessment": "not-requested",
        "reason_codes": ["ROUTINE_CONDITIONAL", "UNVERIFIED_AUTHORITY"],
    }


def test_provider_identity_has_no_authority():
    other = request()
    other["provider"] = "claude"
    assert wd.assess(other) == wd.assess(request())


def test_missing_authority_needs_context():
    value = request()
    value.pop("authorization_reference")
    assert wd.assess(value)["action_boundary"] == "needs-context"


@pytest.mark.parametrize("path", ["docs/standards/HARD-STOP-POLICY.md",
    ".claude/rules/example.md", "config/agents/SHARED_SOUL.md",
    ".github/CODEOWNERS", ".git/config", "scripts/review/cross-review.sh",
    "config/security.yaml", "docs/architecture/authorization.md",
    "docs/engineering/design-basis.md", "scripts/workflow/session_governor.py"])
def test_protected_paths_override_routine_effect(path):
    value = request()
    value["changed_paths"] = [path]
    result = wd.assess(value)
    assert result["risk_class"] == "substantial"
    assert result["action_boundary"] == "approval-required"


@pytest.mark.parametrize("effect", ["publication", "destruction", "access-change",
                                    "engineering-basis-change"])
def test_consequential_effects_require_approval(effect):
    value = request()
    value["effects"].append(effect)
    result = wd.assess(value)
    assert result["risk_class"] == "consequential"
    assert result["action_boundary"] == "approval-required"


@pytest.mark.parametrize("mutation", [
    {"effects": ["new-unknown-effect"]}, {"effects": []},
    {"operation_kind": "unknown"}, {"scope": {}},
    {"changed_paths": ["../outside.md"]}, {"approved": True},
    {"schema_version": "2"}, {"effects": "local-reversible"},
    {"operation_kind": []}, {"operation_kind": {}},
])
def test_ambiguous_or_malformed_request_fails_closed(mutation):
    value = request()
    value.update(mutation)
    assert wd.assess(value)["action_boundary"] == "needs-context"


def test_read_only_requires_consistent_effects():
    value = request()
    value.update(operation_kind="inspect", changed_paths=[], effects=["read-only"])
    value.pop("authorization_reference")
    assert wd.assess(value)["action_boundary"] == "assessment-only"
    value["effects"] = ["local-reversible"]
    assert wd.assess(value)["action_boundary"] == "needs-context"


def test_metrics_do_not_revoke_or_grant_authority():
    value = request()
    value["metrics"] = {"raw": {}, "sample_count": 0}
    result = wd.assess(value)
    assert result["metric_advice"] == "ineligible-shadow"
    assert result["action_boundary"] == "conditional-routine"
    value["metrics"] = {"raw": {}, "sample_count": "invalid"}
    assert wd.assess(value)["metric_advice"] == "unavailable"


def test_receipt_identity_bound_to_current_operation(monkeypatch):
    value = request()
    value["reuse"] = {"previous": {}, "current": {"key": {
        "repository_id": "another/repo", "task_id": "issue:1",
        "operation_id": "fix-typo", "changed_paths": ["docs/example.md"]}},
        "as_of": "2026-09-12T12:00:00Z", "source_ids": [],
        "evidence_artifacts": {}}
    monkeypatch.setattr(wd, "compare_receipts", lambda *a, **k: {
        "reuse_assessment": "candidate-pending-live-validation",
        "reason_codes": ["MUTABLE_VALIDATION_REQUIRED"]})
    assert wd.assess(value, workflow_schema={})["reuse_assessment"] == "invalid"


def test_resource_reuse_requires_explicit_intended_operation():
    value = request()
    value["reuse"] = {"previous": {}, "current": {"key": {
        "repository_id": "fixture/repo", "task_id": "issue:1",
        "operation_id": "fix-typo", "changed_paths": ["docs/example.md"]},
        "resources": [{"descriptor": {}}]}, "as_of": "2026-09-12T12:00:00Z",
        "source_ids": [], "evidence_artifacts": {}}
    result = wd.assess(value, workflow_schema={})
    assert result["reuse_assessment"] == "needs-context"
    assert "MISSING_CONTEXT" in result["reason_codes"]


@pytest.mark.parametrize("path", ["tools/unknown.sh", "Dockerfile", ".env", "weird/path.bin"])
def test_unclassified_path_cannot_be_declared_routine(path):
    value = request()
    value["changed_paths"] = [path]
    assert wd.assess(value)["action_boundary"] == "needs-context"


@pytest.mark.parametrize("path", ["tools/indexer.py", "web/index.js", "index.html",
    "scripts/readme_generator.py", "readme_sync.ts", "docs/build.py"])
def test_documentation_names_do_not_imply_documentation_content(path):
    value = request()
    value["changed_paths"] = [path]
    assert wd.assess(value)["action_boundary"] == "needs-context"


@pytest.mark.parametrize("path", ["docs/plans/issue-3615.html", "deploy/production.yaml",
    "docker-compose.yml", "infra/stack.json", ".vscode/settings.json", "helm/values.yaml"])
def test_plans_and_deployment_configuration_are_protected(path):
    value = request()
    value["changed_paths"] = [path]
    assert wd.assess(value)["action_boundary"] == "approval-required"


@pytest.mark.parametrize("path", [".github/dependabot.yml", "pyproject.toml", "package.json"])
def test_build_and_dependency_control_requires_approval(path):
    value = request()
    value["changed_paths"] = [path]
    assert wd.assess(value)["action_boundary"] == "approval-required"


def test_successful_metrics_still_do_not_authenticate():
    value = request()
    value["metrics"] = {"sample_count": 30, "raw": {
        "adversarial_review_approve_rate": 1, "post_merge_revert_rate": 0,
        "completeness_gate_pass_rate": 1, "reproduction_compliance_rate": 1,
        "plan_revision_rounds": 1}}
    result = wd.assess(value)
    assert result["metric_advice"] == "eligible-shadow"
    assert result["authorization_assessment"] == "unverified-reference"


def test_execution_and_optional_assessments_with_invalid_context():
    value = request()
    value["operation_kind"] = "execute"
    assert wd.assess(value)["action_boundary"] == "needs-context"
    value.update(scope={}, metrics={}, reuse={})
    result = wd.assess(value)
    assert result["metric_advice"] == "unavailable"
    assert result["reuse_assessment"] == "needs-context"


@pytest.mark.parametrize("raw", ['{"schema_version":"1","schema_version":"1"}',
    '{"value":NaN}', '{', '[' * 100 + ']' * 100, 'x' * 1048577],
    ids=["duplicate", "nonfinite", "truncated", "deep", "oversized"])
def test_cli_malformed_input_is_deterministic(raw):
    result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/governance/workflow_decision.py")],
                            input=raw, capture_output=True, text=True)
    assert result.returncode == 2
    assert json.loads(result.stdout)["action_boundary"] == "needs-context"
    assert "Traceback" not in result.stderr


def test_cli_valid_input_and_no_persistence(tmp_path):
    value = request()
    result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/governance/workflow_decision.py")],
                            input=json.dumps(value), capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0
    assert json.loads(result.stdout) == wd.assess(value)
    assert list(tmp_path.iterdir()) == []


def test_assess_does_not_execute_or_write(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("assessment attempted a side effect")
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    import socket
    monkeypatch.setattr(socket, "socket", forbidden)
    assert wd.assess(request())["action_boundary"] == "conditional-routine"
