"""Pilot sequencing in disposable roots with an explicitly mocked provider."""
import hashlib
import importlib
import json
import re
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def source_import_path(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts/agents"))


@pytest.fixture
def pilot(tmp_path, monkeypatch):
    scripts = Path(__file__).resolve().parents[2] / "scripts/agents"
    monkeypatch.syspath_prepend(str(scripts))
    module = importlib.import_module("claude_native_pilot")
    monkeypatch.setattr(module, "provider_version", lambda cli: "synthetic-provider")
    monkeypatch.setattr(module, "check_auth", lambda cli: None)
    # The synthetic home is nested below the real user's home; no live discovery trial.
    monkeypatch.setattr(module, "suppressors", lambda cwd, home: None)
    repo, home = tmp_path / "repo", tmp_path / "home"
    source = repo / "config/agents/claude/SOUL.runtime.md"
    source.parent.mkdir(parents=True)
    (repo / ".git").mkdir()
    source.write_bytes(b"Edit tool freshness window: feedback_edit_tool_freshness_window_after_writes\n")
    (repo / "AGENTS.md").write_text("Readiness: docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md\n")
    cli = tmp_path / "fake"
    cli.write_text("synthetic executable")
    monkeypatch.chdir(tmp_path)
    (home / ".claude").mkdir(parents=True)
    (home / ".claude/CLAUDE.md").symlink_to(source)
    def fake_probe(cli, cwd, output, name, global_token, project_token, **kwargs):
        link = home / ".claude/rules/workspace-soul.md"
        text = link.read_text() if link.exists() else ""
        if kwargs.get("global_mode") == "canonical":
            actual_global = ("feedback_edit_tool_freshness_window_after_writes"
                             if "feedback_edit_tool_freshness_window_after_writes" in text else "NOT_LOADED")
        elif kwargs.get("global_mode") == "bounds":
            beginning = re.search(r"beginning_token is (\w+)", text).group(1)
            actual_global = beginning + "|" + re.search(r"global_token is (\w+)", text).group(1)
        else:
            match = re.search(r"global_token is (\w+)", text)
            actual_global = match.group(1) if match else "NOT_LOADED"
        project = (Path(cwd) / "AGENTS.md").read_text()
        if kwargs.get("project_mode") == "repository":
            actual_project = "docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md" if "MODEL_RELEASE_READINESS_CONTRACT.md" in project else "NOT_LOADED"
        elif kwargs.get("project_mode") == "lazy":
            nested = Path(cwd) / "nested/AGENTS.md"
            match = re.search(r"lazy_token is (\w+)", nested.read_text()) if nested.exists() else None
            actual_project = match.group(1) if match else "NOT_LOADED"
        else:
            actual_project = re.search(r"project_token is (\w+)", project).group(1)
        assert actual_global == global_token and actual_project == project_token
        module.write_json(output / (name + ".synthetic.json"), {"synthetic": True})
        return {"status": "PASS", "tokens": {"global_token": actual_global,
                                               "project_token": actual_project}}
    monkeypatch.setattr(module, "run_probe", fake_probe)
    monkeypatch.setattr(module, "guard_controls", lambda *args: {"allow": "PASS", "deny": "PASS"})
    module._real_lazy_trials = module.lazy_trials
    monkeypatch.setattr(module, "lazy_trials", lambda *args: {"positive": "PASS", "negative": "PASS"})
    return module, repo, home, source


def test_success_retires_only_legacy_after_rollback_drill(pilot, tmp_path):
    module, repo, home, source = pilot
    result = module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake",
                            hashlib.sha256(source.read_bytes()).hexdigest())
    assert result["state"] == "NATIVE_VERIFIED"
    assert not (home / ".claude/CLAUDE.md").exists()
    assert (home / ".claude/rules/workspace-soul.md").resolve() == source.resolve()
    assert (home / ".claude/workspace-soul-verification.json").exists()


def test_credential_change_fails_closed_then_fresh_named_attempt_preserves_history(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    credential = home / ".claude/.credentials.json"
    credential.write_text("synthetic original")
    original = module.run_probe
    def rotate(*args, **kwargs):
        result = original(*args, **kwargs)
        if args[3].startswith("positive"):
            credential.write_text("synthetic refreshed")
        return result
    monkeypatch.setattr(module, "run_probe", rotate)
    failed, journals = tmp_path / "failed-attempt", tmp_path / "journals"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="Protected state changed"):
        module.execute(repo, home, failed, journals, "fake", digest)
    assert (home / ".claude/CLAUDE.md").resolve() == source
    assert not (home / ".claude/rules/workspace-soul.md").exists()
    before = {str(p): p.read_bytes() for p in failed.rglob("*") if p.is_file()}
    monkeypatch.setattr(module, "run_probe", original)
    result = module.execute(repo, home, tmp_path / "fresh-attempt", journals, "fake", digest)
    assert result["state"] == "NATIVE_VERIFIED"
    assert before == {str(p): p.read_bytes() for p in failed.rglob("*") if p.is_file()}
    assert (journals / "failed-attempt-rollback").is_dir()


