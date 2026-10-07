"""Filesystem adversarial contracts; simulated Windows cases are named explicitly."""
import json
import os
from pathlib import Path
import stat
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/skills"))
import materialize_profile_fs as fs
import materialize_profile as materializer


@pytest.fixture
def tree(tmp_path):
    source, target, transaction = [tmp_path / name for name in ("source", "target", "transaction")]
    for path in (source, target, transaction):
        path.mkdir()
    return source, target, transaction


@pytest.mark.parametrize("relative", ["../outside", "/outside", "C:/outside", "a\\b", ""])
def test_payload_containment_rejects_invalid_paths(tree, relative):
    with pytest.raises(ValueError):
        fs.within(tree[1], relative)


def test_missing_descendants_allowed_without_creating_them(tree):
    target = tree[1]
    path = fs.within(target, ".agents/skills/new/SKILL.md")
    assert path == target / ".agents/skills/new/SKILL.md"
    assert list(target.iterdir()) == []


def test_transaction_rejects_source_and_target_overlap(tree):
    source, target, _ = tree
    for path in (source / "transactions/new", target / "transactions/new", source.parent):
        with pytest.raises(ValueError, match="overlap"):
            fs.validate_transaction(path, source, target)


def test_transaction_volume_mismatch_simulation(tree, monkeypatch):
    source, target, transaction = tree
    monkeypatch.setattr(fs, "volume", lambda path: 1 if path == target else 2)
    with pytest.raises(ValueError, match="volume"):
        fs.validate_transaction(transaction, source, target)


def test_real_hardlink_rejected_without_altering_original(tree):
    original = tree[0] / "original"
    original.write_bytes(b"preserve")
    link = tree[1] / "linked"
    try:
        os.link(original, link)
    except OSError as error:
        pytest.skip(f"Real hardlink unavailable: {error}")
    with pytest.raises(ValueError, match="hard-linked"):
        fs.preimage(link)
    assert original.read_bytes() == b"preserve"


def test_real_symlink_ancestor_rejected_without_traversal(tree):
    source, target, _ = tree
    link = target / "linked"
    try:
        link.symlink_to(source, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"Real directory symlink unavailable: {error}")
    with pytest.raises(ValueError, match="link|reparse"):
        fs.within(target, "linked/missing/SKILL.md")
    with pytest.raises(ValueError, match="link|reparse"):
        fs.walk_no_links(target)
    assert list(source.iterdir()) == []


@pytest.mark.parametrize("attributes,tag", [(0x400, 0), (0, 0xA0000003)])
def test_windows_reparse_stat_simulation_rejected(attributes, tag):
    info = SimpleNamespace(st_mode=stat.S_IFDIR, st_nlink=1,
                           st_file_attributes=attributes, st_reparse_tag=tag)
    with pytest.raises(ValueError, match="reparse"):
        fs.validate_stat(info)


def test_windows_missing_stat_evidence_simulation(monkeypatch):
    monkeypatch.setattr(fs, "os", SimpleNamespace(name="nt"))
    with pytest.raises(ValueError, match="unavailable"):
        fs.validate_stat(SimpleNamespace(st_mode=stat.S_IFDIR, st_nlink=1))


def test_replace_preserves_concurrent_destination_edit(tree):
    destination, staged = tree[1] / "SKILL.md", tree[2] / "0000.payload"
    destination.write_bytes(b"before")
    expected = fs.preimage(destination)
    staged.write_bytes(b"intended")
    destination.write_bytes(b"another writer")
    with pytest.raises(ValueError, match="changed"):
        fs.replace_payload(staged, destination, expected)
    assert destination.read_bytes() == b"another writer"
    assert staged.read_bytes() == b"intended"


def test_absent_preimage_does_not_overwrite_concurrent_creation(tree):
    destination, staged = tree[1] / "SKILL.md", tree[2] / "0000.payload"
    staged.write_bytes(b"intended")
    destination.write_bytes(b"foreign")
    with pytest.raises(ValueError, match="changed"):
        fs.replace_payload(staged, destination, None)
    assert destination.read_bytes() == b"foreign"


def test_mkdir_intent_precedes_creation_and_records_owned_dirs(tree, monkeypatch):
    _, target, transaction = tree
    receipt = {"directories": []}
    original = Path.mkdir

    def observed_mkdir(path, *args, **kwargs):
        journal = json.loads((transaction / "journal.json").read_bytes())
        assert journal["directories"][-1] == {"path": path.relative_to(target).as_posix(), "created": False}
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", observed_mkdir)
    fs.create_descendants(target / ".agents/skills/new", target, transaction, receipt)
    assert all(item["created"] for item in receipt["directories"])
    assert json.loads((transaction / "journal.json").read_bytes()) == receipt


def test_concurrent_mkdir_is_not_transaction_owned(tree, monkeypatch):
    _, target, transaction = tree
    receipt = {"directories": []}
    original = Path.mkdir

    def concurrent_mkdir(path, *args, **kwargs):
        original(path, *args, **kwargs)
        raise FileExistsError("Simulated intervening creator")

    monkeypatch.setattr(Path, "mkdir", concurrent_mkdir)
    fs.create_descendants(target / ".agents", target, transaction, receipt)
    assert receipt["directories"] == [{"path": ".agents", "created": False}]
    receipt["manifest"] = {"provider": "codex"}
    materializer.remove_owned_directories(receipt, target)
    assert (target / ".agents").is_dir()


