"""Rollback ownership audit using disposable sentinels, never installed state.

Expected outcomes follow the started-action criterion in issue 3868. Bytes and
operation lists below are literal independent examples, not production outputs.
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def repair(monkeypatch):
    # The imported helper inserts its own dependency directory into sys.path.
    monkeypatch.syspath_prepend(str(ROOT / "scripts/skills"))
    return load("scripts/readiness/repair-sibling-sso-flow.py", "audit_repair")


def record(path):
    """Record identity plus bytes; equal bytes alone cannot prove preservation."""
    metadata = path.lstat()
    return (metadata.st_dev, metadata.st_ino, metadata.st_mode,
            metadata.st_mtime_ns, metadata.st_ctime_ns, path.read_bytes())


def test_whole_snapshot_restore_is_an_unsafe_negative_control(repair, tmp_path):
    """Hand trace: capture absent B; create B; restoring absent B removes B.

    This deliberately unsafe isolated call proves the fixture detects the defect
    described in issue 3868; the supported caller must filter the snapshot first.
    """
    sentinel = tmp_path / "unstarted"
    snapshot = repair.capture_owned_paths([sentinel])
    sentinel.write_bytes(b"concurrent sentinel\n")
    repair.restore_owned_paths(snapshot)
    assert not sentinel.exists()


@pytest.mark.parametrize("kind", ["file", "symlink", "directory"])
def test_refused_second_action_never_enters_restore(
    repair, monkeypatch, tmp_path, kind
):
    """Hand trace: start A; create foreign B; refuse B; restore only A.

    Expected restoration set is {A}. B and its child retain object identity and
    bytes; the remove spy also detects an otherwise invisible remove/recreate.
    """
    repo = tmp_path / "repo"
    first, second = repo / ".gemini/skills", repo / ".codex/skills"
    first.parent.mkdir(parents=True)
    second.parent.mkdir()
    first.symlink_to("original")
    monkeypatch.setattr(repair, "classify_native_root", lambda _repo: "absent")
    removed, restored = [], []
    original_remove, original_restore = repair.remove_path, repair.restore_owned_paths
    sentinel = second / "sentinel" if kind == "directory" else second
    snapshots = []

    def verify(*_args):
        if kind == "directory":
            second.mkdir()
        if kind == "symlink":
            target = tmp_path / "foreign"
            target.write_bytes(b"concurrent sentinel\n")
            second.symlink_to(target)
        else:
            sentinel.write_bytes(b"concurrent sentinel\n")
        snapshots.append((record(sentinel), second.lstat()))
        monkeypatch.setattr(repair, "classify_native_root", lambda _repo: "native")
        return {"status": "pass"}

    def remove(path):
        removed.append(path)
        original_remove(path)

    def restore(backups):
        restored.extend(backups)
        original_restore(backups)

    monkeypatch.setattr(repair, "verify_symlink", verify)
    monkeypatch.setattr(repair, "remove_path", remove)
    monkeypatch.setattr(repair, "restore_owned_paths", restore)
    actions = [{"kind": "rewrite_symlink", "path": str(path), "target": "replacement"}
               for path in (first, second)]
    assert repair._apply_repairable_actions("fixture", actions, repo) == 4
    assert first.readlink() == Path("original")
    assert restored == [str(first)]
    assert second not in removed and sentinel not in removed
    assert record(sentinel) == snapshots[0][0]
    assert second.lstat() == snapshots[0][1]


def test_middle_refusal_preserves_unstarted_tail(
    repair, monkeypatch, tmp_path, capsys
):
    """Acceptance trace for issue 3868: start A, refuse B, never start C.

    Independently enumerate recovery as [A]: only A passed validation and began
    mutation. Removal visits A for the original unlink and A for rollback.
    B and C retain inode, mode, modification/change timestamps and bytes.
    C is an instruction-pointer file in the disposable root only.
    """
    repo = tmp_path / "repo"
    first, second = repo / ".gemini/skills", repo / ".codex/skills"
    tail = repo / "AGENTS.md"
    first.parent.mkdir(parents=True)
    second.parent.mkdir()
    first.symlink_to("original")
    tail.write_bytes(b"Contract: ../AGENTS.md\n")
    before_tail = record(tail)
    verified, refused, removed, restored = [], {}, [], []
    original_remove, original_restore = repair.remove_path, repair.restore_owned_paths

    def verify(path, target):
        assert path == first
        assert path.readlink() == Path(target) == Path("replacement")
        verified.append(path)
        return {"status": "pass"}

    def classify(_repo):
        if not verified:
            return "absent"
        # Preflight has finished. Create B inside its next validation, directly
        # before native ownership makes that validation refuse the action.
        second.write_bytes(b"foreign middle sentinel\n")
        refused[second] = record(second)
        return "native"

    def remove(path):
        removed.append(path)
        original_remove(path)

    def restore(backups):
        restored.append(list(backups))
        original_restore(backups)

    monkeypatch.setattr(repair, "verify_symlink", verify)
    monkeypatch.setattr(repair, "classify_native_root", classify)
    monkeypatch.setattr(repair, "remove_path", remove)
    monkeypatch.setattr(repair, "restore_owned_paths", restore)
    actions = [{"kind": "rewrite_symlink", "path": str(path), "target": "replacement"}
               for path in (first, second)]
    actions.append({"kind": "rewrite_agents_pointer", "path": str(tail),
                    "from": "../AGENTS.md", "to": "../replacement/AGENTS.md"})

    assert repair._apply_repairable_actions("fixture", actions, repo) == 4

    assert "stale Codex action" in capsys.readouterr().err
    assert verified == [first]
    assert set(refused) == {second}
    assert restored == [[str(first)]]
    assert removed == [first, first]
    for untouched in (second, tail):
        assert untouched not in removed
        assert all(str(untouched) not in batch for batch in restored)
    assert first.readlink() == Path("original")
    assert record(second) == refused[second]
    assert record(tail) == before_tail


def test_partial_started_action_is_restored(repair, monkeypatch, tmp_path):
    """Hand trace: unlink A, fail creating its replacement; restore old A.

    This is a positive acceptance control: the write need not finish to own
    partial recovery; validation alone is not sufficient. A later, unstarted B
    must never be restored.
    """
    repo = tmp_path / "repo"
    first, second = repo / ".gemini/skills", repo / ".codex/skills"
    first.parent.mkdir(parents=True)
    first.symlink_to("original")
    monkeypatch.setattr(repair, "classify_native_root", lambda _repo: "absent")
    symlink_to = Path.symlink_to
    restored, failed_after_unlink = [], []
    original_restore = repair.restore_owned_paths

    def fail(path, target, *args, **kwargs):
        if target == "replacement":
            assert path == first
            assert not path.exists() and not path.is_symlink()
            failed_after_unlink.append(path)
            raise OSError("injected after unlink")
        return symlink_to(path, target, *args, **kwargs)

    def restore(backups):
        restored.extend(backups)
        original_restore(backups)

    monkeypatch.setattr(Path, "symlink_to", fail)
    monkeypatch.setattr(repair, "restore_owned_paths", restore)
    actions = [{"kind": "rewrite_symlink", "path": str(path), "target": "replacement"}
               for path in (first, second)]
    assert repair._apply_repairable_actions("fixture", actions, repo) == 4
    assert failed_after_unlink == [first]
    assert first.readlink() == Path("original")
    assert restored == [str(first)]
    assert not second.exists()


def test_preflight_refusal_does_not_restore(repair, monkeypatch, tmp_path):
    """Hand trace: B is already native; reject batch before A starts; writes=0."""
    repo = tmp_path / "repo"
    sentinel = repo / ".codex/skills"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_bytes(b"untouched\n")
    before = record(sentinel)
    monkeypatch.setattr(repair, "classify_native_root", lambda _repo: "native")
    restores = []
    monkeypatch.setattr(repair, "restore_owned_paths", restores.append)
    action = {"kind": "rewrite_symlink", "path": str(sentinel), "target": "new"}
    assert repair._apply_repairable_actions("fixture", [action], repo) == 4
    assert restores == []
    assert record(sentinel) == before


def test_runtime_refused_begin_preserves_foreign_native(monkeypatch, tmp_path):
    """Hand trace: capture, foreign native appears, begin refuses, rollback refuses.

    Neither refusal grants ownership of the native path or the legacy link.
    """
    module = load("scripts/agents/claude_runtime_transaction.py", "audit_runtime")
    user = tmp_path / "user"
    rules = user / ".claude/rules"
    rules.mkdir(parents=True)
    source = tmp_path / "source.md"
    source.write_bytes(b"runtime\n")
    legacy = user / ".claude/CLAUDE.md"
    legacy.symlink_to(source)
    tx = module.Transaction(user, source, tmp_path / "journal")
    # Seed the captured state from real records: capture() separately forbids
    # repository ancestors, while pytest scratch may have such an ancestor.
    # No production guard is patched; begin() and rollback() run real checks.
    tx.journal.mkdir()
    tx.parents = module.ancestors(rules)
    tx.sources = {str(source): module.file_record(source)}
    tx.prestate = {"legacy": module.link_record(legacy)}
    tx.phase = "CAPTURED"
    native = rules / "workspace-soul.md"
    native.write_bytes(b"foreign\n")
    before = record(native), legacy.lstat()
    removed = []
    unlink = Path.unlink

    def track(path, *args, **kwargs):
        removed.append(path)
        return unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", track)
    with pytest.raises(RuntimeError):
        tx.begin(source)
    with pytest.raises(RuntimeError):
        tx.rollback()
    assert native not in removed and legacy not in removed
    assert (record(native), legacy.lstat()) == before
    assert not tx.legacy_parked and tx.native_record is None


@pytest.mark.parametrize("state", ["staged", "replace-intent", "written"])
def test_materializer_rollback_candidates_require_started_state(
    monkeypatch, tmp_path, state
):
    """Hand calculation: candidate = (actual == postimage) AND started state.

    A staged payload whose bytes happen to match a later writer is not owned.
    The example uses digest equality only; no engineering constants apply.
    """
    monkeypatch.syspath_prepend(str(ROOT / "scripts/skills"))
    module = load("scripts/skills/materialize_profile.py", "audit_materializer")
    target, transaction = tmp_path / "target", tmp_path / "journal"
    target.mkdir()
    transaction.mkdir()
    sentinel = target / "sentinel"
    sentinel.write_bytes(b"postimage\n")
    before = record(sentinel)
    entry = {"target": "sentinel", "preimage": None,
             "sha256": module.fs.digest(b"postimage\n")}
    receipt = {"manifest": {"entries": [entry]}, "writes": [{"index": 0, "state": state}]}
    if state == "staged":
        with pytest.raises(ValueError, match="later writer"):
            module.rollback_candidates(receipt, target, transaction)
    else:
        assert module.rollback_candidates(receipt, target, transaction) == [
            (entry, sentinel, transaction / "0000.preimage")]
    assert record(sentinel) == before


@pytest.mark.parametrize("relative,function", [
    ("scripts/development/ai-workflow/auto-fix-loop.sh", "rollback_fix"),
    ("scripts/operations/baseline-validation/hooks/baseline-auto-fix.sh", "restore_backup"),
])
def test_backup_only_helpers_reproduce_unowned_overwrite(tmp_path, relative, function):
    """Hand trace: stale backup=old, unstarted destination=foreign; restore=old.

    These are characterization tests of unresolved findings, not acceptance of
    the behaviour. Only the exact helper function is executed, without its live
    orchestration, model calls, hooks, installations or repository operations.
    """
    import subprocess

    text = (ROOT / relative).read_text()
    declaration = function + "() {\n"
    body = declaration + text.split(declaration, 1)[1].split("\n}\n", 1)[0] + "\n}\n"
    destination = tmp_path / "destination"
    backup = tmp_path / "destination.bak"
    destination.write_bytes(b"foreign sentinel\n")
    backup.write_bytes(b"old snapshot\n")
    script = "log() { :; }; log_warn() { :; }; log_error() { :; };\n" + body
    script += '\n' + function + ' "$1" "$2"\n'
    subprocess.run(["bash", "-c", script, "audit", str(destination), str(backup)],
                   check=True, capture_output=True, text=True)
    assert destination.read_bytes() == b"old snapshot\n"


def test_materializer_refused_replace_still_selects_foreign_postimage(monkeypatch, tmp_path):
    """Hand trace: journal intent, foreign identical payload, replacement refuses.

    Expected observed defect: rollback_candidates still selects the foreign file.
    Intent plus digest equality does not establish that replacement began.
    """
    monkeypatch.syspath_prepend(str(ROOT / "scripts/skills"))
    module = load("scripts/skills/materialize_profile.py", "audit_refused_materializer")
    target, transaction = tmp_path / "target", tmp_path / "journal"
    target.mkdir()
    transaction.mkdir()
    (transaction / "0000.payload").write_bytes(b"postimage\n")
    entry = {"target": "sentinel", "preimage": None,
             "sha256": module.fs.digest(b"postimage\n")}
    receipt = {"manifest": {"entries": [entry]}, "directories": [],
               "writes": [{"index": 0, "state": "staged"}]}
    original = module.fs.replace_payload
    snapshots = []

    def concurrent_writer(staged, destination, expected):
        destination.write_bytes(b"postimage\n")
        snapshots.append(record(destination))
        return original(staged, destination, expected)

    monkeypatch.setattr(module.fs, "replace_payload", concurrent_writer)
    with pytest.raises(ValueError, match="changed immediately"):
        module.install(target, transaction, receipt)
    assert receipt["writes"][0]["state"] == "replace-intent"
    candidates = module.rollback_candidates(receipt, target, transaction)
    assert [destination for _, destination, _ in candidates] == [target / "sentinel"]
    assert record(target / "sentinel") == snapshots[0]
    assert (transaction / "0000.payload").read_bytes() == b"postimage\n"