def test_failed_provider_trial_restores_managed_legacy(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    original = module.run_probe
    def fail_on_trial(cli, cwd, output, name, global_token, project_token, **kwargs):
        if name.startswith("positive"):
            raise ValueError("synthetic provider failure")
        return original(cli, cwd, output, name, global_token, project_token, **kwargs)
    monkeypatch.setattr(module, "run_probe", fail_on_trial)
    with pytest.raises(ValueError):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake",
                       hashlib.sha256(source.read_bytes()).hexdigest())
    assert (home / ".claude/CLAUDE.md").resolve() == source.resolve()
    assert not (home / ".claude/rules/workspace-soul.md").exists()
    assert not (home / ".claude/workspace-soul-verification.json").exists()


def test_unexpected_settings_change_blocks_and_preserves_it(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    original = module.run_probe
    def changed_probe(cli, cwd, output, name, global_token, project_token, **kwargs):
        if name.startswith("positive"):
            (home / ".claude/settings.json").write_text('{"concurrent":true}')
        return original(cli, cwd, output, name, global_token, project_token, **kwargs)
    monkeypatch.setattr(module, "run_probe", changed_probe)
    with pytest.raises(ValueError):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake",
                       hashlib.sha256(source.read_bytes()).hexdigest())
    assert (home / ".claude/settings.json").read_text() == '{"concurrent":true}'
    assert (home / ".claude/CLAUDE.md").is_symlink()


