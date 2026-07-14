"""Consolidated regressions from the Phase A T3 adversarial review."""
# AUTHORITY_FORENSIC_DEFINITION: synthetic detector vectors only.

from __future__ import annotations

import copy
import importlib
import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[3]
LEGAL = ROOT / "scripts/legal"
sys.path.insert(0, str(LEGAL))

from rule_authority import audit_github  # noqa: E402
from rule_authority.codec import canonical_bytes, decode_document  # noqa: E402
from rule_authority.structural import SensitiveArtifacts, scan_blobs  # noqa: E402

CLI = LEGAL / "manage_rule_authority.py"
PREVIEW = ROOT / "docs/plans/evidence/2026-07-14-issue-3522-phase-a-owner-preview.json"
POLICY_SCHEMA = ROOT / "schemas/legal-rule-policy.schema.json"
PATTERN = b"synthetic-block-value"
SENSITIVE = SensitiveArtifacts(b"k" * 32, (PATTERN,), (), frozenset())


def _cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args], cwd=ROOT, text=True,
        capture_output=True, check=False,
    )


@pytest.mark.parametrize("args", [
    ("hostile-command-private-fragment",),
    ("validate-public", "--hostile-private-fragment"),
    ("validate-public", "--registry", "hostile-private-fragment"),
    ("validate-public", "---hostile-private-fragment"),
])
def test_argparse_failures_use_fixed_withholding_envelope(args: tuple[str, ...]) -> None:
    result = _cli(*args)
    assert result.returncode == 2 and result.stdout == ""
    assert json.loads(result.stderr) == {
        "command": "usage", "message": "invalid command usage", "rc": 2,
    }
    assert "hostile-private-fragment" not in result.stderr
    assert "usage:" not in result.stderr


@pytest.mark.parametrize("command,args", [
    ("seal", ("--registry", "x", "--policy", "x", "--map", "x", "--key-file", "x",
              "--current-anchor", "x", "--ledger", "x", "--out-dir", "x")),
    ("verify", ("--registry", "x", "--policy", "x", "--map", "x", "--manifest", "x",
                "--key-file", "x", "--anchor", "x", "--ledger", "x")),
    ("audit-tree", ("--repo", "x", "--commit", "a" * 40, "--required-ref",
                    "refs/heads/main", "--authority-dir", "x", "--out-dir", "x")),
    ("audit-history", ("--remote-url-env", "SYNTHETIC_REMOTE", "--github-repo",
                       "owner/repo", "--authority-dir", "x", "--mirror-dir", "x",
                       "--out-dir", "x", "--github-token-env", "SYNTHETIC_TOKEN")),
    ("cleanup-incomplete", ("--parent", "x", "--transaction-id",
                            "12345678-1234-4234-9234-123456789abc")),
    ("promote", ("--current-envelope-env", "CURRENT", "--pending-envelope-env", "PENDING",
                 "--expected-head", "a" * 40, "--expected-tree", "b" * 40,
                 "--preview", "x")),
])
def test_frozen_cli_surface_runs_synthetic_operations(
        command: str, args: tuple[str, ...]) -> None:
    result = _cli(command, *args)
    assert result.returncode in {0, 1, 2, 3, 4}
    output = result.stdout or result.stderr
    assert json.loads(output)["command"] == command
    assert "Traceback" not in output and " x" not in output


def _anchor(slot: str, generation: int, revision: str, manifest: str,
            tool_sha: str, head: str | None = None) -> dict:
    return {
        "authority_revision": revision, "expected_head_oid": head,
        "generation": generation, "manifest_mac": manifest,
        "schema_id": "-".join(("legal", "rule", "active", "anchor", "v1")),
        "slot": slot, "tool_sha": tool_sha,
    }


def test_dual_slot_identity_cas_tree_and_rollback_guards() -> None:
    ci = importlib.import_module("rule_authority.ci_contract")
    head, tree = "c" * 40, "d" * 40
    current = _anchor("current", 4, "12345678-1234-4234-9234-123456789abc",
                      "a" * 64, "e" * 40)
    pending = _anchor("pending", 5, "22345678-1234-4234-9234-123456789abc",
                      "b" * 64, ci.APPROVED_TOOL_SHA, head)
    assert ci.select_slot(head, current, pending) == pending
    preview = ci.cutover_preview(
        current, pending, expected_head=head, expected_tree=tree,
        observed_head=head, observed_tree=tree,
        observed_current=current, observed_pending=pending,
    )
    assert ci.rollback_preview(current, pending, pending) == current
    assert preview["observed_tree"] == tree
    mutations = [
        {**pending, "generation": 4}, {**pending, "generation": 6},
        {**pending, "authority_revision": current["authority_revision"]},
        {**pending, "manifest_mac": current["manifest_mac"]},
        {**pending, "tool_sha": current["tool_sha"]},
    ]
    for invalid in mutations:
        with pytest.raises(ValueError):
            ci.select_slot(head, current, invalid)
    with pytest.raises(ValueError):
        ci.cutover_preview(current, pending, expected_head=head, expected_tree=tree,
                           observed_head=head, observed_tree="f" * 40,
                           observed_current=current, observed_pending=pending)
    with pytest.raises(ValueError):
        ci.rollback_preview(current, pending, {**pending, "manifest_mac": "f" * 64})


