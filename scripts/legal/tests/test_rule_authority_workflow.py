"""Phase A3 bootstrap, workflow, CLI, and owner-preview contracts."""

from __future__ import annotations

import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
LEGAL = ROOT / "scripts" / "legal"
sys.path.insert(0, str(LEGAL))

CALLER = ROOT / ".github/workflows/legal-rule-authority-gate.yml"
REUSABLE = ROOT / ".github/workflows/legal-rule-authority-reusable.yml"
REGISTRY = ROOT / "config/legal-rule-registry.json"
POLICY = ROOT / "config/legal-rule-authority-policy.json"
PREVIEW = ROOT / "docs/plans/evidence/2026-07-14-issue-3522-phase-a-owner-preview.json"
DOC = ROOT / ".claude/docs/legal-rule-authority.md"
CLIENT_DOC = ROOT / ".claude/docs/client-pii-prevention.md"
CLI = LEGAL / "manage_rule_authority.py"
OID = re.compile(r"[0-9a-f]{40}")


def _yaml(path: Path) -> dict:
    return yaml.load(path.read_text(), Loader=yaml.BaseLoader)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args], cwd=ROOT, text=True,
        capture_output=True, check=False,
    )


def _anchor(slot: str, head: str | None = None) -> dict:
    return {
        "authority_revision": "12345678-1234-4234-9234-123456789abc",
        "expected_head_oid": head, "generation": 1, "manifest_mac": "a" * 64,
        "schema_id": "legal-rule-active-anchor-v1", "slot": slot,
        "tool_sha": "b" * 40,
    }


def test_validate_public_is_deterministic_and_synthetic() -> None:
    first = _run_cli("validate-public", "--registry", str(REGISTRY), "--policy", str(POLICY))
    second = _run_cli("validate-public", "--registry", str(REGISTRY), "--policy", str(POLICY))
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout
    assert first.stderr == second.stderr == ""
    result = json.loads(first.stdout)
    assert result == {
        "authority_revision": "12345678-1234-4234-9234-123456789abc",
        "command": "validate-public", "generation": 1, "rc": 0, "verdict": "valid",
    }
    assert json.loads(REGISTRY.read_text())["rules"] == [{
        "match_mode": "exact-bytes", "rule_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "severity": "block", "target": "both",
    }]


def test_validate_public_failure_withholds_paths_and_fragments(tmp_path: Path) -> None:
    fragment = "synthetic-private-fragment"
    invalid = tmp_path / fragment
    invalid.write_text(fragment)
    result = _run_cli("validate-public", "--registry", str(invalid), "--policy", str(POLICY))
    assert result.returncode == 2
    assert result.stdout == ""
    assert json.loads(result.stderr) == {
        "command": "validate-public", "message": "invalid public authority", "rc": 2,
    }
    assert fragment not in result.stderr


def test_caller_has_constant_fork_boundary_and_pinned_reusable() -> None:
    raw, workflow = CALLER.read_text(), _yaml(CALLER)
    assert set(workflow["on"]) == {"pull_request_target"}
    assert "secrets." not in raw and "secrets: inherit" not in raw
    assert "actions/checkout" not in raw
    fork = workflow["jobs"]["fork-boundary"]
    assert fork["name"] == "strict-scan"
    assert "head.repo.full_name != github.repository" in fork["if"]
    runs = "\n".join(step.get("run", "") for step in fork["steps"])
    assert runs.strip() == "echo 'owner review required' >&2\nexit 1"
    trusted = workflow["jobs"]["strict-scan"]
    assert "head.repo.full_name == github.repository" in trusted["if"]
    match = re.search(r"legal-rule-authority-reusable\.yml@([0-9a-f]{40})", trusted["uses"])
    assert match and _pin_contains_tools(match.group(1))


def _pin_contains_tools(sha: str) -> bool:
    paths = [
        ".github/workflows/legal-rule-authority-reusable.yml",
        "scripts/legal/manage_rule_authority.py",
    ]
    return all(subprocess.run(
        ["git", "cat-file", "-e", f"{sha}:{path}"], cwd=ROOT, check=False,
        capture_output=True,
    ).returncode == 0 for path in paths)