def test_final_positive_failure_prevents_receipt(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    original = module.run_probe
    def mismatch(*args, **kwargs):
        if args[3].startswith("final-positive"):
            return {"status": "PASS", "tokens": {"global_token": "NOT_LOADED", "project_token": args[5]}}
        return original(*args, **kwargs)
    monkeypatch.setattr(module, "run_probe", mismatch)
    with pytest.raises(ValueError):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", hashlib.sha256(source.read_bytes()).hexdigest())
    assert not (tmp_path / "evidence/verification-receipt.json").exists()
    assert (home / ".claude/CLAUDE.md").is_symlink()


def test_home_receipt_failure_never_leaves_positive(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    def fail(*args):
        raise OSError("receipt publication failed")
    monkeypatch.setattr(module, "publish_replica", fail)
    with pytest.raises(OSError):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", hashlib.sha256(source.read_bytes()).hexdigest())
    assert not (tmp_path / "evidence/verification-receipt.json").exists()
    assert (home / ".claude/CLAUDE.md").is_symlink()


def test_auth_failure_does_not_create_output(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    monkeypatch.setattr(module, "check_auth", lambda cli: (_ for _ in ()).throw(ValueError("no auth")))
    with pytest.raises(ValueError):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", hashlib.sha256(source.read_bytes()).hexdigest())
    assert not (tmp_path / "evidence").exists()


def test_worktree_git_file_refused_before_writes(pilot, tmp_path):
    module, repo, home, source = pilot
    (repo / ".git").rmdir()
    (repo / ".git").write_text("gitdir: external")
    with pytest.raises(ValueError, match="Persistent"):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", module.sha(source))
    assert not (tmp_path / "evidence").exists()


def test_late_suppressor_blocks_receipt(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    original = module.run_probe
    def changed(*args, **kwargs):
        result = original(*args, **kwargs)
        if args[3].startswith("final-positive"):
            (repo / "CLAUDE.local.md").write_text("concurrent suppression")
        return result
    def check(cwd, home):
        if (repo / "CLAUDE.local.md").exists():
            raise ValueError("suppressor")
    monkeypatch.setattr(module, "run_probe", changed)
    monkeypatch.setattr(module, "suppressors", check)
    with pytest.raises(ValueError, match="suppressor"):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", module.sha(source))
    assert not (tmp_path / "evidence/verification-receipt.json").exists()


def test_lazy_pair_restores_only_fixture_instructions(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    monkeypatch.setattr(module, "lazy_trials", module._real_lazy_trials)
    output = tmp_path / "evidence"
    module.execute(repo, home, output, tmp_path / "journals", "fake", module.sha(source))
    assert json.loads((output / "lazy-checks.json").read_text()) == {"positive": "PASS", "negative": "PASS"}
    assert (output / "fixture/nested/AGENTS.md").exists()
    assert not (output / "parked-lazy-AGENTS.md").exists()
    positive = json.loads((output / "lazy-positive-before.fixture.json").read_text())
    negative = json.loads((output / "lazy-negative-before.fixture.json").read_text())
    assert positive["instruction"]["record"] and positive["parked"]["record"] is None
    assert negative["instruction"]["record"] is None
    # POSIX rename can update ctime; identity/content and mtime remain bound.
    stable = lambda record: {key: value for key, value in record.items() if key != "ctime_ns"}
    assert stable(negative["parked"]["record"]) == stable(positive["instruction"]["record"])
    for phase in ("positive", "negative"):
        assert json.loads((output / ("lazy-" + phase + "-before.fixture.json")).read_text()) == json.loads(
            (output / ("lazy-" + phase + "-after.fixture.json")).read_text())
    restored = json.loads((output / "lazy-restored.fixture.json").read_text())
    assert restored["instruction"]["path"] == positive["instruction"]["path"]
    assert restored["parked"] == positive["parked"]
    assert stable(restored["instruction"]["record"]) == stable(positive["instruction"]["record"])


def test_authoritative_publication_failure_removes_replica(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    original = module.os.link
    def fail(source, destination, **kwargs):
        if Path(destination).name == "verification-receipt.json":
            raise OSError("authority publication failed")
        return original(source, destination, **kwargs)
    monkeypatch.setattr(module.os, "link", fail)
    with pytest.raises(OSError, match="authority"):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", module.sha(source))
    assert not (home / ".claude/workspace-soul-verification.json").exists()
    assert not (tmp_path / "evidence/verification-receipt.json").exists()
    assert (home / ".claude/CLAUDE.md").resolve() == source


def test_disabled_guard_controls_block_before_legacy_park(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    monkeypatch.setattr(module, "guard_controls", lambda *args: (_ for _ in ()).throw(ValueError("hook unavailable")))
    with pytest.raises(ValueError, match="hook"):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", module.sha(source))
    assert (home / ".claude/CLAUDE.md").is_symlink()
    assert not list((tmp_path / "journals").iterdir())


def test_project_settings_drift_blocks_publication(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    original = module.run_probe
    def changed(*args, **kwargs):
        result = original(*args, **kwargs)
        if args[3].startswith("final-restored"):
            (repo / ".claude").mkdir(exist_ok=True)
            (repo / ".claude/settings.json").write_text('{"concurrent":true}')
        return result
    monkeypatch.setattr(module, "run_probe", changed)
    with pytest.raises(ValueError, match="Project/ancestor"):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", module.sha(source))
    assert not (tmp_path / "evidence/verification-receipt.json").exists()
    assert (repo / ".claude/settings.json").exists()


def test_auth_override_refused_before_subprocess(monkeypatch):
    module = importlib.import_module("claude_native_pilot")
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://invalid.example")
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k: pytest.fail("unexpected auth call"))
    with pytest.raises(ValueError, match="override"):
        module.check_auth("fake")


def test_interruption_after_publication_invalidates_authority(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    original = module.publish_receipt
    def interrupt(*args):
        original(*args)
        raise KeyboardInterrupt("after publish")
    monkeypatch.setattr(module, "publish_receipt", interrupt)
    with pytest.raises(KeyboardInterrupt):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", module.sha(source))
    assert not (tmp_path / "evidence/verification-receipt.json").exists()
    assert (home / ".claude/CLAUDE.md").is_symlink()
    assert not (home / ".claude/workspace-soul-verification.json").exists()


def test_invalidation_failure_cannot_prevent_trial_rollback(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    original = module.run_probe
    def fail(*args, **kwargs):
        if args[3].startswith("positive"):
            raise ValueError("original trial failure")
        return original(*args, **kwargs)
    monkeypatch.setattr(module, "run_probe", fail)
    monkeypatch.setattr(module, "invalidate_authority", lambda *args: (_ for _ in ()).throw(OSError("invalidation failed")))
    with pytest.raises(ValueError, match="original trial"):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", module.sha(source))
    assert (home / ".claude/CLAUDE.md").is_symlink()
    assert not (home / ".claude/rules/workspace-soul.md").exists()
    marker = json.loads(next((tmp_path / "evidence").glob("BLOCKED-*.json")).read_text())
    assert marker["outcomes"]["invalidation"]["status"] == "ERROR"
    assert marker["outcomes"]["rollback"]["status"] == "PASS"


def test_failed_recovery_logging_preserves_original_exception(pilot, tmp_path, monkeypatch):
    module, repo, home, source = pilot
    original_probe, original_write = module.run_probe, module.write_json
    def fail(*args, **kwargs):
        if args[3].startswith("positive"):
            raise ValueError("original provider failure")
        return original_probe(*args, **kwargs)
    def failed_log(path, value):
        if path.name.startswith("BLOCKED") or path.name == "failure-rollback.json":
            raise OSError("logging unavailable")
        original_write(path, value)
    monkeypatch.setattr(module, "run_probe", fail)
    monkeypatch.setattr(module, "write_json", failed_log)
    monkeypatch.setattr(module, "invalidate_authority", lambda *args: (_ for _ in ()).throw(OSError("invalidation failed")))
    with pytest.raises(ValueError, match="original provider"):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", module.sha(source))
    assert (home / ".claude/CLAUDE.md").is_symlink()


def test_journal_collision_refused_before_output_creation(pilot, tmp_path):
    module, repo, home, source = pilot
    (tmp_path / "journals/evidence-apply").mkdir(parents=True)
    with pytest.raises(ValueError, match="journal"):
        module.execute(repo, home, tmp_path / "evidence", tmp_path / "journals", "fake", module.sha(source))
    assert not (tmp_path / "evidence").exists()


def test_final_canonical_pairs_have_two_processes_per_surface(pilot, tmp_path):
    module, repo, home, source = pilot
    output = tmp_path / "evidence"
    module.execute(repo, home, output, tmp_path / "journals", "fake", module.sha(source))
    rows = json.loads((output / "observed-checks.json").read_text())
    for phase in ("final-positive", "final-negative", "final-restored"):
        for case in ("root", "nested", "repository"):
            assert len([row for row in rows if row["phase"] == phase and row["case"] == case]) == 2


def test_receipt_binds_non_json_evidence(pilot, tmp_path):
    module, repo, home, source = pilot
    output = tmp_path / "evidence"
    module.execute(repo, home, output, tmp_path / "journals", "fake", module.sha(source))
    receipt = json.loads((output / "verification-receipt.json").read_text())
    names = {row["path"] for row in receipt["evidence"]}
    assert {"trial-runtime.md", "fixture/AGENTS.md", "fixture/nested/AGENTS.md"} <= names


def test_home_ancestor_suppressor_is_checked_from_other_cwd(tmp_path, monkeypatch):
    module = importlib.import_module("claude_native_pilot")
    home, cwd = tmp_path / "home", tmp_path / "other-drive-fixture"
    unexpected = home / "CLAUDE.md"
    monkeypatch.setattr(module.os.path, "lexists", lambda path: Path(path) == unexpected)
    with pytest.raises(ValueError, match="suppressor"):
        module.suppressors(cwd, home)


def test_single_final_observation_cannot_certify_pair(monkeypatch):
    module = importlib.import_module("claude_native_pilot")
    records = [{"phase": "final-positive", "case": case, "verdict": {"status": "PASS"},
                "protected": "PASS"} for case in ("root", "nested", "repository")]
    checks = module.derive_checks(records, {"phase": "ROLLED_BACK"}, {"phase": "FINALIZED"},
                                   {"positive": "PASS", "negative": "PASS"},
                                   {"allow": "PASS", "deny": "PASS"})
    assert checks["global_positive"] == "FAIL"


def test_both_recovery_errors_are_retained(tmp_path, monkeypatch):
    module = importlib.import_module("claude_native_pilot")
    class BrokenTransaction:
        phase = "TRIAL"
        def rollback(self):
            raise OSError("rollback drift")
    monkeypatch.setattr(module, "invalidate_authority", lambda *args: (_ for _ in ()).throw(ValueError("receipt drift")))
    (tmp_path / "BLOCKED.json").write_text("prior marker")
    module.recover_pilot(BrokenTransaction(), tmp_path, tmp_path, {}, ValueError("original"))
    record = json.loads(next(tmp_path.glob("BLOCKED-*.json")).read_text())
    assert record["outcomes"]["invalidation"]["reason"] == "receipt drift"
    assert record["outcomes"]["rollback"]["reason"] == "rollback drift"
    assert (tmp_path / "BLOCKED.json").read_text() == "prior marker"


def test_published_receipt_binds_exact_restore_journal(pilot, tmp_path):
    module, repo, home, source = pilot
    restore = importlib.import_module("claude_native_restore")
    output = tmp_path / "evidence"
    module.execute(repo, home, output, tmp_path / "journals", "fake", module.sha(source))
    receipt = json.loads((output / "verification-receipt.json").read_text())
    assert receipt["recovery"] == restore.recovery_reference(Path(receipt["readback"]["journal"]))