@pytest.mark.parametrize("length", [40, 64])
def test_workflow_and_slot_accept_full_git_oid_widths(length: int) -> None:
    ci = importlib.import_module("rule_authority.ci_contract")
    request = {
        "base_ref": "refs/heads/main", "event_name": "pull_request_target",
        "head_repository": ci.APPROVED_REPOSITORY, "head_sha": "a" * length,
        "repository": ci.APPROVED_REPOSITORY,
    }
    assert ci.validate_workflow_context(request)["head_sha"] == "a" * length


def test_owner_readback_rejects_every_security_leaf_mutation() -> None:
    protection = importlib.import_module("rule_authority.protection_preview")
    preview = json.loads(PREVIEW.read_text())
    fixture = {name: copy.deepcopy(preview[name])
               for name in ("codeowners", "environment", "ruleset")}
    mutations = [
        ("environment", "name", "wrong"), ("environment", "prevent_self_review", False),
        ("environment", "reviewers", ["attacker"]), ("ruleset", "enforcement", "disabled"),
        ("ruleset", "bypass_actors", ["attacker"]), ("ruleset", "conditions", {}),
        ("ruleset", "block_deletions", False),
        ("ruleset", "block_non_fast_forward", False),
        ("ruleset", "pull_request", {}), ("codeowners", "owners", ["@attacker"]),
    ]
    assert protection.parse_readback_fixture(fixture, preview) == fixture
    for section, name, value in mutations:
        changed = copy.deepcopy(fixture)
        changed[section][name] = value
        with pytest.raises(ValueError):
            protection.parse_readback_fixture(changed, preview)
    assert ".github/CODEOWNERS" in preview["codeowners"]["paths"]


def test_complete_tracked_authority_surface_self_scans() -> None:
    patterns = [
        "schemas/legal-rule-*", "config/legal-rule-*", "scripts/legal/manage_rule_authority.py",
        "scripts/legal/rule_authority/*.py", "scripts/legal/tests/test_rule_authority_*.py",
        ".github/workflows/legal-rule-authority-*.yml", ".claude/docs/legal-rule-authority.md",
        ".claude/docs/client-pii-prevention.md", "docs/plans/*issue-3522*",
        "docs/plans/evidence/*issue-3522*",
    ]
    tracked = set(subprocess.check_output(
        ["git", "ls-files", "--", *patterns], cwd=ROOT, text=True
    ).splitlines())
    changed = set(subprocess.check_output(
        ["git", "diff", "--name-only", "6c6fb6401..HEAD"], cwd=ROOT, text=True
    ).splitlines())
    assert changed <= tracked
    blobs = {path: (ROOT / path).read_bytes() for path in tracked}
    assert scan_blobs(blobs, SensitiveArtifacts(b"", (), (), frozenset())) == []


def _zip(name: str, payload: bytes) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(name, payload)
    return output.getvalue()


def test_nested_zip_expanded_bytes_are_scanned() -> None:
    raw = _zip("inner.zip", _zip("secret.bin", PATTERN))
    result = audit_github.scan_zip(
        raw, SENSITIVE, max_entries=10, max_compressed_bytes=10_000,
        max_expanded_bytes=10_000, max_ratio=100, max_depth=4,
    )
    assert b"inner.zip!secret.bin" in result.private_findings


@pytest.mark.parametrize("prefix,valid", [
    ("ok/", True), ("ok/\n/", False), ("ok/\x7f/", False),
    ("ok/../", False), ("unicodé/", False),
])
def test_printable_prefix_runtime_matches_schema(prefix: str, valid: bool) -> None:
    value = {
        "authority_revision": "12345678-1234-4234-9234-123456789abc",
        "forensic_prefixes": [prefix], "generation": 1,
        "limits": {"max_blob_bytes": 1, "max_entries": 1,
                   "max_findings": 1, "max_request_bytes": 1},
        "schema_id": "legal-rule-policy-v1",
    }
    schema = json.loads(POLICY_SCHEMA.read_text())
    schema_valid = not list(jsonschema.Draft202012Validator(schema).iter_errors(value))
    try:
        decode_document("policy", canonical_bytes(value))
        runtime_valid = True
    except ValueError:
        runtime_valid = False
    assert runtime_valid == schema_valid == valid


def test_reusable_has_fixed_tool_identity_and_pinned_uv_runtime() -> None:
    ci = importlib.import_module("rule_authority.ci_contract")
    caller = (ROOT / ".github/workflows/legal-rule-authority-gate.yml").read_text()
    reusable = (ROOT / ".github/workflows/legal-rule-authority-reusable.yml").read_text()
    pin = re.search(r"reusable\.yml@([0-9a-f]{40})", caller).group(1)
    assert f"ref: {ci.APPROVED_TOOL_SHA}" in reusable
    subprocess.run(["git", "cat-file", "-e", f"{pin}:.github/workflows/legal-rule-authority-reusable.yml"],
                   cwd=ROOT, check=True)
    subprocess.run(["git", "cat-file", "-e", f"{ci.APPROVED_TOOL_SHA}:scripts/legal/manage_rule_authority.py"],
                   cwd=ROOT, check=True)
    assert "tool_sha:" not in caller and "tool_sha:" not in reusable
    assert re.search(r"astral-sh/setup-uv@[0-9a-f]{40}", reusable)
    assert "uv run --no-project python" in reusable and "python3 " not in reusable
    assert ci.APPROVED_REPOSITORY == "vamseeachanta/workspace-hub"
