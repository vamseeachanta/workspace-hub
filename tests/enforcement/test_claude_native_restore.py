"""Operator restore against disposable homes; no provider or fleet qualification."""
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts/agents"))
    from claude_runtime_transaction import Transaction
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    source = tmp_path / "source.md"
    source.write_text("Original canonical policy\n")
    (home / ".claude/CLAUDE.md").symlink_to(source)
    trial = tmp_path / "trial.md"
    trial.write_text("Trial policy\n")
    original = tmp_path / "original-journal"
    tx = Transaction(home, source, original)
    tx.capture()
    tx.begin(trial)
    tx.finalize()
    (home / ".claude/workspace-soul-verification.json").write_text('{"old":true}')
    return home, source, original, tmp_path / "restore-journal"


def restore_object(prepared):
    from claude_native_restore import Restore
    home, source, original, journal = prepared
    capture = original / "0001-captured.json"
    final = sorted(original.glob("*-finalized.json"))[-1]
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    return Restore(home, source, capture, final, journal, sha(source), sha(capture), sha(final))


def test_restore_allows_new_verification_and_preserves_unrelated_rules(prepared):
    from claude_runtime_transaction import Transaction
    home, source, original, journal = prepared
    rule = home / ".claude/rules/unrelated.md"
    rule.write_text("New authorized rule\n")
    before = (original / "legacy.link").lstat().st_ino
    result = restore_object(prepared).run()
    assert result["state"] == "LEGACY_RESTORED"
    assert (home / ".claude/CLAUDE.md").lstat().st_ino == before
    assert not (home / ".claude/rules/workspace-soul.md").exists()
    assert (journal / "native.link").is_symlink()
    assert (journal / "verification-receipt.json").is_file()
    assert rule.read_text() == "New authorized rule\n"
    Transaction(home, source, journal.parent / "new-pilot").capture()


@pytest.mark.parametrize("path", ["native", "parked", "occupied_legacy"])
def test_changed_loader_identity_blocks_before_writes(prepared, path):
    home, source, original, journal = prepared
    if path == "occupied_legacy":
        (home / ".claude/CLAUDE.md").write_text("User-owned content")
    else:
        target = home / ".claude/rules/workspace-soul.md" if path == "native" else original / "legacy.link"
        target.unlink()
        target.symlink_to(source)
    with pytest.raises(RuntimeError):
        restore_object(prepared).run()
    assert not journal.exists()


def test_new_source_revision_requires_explicit_current_digest(prepared):
    home, source, _, _ = prepared
    restore = restore_object(prepared)
    source.write_text("New reviewed canonical policy\n")
    with pytest.raises(RuntimeError, match="source"):
        restore.run()
    assert restore_object(prepared).run()["state"] == "LEGACY_RESTORED"
    assert (home / ".claude/CLAUDE.md").read_text() == "New reviewed canonical policy\n"


def test_failure_restores_native_and_preserves_original_journal(prepared, monkeypatch):
    home, source, original, _ = prepared
    restore = restore_object(prepared)
    actual = restore.move
    def fail_native(key, destination):
        if key == "native":
            raise OSError("Injected native parking failure")
        return actual(key, destination)
    monkeypatch.setattr(restore, "move", fail_native)
    result = restore.run()
    assert result["state"] == "NATIVE_RESTORED"
    assert (home / ".claude/rules/workspace-soul.md").resolve() == source
    assert (original / "legacy.link").is_symlink()
    assert not (home / ".claude/CLAUDE.md").exists()


def test_missing_receipt_does_not_prevent_operator_restore(prepared):
    home, _, _, _ = prepared
    (home / ".claude/workspace-soul-verification.json").unlink()
    assert restore_object(prepared).run()["state"] == "LEGACY_RESTORED"


def test_changed_reviewed_journal_is_rejected(prepared):
    _, _, original, journal = prepared
    restore = restore_object(prepared)
    (original / "0001-captured.json").write_text("{}")
    with pytest.raises(RuntimeError, match="journal"):
        restore.run()
    assert not journal.exists()
