"""Recovery examples use literal byte equality, not computed materializer results.

Basis: issue 3858 recovery contract and the existing PAYLOADS boundary in
materialize_profile_schema.py. No engineering coefficients or limits apply.
"""
import importlib
import json
import subprocess

import pytest
from test_materialize_profile import apply, module, report, write
from test_materialize_profile import setup as materializer_setup

fs = importlib.import_module("materialize_profile_fs")


@pytest.fixture(name="setup")
def recovery_setup(tmp_path):
    return materializer_setup.__wrapped__(tmp_path)


def rollback(s, receipt):
    return module().rollback(receipt, s["source"], s["target"], s["transaction"])


def test_legacy_pending_evidence_does_not_block_journal(tmp_path):
    """Input partial JSON stays unchanged; the newly saved receipt is authoritative."""
    pending = tmp_path / "journal.pending"
    pending.write_bytes(b'{"partial":')
    receipt = {"status": "rollback-intent"}
    fs.save_journal(tmp_path, receipt)
    assert pending.read_bytes() == b'{"partial":'
    assert json.loads((tmp_path / "journal.json").read_bytes()) == receipt


def test_interrupted_journal_write_can_be_retried(tmp_path, monkeypatch):
    """A failed replace leaves its staged bytes; a retry preserves and bypasses them."""
    fs.save_journal(tmp_path, {"status": "applying"})
    original = fs.os.replace

    def interrupted(*args):
        raise OSError("injected interruption")

    monkeypatch.setattr(fs.os, "replace", interrupted)
    with pytest.raises(OSError):
        fs.save_journal(tmp_path, {"status": "interrupted"})
    residue = {p: p.read_bytes() for p in tmp_path.iterdir() if p.name != "journal.json"}
    assert residue
    assert json.loads((tmp_path / "journal.json").read_bytes())["status"] == "applying"
    monkeypatch.setattr(fs.os, "replace", original)
    fs.save_journal(tmp_path, {"status": "rolled-back"})
    assert all(p.read_bytes() == raw for p, raw in residue.items())
    assert json.loads((tmp_path / "journal.json").read_bytes())["status"] == "rolled-back"


def test_repeated_rollback_preserves_staging_and_backup_evidence(setup, monkeypatch):
    """Hand result: old bytes replace new bytes once; retry restores the remaining file.

    Two preimages are literal valid skill bytes. An interrupted replacement leaves
    rollback staging behind. Recovery must neither overwrite that residue nor use
    the legacy fixed-name file, whose intentionally unrelated bytes stay intact.
    """
    manifest = report(setup)
    old = b"---\nname: wiki-context\n---\noriginal\n"
    path = setup["target"] / ".agents/skills/research/wiki-context/SKILL.md"
    write(path, old)
    second = setup["target"] / manifest["entries"][0]["target"]
    second_old = b"---\nname: ecosystem-data-sources\n---\noriginal\n"
    write(second, second_old)
    receipt = apply(setup, report(setup))
    transaction = setup["transaction"]
    legacy = transaction / "rollback-0000.payload"
    legacy.write_bytes(b"unrelated residue")
    pending = transaction / "journal.pending"
    pending.write_bytes(b"partial journal")
    backups = {p: p.read_bytes() for p in transaction.glob("*.preimage")}
    original = fs.replace_payload
    count = 0

    def interrupted(staged, destination, expected):
        nonlocal count
        count += 1
        if count == 2:
            raise OSError("injected rollback interruption")
        return original(staged, destination, expected)

    monkeypatch.setattr(fs, "replace_payload", interrupted)
    with pytest.raises(OSError, match="interruption"):
        rollback(setup, receipt)
    residue = {p: p.read_bytes() for p in transaction.glob("rollback-*.payload")}
    assert len(residue) > 1
    saved = module().load_json(transaction / "journal.json")
    monkeypatch.setattr(fs, "replace_payload", original)
    assert rollback(setup, saved)["status"] == "rolled-back"
    assert path.read_bytes() == old
    assert second.read_bytes() == second_old
    assert all(p.read_bytes() == raw for p, raw in (backups | residue).items())
    assert pending.read_bytes() == b"partial journal"
    assert rollback(setup, saved)["status"] == "rolled-back"


def test_rollback_rechecks_backup_bytes_after_candidate_scan(setup, monkeypatch):
    """A changed backup must never supply restored bytes, even after preflight."""
    path = setup["target"] / ".agents/skills/research/wiki-context/SKILL.md"
    write(path, b"---\nname: wiki-context\n---\noriginal")
    receipt = apply(setup, report(setup))
    installed = path.read_bytes()
    original = module().rollback_candidates

    def tampered(*args):
        candidates = original(*args)
        for entry, _, backup in candidates:
            if entry["preimage"] is not None:
                backup.write_bytes(b"changed after candidate scan")
        return candidates

    monkeypatch.setattr(module(), "rollback_candidates", tampered)
    with pytest.raises(ValueError, match="backup"):
        rollback(setup, receipt)
    assert path.read_bytes() == installed


