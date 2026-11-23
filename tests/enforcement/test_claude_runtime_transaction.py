"""Filesystem transactions against disposable homes only."""
import importlib.util
import os
import hashlib
from pathlib import Path

import pytest


MODULE = Path(__file__).parents[2] / "scripts/agents/claude_runtime_transaction.py"


def load():
    spec = importlib.util.spec_from_file_location("transaction", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Transaction


@pytest.fixture
def fixture(tmp_path):
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    source = tmp_path / "source.md"
    source.write_text("canonical runtime\n")
    old_source = tmp_path / "old-source.md"
    old_source.write_bytes(source.read_bytes())
    legacy = home / ".claude/CLAUDE.md"
    legacy.symlink_to(old_source)
    trial = tmp_path / "trial.md"
    trial.write_text("trial canaries\n")
    return home, source, tmp_path / "journal", legacy, trial


def test_round_trip_and_repeat_readback(fixture):
    home, source, journal, legacy, trial = fixture
    tx = load()(home, source, journal)
    before = tx.capture()
    tx.begin(trial)
    native = home / ".claude/rules/workspace-soul.md"
    assert native.resolve() == trial
    assert not legacy.exists()
    tx.park_native()
    assert not os.path.lexists(native)
    tx.restore_native()
    assert native.resolve() == trial
    tx.finalize()
    assert native.resolve() == source
    assert tx.readback() == tx.readback()
    assert (journal / "legacy.link").is_symlink()
    tx.rollback()
    assert legacy.resolve() == Path(before["legacy"]["resolved"])
    assert not os.path.lexists(native)
    assert not (home / ".claude/rules").exists()


def test_relative_legacy_target_is_rejected_before_parking(fixture):
    home, source, journal, legacy, _ = fixture
    old = legacy.resolve()
    legacy.unlink()
    legacy.symlink_to(os.path.relpath(old, legacy.parent))
    with pytest.raises(RuntimeError, match="absolute"):
        load()(home, source, journal).capture()
    assert legacy.resolve() == old
    assert not journal.exists()


def test_pending_journal_blocks_second_apply(fixture):
    home, source, journal, _, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    tx.begin(trial)
    with pytest.raises(RuntimeError):
        load()(home, source, journal).capture()


@pytest.mark.parametrize("kind", ["file", "other_link", "missing"])
def test_rollback_refuses_concurrent_native_change(fixture, kind):
    home, source, journal, legacy, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    tx.begin(trial)
    native = home / ".claude/rules/workspace-soul.md"
    native.unlink()
    if kind == "file":
        native.write_text("concurrent")
    elif kind == "other_link":
        native.symlink_to(source)
    with pytest.raises(RuntimeError):
        tx.rollback()
    assert not os.path.lexists(legacy)
    assert (journal / "legacy.link").is_symlink()


def test_symlink_creation_failure_can_restore_legacy(fixture, monkeypatch):
    home, source, journal, legacy, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    def fail(*args, **kwargs):
        raise OSError("injected unavailable symlink")
    monkeypatch.setattr(os, "symlink", fail)
    with pytest.raises(OSError):
        tx.begin(trial)
    tx.rollback()
    assert legacy.is_symlink()


@pytest.mark.parametrize("kind", ["handwritten", "missing", "different_bytes"])
def test_capture_refuses_unknown_legacy(fixture, kind):
    home, source, journal, legacy, _ = fixture
    if kind == "different_bytes":
        source.write_text("different")
    else:
        legacy.unlink()
        if kind == "handwritten":
            legacy.write_text("handwritten")
    with pytest.raises(RuntimeError):
        load()(home, source, journal).capture()
    assert not journal.exists()


def test_source_and_target_drift_block_transition(fixture):
    home, source, journal, _, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    source.write_text("changed source")
    with pytest.raises(RuntimeError):
        tx.begin(trial)


def test_parent_replacement_blocks_rollback(fixture):
    home, source, journal, legacy, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    tx.begin(trial)
    rules = home / ".claude/rules"
    rules.rename(home / ".claude/other")
    rules.mkdir()
    with pytest.raises(RuntimeError):
        tx.rollback()
    assert not os.path.lexists(legacy)


def test_existing_rules_preserved_and_collision_refused(fixture):
    home, source, journal, _, trial = fixture
    rules = home / ".claude/rules"
    rules.mkdir()
    other = rules / "unrelated.md"
    other.write_text("preserve")
    tx = load()(home, source, journal)
    tx.capture()
    tx.begin(trial)
    tx.rollback()
    assert other.read_text() == "preserve"
    (rules / "workspace-soul.md").write_text("collision")
    with pytest.raises(RuntimeError):
        load()(home, source, journal.parent / "other-journal").capture()


def test_journal_inside_discovery_root_refused(fixture):
    home, source, _, _, _ = fixture
    with pytest.raises(RuntimeError):
        load()(home, source, home / ".claude/journal").capture()


def test_private_same_volume_home_journal_allowed(fixture):
    home, source, _, legacy, trial = fixture
    parent = home / "AppData/Local/workspace-hub/transactions"
    parent.mkdir(parents=True)
    tx = load()(home, source, parent / "pilot")
    tx.capture()
    tx.begin(trial)
    tx.rollback()
    assert legacy.is_symlink()


def test_rules_created_after_capture_refuses_before_parking(fixture):
    home, source, journal, legacy, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    (home / ".claude/rules").mkdir()
    with pytest.raises(RuntimeError):
        tx.begin(trial)
    assert legacy.is_symlink()


def test_parked_native_drift_blocks_negative_readback(fixture):
    home, source, journal, _, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    tx.begin(trial)
    tx.park_native()
    (journal / "native.link").unlink()
    with pytest.raises(RuntimeError):
        tx.readback()


def test_finalized_native_can_park_and_restore_to_finalized(fixture):
    home, source, journal, _, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    tx.begin(trial)
    tx.finalize()
    native = home / ".claude/rules/workspace-soul.md"

    tx.park_native()
    assert tx.readback()["phase"] == "NEGATIVE"
    assert not os.path.lexists(native)
    tx.restore_native()

    assert tx.readback()["phase"] == "FINALIZED"
    assert native.resolve() == source


def test_finalized_park_drift_refuses_restore(fixture):
    home, source, journal, legacy, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    tx.begin(trial)
    tx.finalize()
    tx.park_native()
    parked = journal / "native.link"
    parked.unlink()
    parked.symlink_to(trial)

    with pytest.raises(RuntimeError, match="parked native drift"):
        tx.restore_native()

    assert not os.path.lexists(legacy)
    assert not os.path.lexists(home / ".claude/rules/workspace-soul.md")


def test_finalized_negative_can_rollback_to_legacy(fixture):
    home, source, journal, legacy, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    tx.begin(trial)
    tx.finalize()
    tx.park_native()

    result = tx.rollback()

    assert result["phase"] == "ROLLED_BACK"
    assert legacy.is_symlink()
    assert not os.path.lexists(home / ".claude/rules/workspace-soul.md")
    assert (journal / "native.link").is_symlink()


def test_concurrent_legacy_collision_never_overwritten(fixture):
    home, source, journal, legacy, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    tx.begin(trial)
    legacy.write_text("another writer")
    with pytest.raises(RuntimeError):
        tx.rollback()
    assert legacy.read_text() == "another writer"


def test_finalization_link_failure_restores_legacy(fixture, monkeypatch):
    home, source, journal, legacy, trial = fixture
    tx = load()(home, source, journal)
    tx.capture()
    tx.begin(trial)
    def fail(*args, **kwargs):
        raise OSError("final source link failure")
    monkeypatch.setattr(os, "symlink", fail)
    with pytest.raises(OSError):
        tx.finalize()
    tx.rollback()
    assert legacy.is_symlink()


def test_explicit_legacy_pin_allows_reviewed_new_source(fixture):
    home, source, journal, legacy, trial = fixture
    old_bytes = legacy.read_bytes()
    pin = hashlib.sha256(old_bytes).hexdigest()
    source.write_text("reviewed revised canonical runtime\n")
    tx = load()(home, source, journal, expected_legacy_sha256=pin)
    before = tx.capture()
    tx.begin(trial)
    tx.finalize()
    assert before["legacy"]["target"]["sha256"] == pin
    assert before["source_record"]["sha256"] != pin
    tx.rollback()
    assert legacy.read_bytes() == old_bytes


@pytest.mark.parametrize("pin", ["0" * 64, "not-a-sha256", "A" * 64])
def test_wrong_or_invalid_explicit_legacy_pin_blocks(fixture, pin):
    home, source, journal, legacy, _ = fixture
    with pytest.raises(RuntimeError):
        load()(home, source, journal, expected_legacy_sha256=pin).capture()
    assert legacy.is_symlink()
    assert not journal.exists()