def test_mkdir_failure_preserves_foreign_file_and_intent(tree, monkeypatch):
    _, target, transaction = tree
    receipt = {"directories": []}

    def concurrent_file(path, *args, **kwargs):
        path.write_bytes(b"foreign")
        raise FileExistsError("Simulated intervening file")

    monkeypatch.setattr(Path, "mkdir", concurrent_file)
    with pytest.raises(ValueError, match="not directory|non-directory"):
        fs.create_descendants(target / ".agents", target, transaction, receipt)
    assert (target / ".agents").read_bytes() == b"foreign"
    saved = json.loads((transaction / "journal.json").read_bytes())
    assert saved["directories"] == [{"path": ".agents", "created": False}]


def test_rollback_preserves_foreign_children_in_owned_directory(tree):
    _, target, transaction = tree
    receipt = {"directories": [], "manifest": {"provider": "codex"}}
    directory = target / ".agents/skills/new"
    fs.create_descendants(directory, target, transaction, receipt)
    foreign = directory / "foreign.txt"
    foreign.write_bytes(b"preserve")
    with pytest.raises((OSError, ValueError)):
        materializer.remove_owned_directories(receipt, target)
    assert foreign.read_bytes() == b"preserve"


def test_rollback_preserves_recreated_foreign_empty_directory(tree):
    _, target, transaction = tree
    receipt = {"directories": [], "manifest": {"provider": "codex"}}
    directory = target / ".agents/skills/new"
    fs.create_descendants(directory, target, transaction, receipt)
    for item in receipt["directories"]:
        item["path"] = Path(item["path"]).as_posix()
    directory.rename(directory.with_name("original-owned"))
    directory.mkdir()
    try:
        materializer.remove_owned_directories(receipt, target)
    except (ValueError, OSError):
        pass
    assert directory.is_dir(), "Rollback deleted another writer's replacement directory"


def test_owned_nested_directories_are_removable_on_current_platform(tree):
    _, target, transaction = tree
    receipt = {"directories": [], "manifest": {"provider": "codex"}}
    fs.create_descendants(target / ".agents/skills/new", target, transaction, receipt)
    materializer.remove_owned_directories(receipt, target)
    assert not (target / ".agents").exists()


def test_sharing_violation_injection_preserves_destination_and_staged(tree, monkeypatch):
    destination, staged = tree[1] / "SKILL.md", tree[2] / "0000.payload"
    destination.write_bytes(b"before")
    staged.write_bytes(b"after")

    def denied_replace(*args):
        raise PermissionError("Simulated Windows sharing violation")

    monkeypatch.setattr(fs.os, "replace", denied_replace)
    with pytest.raises(PermissionError):
        fs.replace_payload(staged, destination, fs.digest(b"before"))
    assert destination.read_bytes() == b"before"
    assert staged.read_bytes() == b"after"


def test_real_windows_junction_ancestor_rejected(tree):
    if os.name != "nt":
        pytest.skip("Real NTFS junction fixture requires Windows")
    import subprocess
    source, target, _ = tree
    junction = target / "junction"
    result = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(source)],
                            capture_output=True, text=True)
    if result.returncode:
        pytest.skip("Real NTFS junction creation unavailable: " + result.stderr.strip())
    with pytest.raises(ValueError, match="reparse"):
        fs.within(target, "junction/missing/SKILL.md")
    assert list(source.iterdir()) == []


# Reconciled worker integration cases; equivalent primitive cases above cover the other three.
from test_materialize_profile import setup, report, apply, module


def test_symlink_destination_rejected(setup):
    real = setup['target'].parent / 'real'; real.mkdir()
    (setup['target'] / '.agents').mkdir()
    try:
        (setup['target'] / '.agents/skills').symlink_to(real, target_is_directory=True)
    except OSError:
        pytest.skip('host does not permit real symbolic-link fixture')
    with pytest.raises(ValueError): report(setup)


def test_hardlink_payload_rejected(setup):
    path = setup['source'] / '.claude/skills/research/wiki-context/SKILL.md'
    os.link(path, setup['source'] / 'hardlink')
    with pytest.raises(ValueError): report(setup)


def test_failure_between_replacements_has_recoverable_journal(setup, monkeypatch):
    import materialize_profile_fs as fs
    original = fs.replace_payload; count = 0
    def interrupted(*args):
        nonlocal count
        count += 1
        if count == 2: raise OSError('synthetic sharing violation')
        return original(*args)
    monkeypatch.setattr(fs, 'replace_payload', interrupted)
    with pytest.raises(OSError): apply(setup, report(setup))
    receipt = json.loads((setup['transaction'] / 'journal.json').read_text())
    assert receipt['status'] == 'interrupted'
    monkeypatch.setattr(fs, 'replace_payload', original)
    module().rollback(receipt, setup['source'], setup['target'], setup['transaction'])
    assert not list(setup['target'].rglob('SKILL.md'))


def test_ancestor_swap_before_replacement_stops(setup, monkeypatch):
    import materialize_profile_fs as fs
    original = fs.replace_payload
    def concurrent(staged, destination, expected):
        destination.write_bytes(b'concurrent bytes')
        return original(staged, destination, expected)
    monkeypatch.setattr(fs, 'replace_payload', concurrent)
    with pytest.raises(ValueError): apply(setup, report(setup))
    receipt = json.loads((setup['transaction'] / 'journal.json').read_text())
    assert receipt['status'] == 'interrupted'
    assert any(p.read_bytes() == b'concurrent bytes' for p in setup['target'].rglob('SKILL.md'))
