"""Synthetic filesystem receipts are not native-provider execution evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def runtime(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts/agents"))
    path = ROOT / "scripts/agents/claude_runtime_state.py"
    spec = importlib.util.spec_from_file_location("claude_runtime_state", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "provider_version", lambda cli: "fixture-version")
    repo, home = tmp_path / "repo", tmp_path / "user"
    source = repo / "config/agents/claude/SOUL.runtime.md"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"Synthetic fixture instructions\n")
    (home / ".claude/rules").mkdir(parents=True)
    return module, repo, home, source


def native_fixture(runtime, tmp_path):
    module, repo, home, source = runtime
    link = home / ".claude/rules/workspace-soul.md"
    link.symlink_to(source)
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "probe.json").write_bytes(b'{"synthetic":true}\n')
    cli = tmp_path / "fixture-provider.exe"
    cli.write_bytes(b"Synthetic provider binary")
    journal = tmp_path / "recovery-journal"
    journal.mkdir()
    (journal / "0001-captured.json").write_text('{"event":"captured"}')
    (journal / "0002-finalized.json").write_text('{"phase":"FINALIZED"}')
    receipt = {
        "schema_version": 1, "evidence_class": "live-provider",
        "home": str(home.resolve()), "source": str(source.resolve()),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "provider_version": "fixture-version", "observed_at": "2026-09-20T00:00:00Z",
        "provider_cli": str(cli.resolve()), "provider_sha256": module.digest(cli),
        "environment": module.provider_environment(),
        "checks": {key: "PASS" for key in module.REQUIRED_CHECKS},
        "evidence_root": str(evidence),
        "evidence": [{"path": "probe.json", "sha256": hashlib.sha256(
            (evidence / "probe.json").read_bytes()).hexdigest()}],
        "protected": __import__("claude_native_probe").protected_admission_state(home),
        "project_root": str(repo.resolve()),
        "project_protected": __import__("claude_native_probe").project_state(repo),
        "recovery": __import__("claude_native_restore").recovery_reference(journal),
    }
    state = home / ".claude/workspace-soul-verification.json"
    state.write_text(json.dumps(receipt))
    (evidence / "verification-receipt.json").write_bytes(state.read_bytes())
    return state, receipt


def test_absent_is_blocked_without_creating_files(runtime):
    module, repo, home, _ = runtime
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"
    assert not (home / ".claude/CLAUDE.md").exists()


def test_managed_legacy_is_preserved_and_not_native(runtime):
    module, repo, home, source = runtime
    link = home / ".claude/CLAUDE.md"
    link.symlink_to(source)
    before = link.lstat()
    assert module.inspect_runtime(repo, home)["state"] == "LEGACY"
    assert link.lstat() == before


def test_regular_file_is_not_accepted_as_managed(runtime):
    module, repo, home, source = runtime
    (home / ".claude/CLAUDE.md").write_bytes(source.read_bytes())
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"


def test_new_link_without_evidence_is_not_success(runtime):
    module, repo, home, source = runtime
    (home / ".claude/rules/workspace-soul.md").symlink_to(source)
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"


def test_bound_receipt_selects_native_fixture(runtime, tmp_path):
    module, repo, home, _ = runtime
    native_fixture(runtime, tmp_path)
    assert module.inspect_runtime(repo, home)["state"] == "NATIVE_VERIFIED"


def marketplace_registry(home):
    path = home / ".claude/plugins/known_marketplaces.json"
    path.parent.mkdir()
    data = {"fixture": {"source": {"source": "github", "repo": "example/fixture"},
                        "installLocation": "fixture", "lastUpdated": "2026-09-20T00:00:00Z"}}
    path.write_text(json.dumps(data))
    return path, data


def test_marketplace_clock_is_not_policy_but_full_preservation_sees_it(runtime, tmp_path):
    from claude_native_probe import protected_state
    module, repo, home, _ = runtime
    path, data = marketplace_registry(home)
    native_fixture(runtime, tmp_path)
    before = protected_state(home)
    data["fixture"]["lastUpdated"] = "2026-09-20T01:00:00Z"
    path.write_text(json.dumps(data))
    assert protected_state(home) != before
    assert module.inspect_runtime(repo, home)["state"] == "NATIVE_VERIFIED"


@pytest.mark.parametrize("change", ["valid", "unchanged", "missing", "tampered", "source", "location", "extra", "bad-clock", "linked", "escaping-link"])
def test_legacy_marketplace_reference_requires_exact_authenticated_baseline(runtime, tmp_path, change):
    module, repo, home, _ = runtime
    path, data = marketplace_registry(home)
    original = path.read_bytes()
    state, receipt = native_fixture(runtime, tmp_path)
    row = next(x for x in receipt["protected"] if x["path"] == "plugins/known_marketplaces.json")
    row.pop("digest_kind", None)
    row["sha256"] = hashlib.sha256(original).hexdigest()
    state.write_text(json.dumps(receipt))
    evidence = Path(receipt["evidence_root"])
    (evidence / "verification-receipt.json").write_bytes(state.read_bytes())
    if change in ("linked", "escaping-link"):
        target = (evidence if change == "linked" else tmp_path) / "baseline-target.json"
        target.write_bytes(original)
        (evidence / "known-marketplaces-baseline.json").symlink_to(target)
    elif change not in ("missing", "unchanged"):
        (evidence / "known-marketplaces-baseline.json").write_bytes(original if change != "tampered" else b"{}")
    if change != "unchanged":
        data["fixture"]["lastUpdated"] = "2026-09-20T01:00:00Z"
    if change == "source":
        data["fixture"]["source"]["repo"] = "example/changed"
    elif change == "location":
        data["fixture"]["installLocation"] = "changed"
    elif change == "extra":
        data["added"] = data["fixture"].copy()
    elif change == "bad-clock":
        data["fixture"]["lastUpdated"] = "invalid"
    path.write_text(json.dumps(data))
    expected = "NATIVE_VERIFIED" if change in ("valid", "unchanged") else "BLOCKED"
    assert module.inspect_runtime(repo, home)["state"] == expected


@pytest.mark.parametrize("change", ["source", "evidence", "config", "version", "home", "checks"])
def test_changed_proof_fails_closed(runtime, tmp_path, change, monkeypatch):
    module, repo, home, source = runtime
    state, receipt = native_fixture(runtime, tmp_path)
    if change == "source":
        source.write_bytes(b"changed")
    elif change == "evidence":
        (tmp_path / "evidence/probe.json").write_bytes(b"changed")
    elif change == "config":
        (home / ".claude/settings.json").write_text("{}")
    elif change == "version":
        monkeypatch.setattr(module, "provider_version", lambda cli: "changed-version")
    else:
        receipt[change] = "different" if change == "home" else {}
        state.write_text(json.dumps(receipt))
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"


def test_dual_verified_is_visible_but_not_single_source(runtime, tmp_path):
    module, repo, home, source = runtime
    native_fixture(runtime, tmp_path)
    (home / ".claude/CLAUDE.md").symlink_to(source)
    assert module.inspect_runtime(repo, home)["state"] == "DUAL_VERIFIED"


def test_evidence_traversal_rejected(runtime, tmp_path):
    module, repo, home, _ = runtime
    state, receipt = native_fixture(runtime, tmp_path)
    receipt["evidence"][0]["path"] = "../probe.json"
    state.write_text(json.dumps(receipt))
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"


def test_authored_rule_documents_staged_native_loader():
    rule = (ROOT / ".claude/rules/coding-style.md").read_text(encoding="utf-8")
    assert "rules/workspace-soul.md" in rule
    assert "LEGACY" in rule and "NATIVE_VERIFIED" in rule
    assert "Never replace that link with a regular file" not in rule


def test_environment_switch_invalidates_native_receipt(runtime, tmp_path, monkeypatch):
    module, repo, home, _ = runtime
    native_fixture(runtime, tmp_path)
    monkeypatch.setenv("CLAUDE_CODE_USE_BEDROCK", "changed-fixture")
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"


def test_provider_binary_replacement_invalidates_receipt(runtime, tmp_path):
    module, repo, home, _ = runtime
    _, receipt = native_fixture(runtime, tmp_path)
    Path(receipt["provider_cli"]).write_bytes(b"Different binary; same version")
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"


@pytest.mark.parametrize("change", ["missing", "different"])
def test_unpublished_or_changed_authority_is_blocked(runtime, tmp_path, change):
    module, repo, home, _ = runtime
    native_fixture(runtime, tmp_path)
    authority = tmp_path / "evidence/verification-receipt.json"
    if change == "missing":
        authority.unlink()
    else:
        authority.write_text("{}")
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"


def test_project_settings_change_invalidates_receipt(runtime, tmp_path):
    module, repo, home, _ = runtime
    native_fixture(runtime, tmp_path)
    settings = repo / ".claude/settings.json"
    settings.parent.mkdir()
    settings.write_text("{}")
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"


def test_credential_refresh_does_not_invalidate_loading_receipt(runtime, tmp_path):
    module, repo, home, _ = runtime
    credentials = home / ".claude/.credentials.json"
    credentials.write_text('{"fixture_token":"old"}')
    native_fixture(runtime, tmp_path)
    credentials.write_text('{"fixture_token":"refreshed"}')
    assert module.inspect_runtime(repo, home)["state"] == "NATIVE_VERIFIED"


def test_missing_recovery_evidence_invalidates_receipt(runtime, tmp_path):
    module, repo, home, _ = runtime
    native_fixture(runtime, tmp_path)
    (tmp_path / "recovery-journal/0001-captured.json").unlink()
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"


@pytest.mark.parametrize("tree", ["rules", "hooks"])
def test_new_protected_file_invalidates_receipt(runtime, tmp_path, tree):
    module, repo, home, _ = runtime
    native_fixture(runtime, tmp_path)
    path = home / ".claude" / tree / "new-file.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("Changed runtime discovery")
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"


def test_version_uses_explicit_binary_not_path(runtime, monkeypatch, tmp_path):
    module, _, _, _ = runtime
    calls = []
    def run(args, **kwargs):
        calls.append(args)
        return type("Result", (), {"stdout": "observed-version\n"})()
    monkeypatch.undo()
    monkeypatch.setattr(module.subprocess, "run", run)
    cli = tmp_path / "explicit provider.exe"
    assert module.provider_version(cli) == "observed-version"
    assert calls == [[str(cli), "--version"]]


@pytest.mark.parametrize("value", [[], {"schema_version": 1, "evidence_class": "live-provider", "checks": []}])
def test_malformed_receipt_is_explicitly_blocked(runtime, value):
    module, repo, home, source = runtime
    (home / ".claude/rules/workspace-soul.md").symlink_to(source)
    (home / ".claude/workspace-soul-verification.json").write_text(json.dumps(value))
    assert module.inspect_runtime(repo, home)["state"] == "BLOCKED"