def test_mixed_apply_preserves_identical_entry_identity(setup):
    """One matching entry plus absent entries must retain matching bytes/inode/mtime."""
    manifest = report(setup)
    entry = manifest["entries"][0]
    path = setup["target"] / entry["target"]
    raw = (setup["source"] / entry["source"]).read_bytes()
    write(path, raw)
    before = path.stat()
    receipt = apply(setup, report(setup))
    after = path.stat()
    assert path.read_bytes() == raw
    assert (after.st_ino, after.st_mtime_ns) == (before.st_ino, before.st_mtime_ns)
    assert all(item["index"] != 0 for item in receipt["writes"])
    rollback(setup, receipt)
    assert path.read_bytes() == raw


@pytest.mark.parametrize("config_kind", ["global", "system"])
def test_controlled_git_config_is_excluded(setup, monkeypatch, config_kind):
    """A real config supplies a marker; production reads must exclude that file.

    The control invocation must see the marker, while the isolated Git reader
    must not. Report must retain the supplied revision and config bytes.
    """
    config = setup["source"].parent / (config_kind + ".gitconfig")
    raw = b"[foundation]\n\ttestmarker = injected-config\n"
    config.write_bytes(raw)
    monkeypatch.setenv("GIT_CONFIG_" + config_kind.upper(), str(config))
    monkeypatch.delenv("GIT_CONFIG_NOSYSTEM", raising=False)
    schema = importlib.import_module("materialize_profile_schema")
    control_env = {k: v for k, v in schema.os.environ.items()
                   if not k.upper().startswith("GIT_")}
    control_env["GIT_CONFIG_" + config_kind.upper()] = str(config)
    control = subprocess.run(["git", "-C", str(setup["source"]), "config", "--get", "foundation.testmarker"],
                             env=control_env, capture_output=True, check=True, text=True)
    assert control.stdout.strip() == "injected-config"
    isolated = schema.git_read(setup["source"], "config", "--get", "foundation.testmarker")
    assert isolated.returncode == 1 and isolated.stdout == b""
    assert report(setup)["source_revision"] == setup["revision"]
    assert config.read_bytes() == raw


def test_partial_journal_staging_is_retained_on_retry(tmp_path, monkeypatch):
    """A flush failure after writing bytes must leave evidence and permit a new save."""
    original = fs.os.fsync

    def interrupted(_descriptor):
        raise OSError("injected flush failure")

    monkeypatch.setattr(fs.os, "fsync", interrupted)
    with pytest.raises(OSError, match="flush failure"):
        fs.save_journal(tmp_path, {"status": "interrupted"})
    residue = {p: p.read_bytes() for p in tmp_path.iterdir()}
    assert residue and not (tmp_path / "journal.json").exists()
    monkeypatch.setattr(fs.os, "fsync", original)
    fs.save_journal(tmp_path, {"status": "rollback-intent"})
    assert all(p.read_bytes() == raw for p, raw in residue.items())
    assert json.loads((tmp_path / "journal.json").read_bytes())["status"] == "rollback-intent"


def test_exclusive_staging_collision_preserves_existing_bytes(tmp_path, monkeypatch):
    """Even identical proposed names must fail exclusive creation, never overwrite."""
    token = fs.uuid.uuid4()
    monkeypatch.setattr(fs.uuid, "uuid4", lambda: token)
    staged = fs.stage_attempt(tmp_path, "rollback", b"first attempt")
    with pytest.raises(FileExistsError):
        fs.stage_attempt(tmp_path, "rollback", b"second attempt")
    assert staged.read_bytes() == b"first attempt"


def test_apply_journal_interruption_keeps_replace_intent_recoverable(setup, monkeypatch):
    """Crash after replacement leaves new bytes; replace-intent permits guarded undo."""
    original = fs.save_journal
    interrupted = False

    def crash(transaction, receipt):
        nonlocal interrupted
        if not interrupted and any(item["state"] == "written" for item in receipt["writes"]):
            interrupted = True
            raise KeyboardInterrupt("injected process interruption")
        return original(transaction, receipt)

    monkeypatch.setattr(fs, "save_journal", crash)
    with pytest.raises(KeyboardInterrupt):
        apply(setup, report(setup))
    receipt = module().load_json(setup["transaction"] / "journal.json")
    assert any(item["state"] == "replace-intent" for item in receipt["writes"])
    monkeypatch.setattr(fs, "save_journal", original)
    assert rollback(setup, receipt)["status"] == "rolled-back"
    assert not list(setup["target"].rglob("SKILL.md"))


def test_pending_residue_cannot_override_later_writer_guard(setup):
    """Untrusted residue is retained; changed destination bytes prevent rollback."""
    receipt = apply(setup, report(setup))
    entry = receipt["manifest"]["entries"][0]
    destination = setup["target"] / entry["target"]
    destination.write_bytes(b"later writer")
    pending = setup["transaction"] / "journal.pending"
    pending.write_bytes(b"untrusted")
    before = (setup["transaction"] / "journal.json").read_bytes()
    with pytest.raises(ValueError, match="later writer"):
        rollback(setup, receipt)
    assert destination.read_bytes() == b"later writer"
    assert pending.read_bytes() == b"untrusted"
    assert (setup["transaction"] / "journal.json").read_bytes() == before