def test_reusable_owns_environment_and_uses_trusted_context_files() -> None:
    raw, workflow = REUSABLE.read_text(), _yaml(REUSABLE)
    assert set(workflow["on"]) == {"workflow_call"}
    assert workflow["permissions"] == {"contents": "read"}
    job = workflow["jobs"]["strict-scan"]
    assert job["name"] == "strict-scan"
    assert job["environment"] == "legal-rule-authority"
    assert "secrets." not in raw and "pull_request.head.sha }}" not in raw
    assert "persist-credentials: false" in raw
    assert "PYTHONNOUSERSITE: '1'" in raw
    action_pins = re.findall(r"uses: [^\s@]+@([^\s]+)", raw)
    assert action_pins and all(OID.fullmatch(pin) for pin in action_pins)
    assert "validate-workflow-context" in raw and "validate-public" in raw


def test_fork_oracle_stops_before_authority_loader() -> None:
    ci = importlib.import_module("rule_authority.ci_contract")
    calls = []
    result = ci.classify_pull_request(
        repository="owner/repo", head_repository="fork/repo",
        base_ref="refs/heads/main", head_sha="a" * 40,
        authority_loader=lambda: calls.append("loaded"),
    )
    assert result == {"message": "owner review required", "rc": 1}
    assert calls == []


def test_trusted_event_ref_and_sha_are_closed() -> None:
    ci = importlib.import_module("rule_authority.ci_contract")
    request = {
        "event_name": "pull_request_target", "repository": "owner/repo",
        "head_repository": "owner/repo", "base_ref": "refs/heads/main",
        "head_sha": "a" * 40, "tool_sha": "b" * 40,
    }
    assert ci.validate_workflow_context(request)["head_sha"] == "a" * 40
    for key, value in (("event_name", "pull_request"), ("base_ref", "main"),
                       ("head_sha", "HEAD"), ("tool_sha", "b" * 39)):
        with pytest.raises(ValueError):
            ci.validate_workflow_context({**request, key: value})


def test_dual_slot_exact_head_selection_and_rollback_preview() -> None:
    ci = importlib.import_module("rule_authority.ci_contract")
    head = "c" * 40
    current, pending = _anchor("current"), _anchor("pending", head)
    assert ci.select_slot("d" * 40, current, pending) == current
    assert ci.select_slot(head, current, pending) == pending
    preview = ci.cutover_preview(
        current, pending, expected_head=head, expected_tree="e" * 40,
        observed_current=current,
    )
    assert preview["compare_and_swap"] is True
    assert preview["rollback"] == "restore-current-if-and-only-if-promoted-identity-matches"
    with pytest.raises(ValueError):
        ci.cutover_preview(current, pending, expected_head="d" * 40,
                           expected_tree="e" * 40, observed_current=current)


def test_readback_parser_matches_exact_owner_preview_without_network() -> None:
    protection = importlib.import_module("rule_authority.protection_preview")
    preview = json.loads(PREVIEW.read_text())
    fixture = {
        "environment": preview["environment"],
        "ruleset": preview["ruleset"],
        "codeowners": preview["codeowners"],
    }
    normalized = protection.parse_readback_fixture(fixture)
    assert normalized == protection.expected_readback(preview)
    assert normalized["ruleset"]["required_check"] == {
        "context": "legal-rule-authority / strict-scan", "integration_id": 15368,
    }
    assert normalized["ruleset"]["bypass_actors"] == []
    assert normalized["environment"]["reviewers"] == ["vamseeachanta"]


def test_docs_freeze_owner_preview_and_rollback_without_live_mutation() -> None:
    doc, client_doc = DOC.read_text(), CLIENT_DOC.read_text()
    preview = json.loads(PREVIEW.read_text())
    for heading in ("Phase A bootstrap", "Fork boundary", "Owner transaction preview",
                    "Dual-slot cutover and rollback", "Explicitly not performed"):
        assert f"## {heading}" in doc
    assert preview["schema_id"] == "legal-rule-phase-a-owner-preview-v1"
    assert preview["owner"] == "vamseeachanta"
    assert preview["target_ref"] == "refs/heads/main"
    assert preview["cutover"]["rollback"]["requires_owner_approval"] is True
    assert "No environment, CODEOWNERS, ruleset, or secret was mutated" in doc
    assert "legacy client-PII gate remains active" in client_doc
