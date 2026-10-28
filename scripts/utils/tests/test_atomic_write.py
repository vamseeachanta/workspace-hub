"""Isolated transaction tests; all destinations are synthetic temporary files.

Byte expectations use the UTF-8 construction in RFC 3629, section 3. Digest
expectations use hashlib independently of the helper, on literal fixture bytes.
Permission expectations use the symbolic POSIX permission flags in stat.
"""

import hashlib
import os
import stat
from pathlib import Path

import pytest

from scripts.utils import atomic_write as atomic


BEFORE = b"original"
ATTEMPTED = b"replacement"
MODE = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP


def digest(data):
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def target(tmp_path):
    path = tmp_path / "state.yaml"
    path.write_bytes(BEFORE)
    path.chmod(MODE)
    return path


def assert_only_target(target, expected=BEFORE):
    assert target.read_bytes() == expected
    assert set(target.parent.iterdir()) == {target}


def test_encoding_failure_preserves_existing_bytes(target):
    with pytest.raises(UnicodeEncodeError):
        atomic.atomic_write_utf8(target, "\udcff")
    assert_only_target(target)
    assert stat.S_IMODE(target.stat().st_mode) == MODE


def test_unicode_round_trip(target):
    # RFC 3629 section 3, manually mapping U+2192, U+00E9 and U+4E2D.
    expected = b"\xe2\x86\x92 caf\xc3\xa9 \xe4\xb8\xad"
    receipt = atomic.atomic_write_utf8(target, "→ café 中")
    assert_only_target(target, expected)
    assert target.read_text(encoding="utf-8") == "→ café 中"
    assert receipt == {
        "path": target.as_posix(),
        "before_sha": digest(BEFORE),
        "attempted_sha": digest(expected),
        "written_sha": digest(expected),
        "restored_sha": None,
        "recovery": "not_needed",
    }


def test_mode_preserved(target):
    atomic.atomic_write_utf8(target, ATTEMPTED.decode("ascii"))
    assert_only_target(target, ATTEMPTED)
    assert stat.S_IMODE(target.stat().st_mode) == MODE


def test_replace_failure_preserves_target(target, monkeypatch):
    def refuse_replace(source, destination):
        raise PermissionError("injected replacement failure")

    monkeypatch.setattr(atomic.os, "replace", refuse_replace)
    with pytest.raises(atomic.AtomicWriteError) as failure:
        atomic.atomic_write_utf8(target, ATTEMPTED.decode("ascii"))
    assert isinstance(failure.value.__cause__, PermissionError)
    assert failure.value.receipt["before_sha"] == digest(BEFORE)
    assert failure.value.receipt["attempted_sha"] == digest(ATTEMPTED)
    assert failure.value.receipt["written_sha"] is None
    assert failure.value.before_bytes == BEFORE
    assert failure.value.before_mode == MODE
    assert_only_target(target)


def test_concurrent_change_refused(target, monkeypatch):
    real_stage = atomic._stage
    concurrent = b"other writer"

    def stage_and_change(*args):
        staged = real_stage(*args)
        target.write_bytes(concurrent)
        return staged

    monkeypatch.setattr(atomic, "_stage", stage_and_change)
    with pytest.raises(atomic.ConcurrentChangeError):
        atomic.atomic_write_utf8(target, "replacement")
    assert_only_target(target, concurrent)


def test_readback_failure_receipt(target, monkeypatch):
    real_snapshot = atomic._snapshot
    installed = False
    failed = False
    real_replace = atomic.os.replace

    def replace(source, destination):
        nonlocal installed
        real_replace(source, destination)
        installed = True

    def fail_readback(path):
        nonlocal failed
        if Path(path) == target and installed and not failed:
            failed = True
            raise OSError("injected readback failure")
        return real_snapshot(path)

    monkeypatch.setattr(atomic.os, "replace", replace)
    monkeypatch.setattr(atomic, "_snapshot", fail_readback)
    with pytest.raises(atomic.AtomicWriteError) as failure:
        atomic.atomic_write_utf8(target, "replacement")
    receipt = failure.value.receipt
    assert receipt["before_sha"] == digest(BEFORE)
    assert receipt["attempted_sha"] == digest(ATTEMPTED)
    assert receipt["written_sha"] is None
    assert receipt["restored_sha"] == digest(BEFORE)
    assert receipt["recovery"] == "restored"
    assert failure.value.before_bytes == BEFORE
    assert_only_target(target)
    assert stat.S_IMODE(target.stat().st_mode) == MODE


def test_readback_mismatch_preserves_unrelated_bytes(target, monkeypatch):
    real_replace = atomic.os.replace
    concurrent = b"unrelated concurrent bytes"

    def replace_and_change(source, destination):
        real_replace(source, destination)
        target.write_bytes(concurrent)

    monkeypatch.setattr(atomic.os, "replace", replace_and_change)
    with pytest.raises(atomic.AtomicWriteError) as failure:
        atomic.atomic_write_utf8(target, "replacement")
    assert failure.value.receipt["restored_sha"] is None
    assert failure.value.receipt["recovery"] == "refused"
    assert failure.value.before_bytes == BEFORE
    assert_only_target(target, concurrent)


def test_new_file_receipt(tmp_path):
    target = tmp_path / "new.yaml"
    receipt = atomic.atomic_write_utf8(target, "replacement")
    assert receipt["before_sha"] is None
    assert receipt["attempted_sha"] == digest(ATTEMPTED)
    assert receipt["written_sha"] == digest(ATTEMPTED)
    assert receipt["restored_sha"] is None
    assert_only_target(target, ATTEMPTED)


def test_short_writes_are_completed(target, monkeypatch):
    real_write = atomic.os.write

    def short_write(fd, data):
        # One byte per call is the smallest positive POSIX write result.
        return real_write(fd, data[:len(b"x")])

    monkeypatch.setattr(atomic.os, "write", short_write)
    atomic.atomic_write_utf8(target, "replacement")
    assert_only_target(target, ATTEMPTED)


@pytest.mark.parametrize("operation", ["write", "chmod", "fsync"])
def test_staging_failure_preserves_target(target, monkeypatch, operation):
    def fail(*args):
        raise OSError("injected staging failure")

    monkeypatch.setattr(atomic.os, operation, fail)
    with pytest.raises(atomic.AtomicWriteError):
        atomic.atomic_write_utf8(target, "replacement")
    assert_only_target(target)
    assert stat.S_IMODE(target.stat().st_mode) == MODE


def test_concurrent_creation_refused(tmp_path, monkeypatch):
    target = tmp_path / "new.yaml"
    real_stage = atomic._stage

    def stage_and_create(*args):
        staged = real_stage(*args)
        target.write_bytes(BEFORE)
        return staged

    monkeypatch.setattr(atomic, "_stage", stage_and_create)
    with pytest.raises(atomic.ConcurrentChangeError):
        atomic.atomic_write_utf8(target, "replacement")
    assert_only_target(target)


def test_concurrent_mode_change_refused(target, monkeypatch):
    real_stage = atomic._stage
    changed_mode = stat.S_IRUSR

    def stage_and_chmod(*args):
        staged = real_stage(*args)
        target.chmod(changed_mode)
        return staged

    monkeypatch.setattr(atomic, "_stage", stage_and_chmod)
    with pytest.raises(atomic.ConcurrentChangeError):
        atomic.atomic_write_utf8(target, "replacement")
    assert_only_target(target)
    assert stat.S_IMODE(target.stat().st_mode) == changed_mode


def test_symlink_refused(tmp_path):
    referent = tmp_path / "referent.yaml"
    referent.write_bytes(BEFORE)
    target = tmp_path / "link.yaml"
    target.symlink_to(referent)
    with pytest.raises(ValueError, match="regular file"):
        atomic.atomic_write_utf8(target, "replacement")
    assert referent.read_bytes() == BEFORE
    assert target.is_symlink()
    assert set(tmp_path.iterdir()) == {referent, target}


def test_encoding_precedes_filesystem_access(target, monkeypatch):
    def unexpected_access(*args):
        pytest.fail("encoding must precede filesystem access")

    monkeypatch.setattr(atomic, "_snapshot", unexpected_access)
    monkeypatch.setattr(atomic, "_stage", unexpected_access)
    with pytest.raises(UnicodeEncodeError):
        atomic.atomic_write_utf8(target, "\udcff")
    assert_only_target(target)


def test_empty_content(target):
    receipt = atomic.atomic_write_utf8(target, "")
    assert_only_target(target, b"")
    assert receipt["written_sha"] == digest(b"")


def test_zero_progress_preserves_target(target, monkeypatch):
    monkeypatch.setattr(atomic.os, "write", lambda *args: len(b""))
    with pytest.raises(atomic.AtomicWriteError, match="replacement failed"):
        atomic.atomic_write_utf8(target, "replacement")
    assert_only_target(target)


def test_same_bytes_in_different_inode_refused(target, monkeypatch):
    real_stage = atomic._stage

    def stage_and_replace(*args):
        staged = real_stage(*args)
        unrelated = target.with_name("other.yaml")
        unrelated.write_bytes(BEFORE)
        unrelated.chmod(MODE)
        os.replace(unrelated, target)
        return staged

    monkeypatch.setattr(atomic, "_stage", stage_and_replace)
    with pytest.raises(atomic.ConcurrentChangeError):
        atomic.atomic_write_utf8(target, "replacement")
    assert_only_target(target)


def inject_readback_failure(target, monkeypatch, persistent=False):
    """Fail target observation after replacement; staging remains real."""
    real_replace = atomic.os.replace
    real_snapshot = atomic._snapshot
    state = {"installed": False, "failed": False}

    def replace(source, destination):
        real_replace(source, destination)
        state["installed"] = True

    def snapshot(path):
        if Path(path) == target and state["installed"] and (persistent or not state["failed"]):
            state["failed"] = True
            raise OSError("injected readback failure")
        return real_snapshot(path)

    monkeypatch.setattr(atomic.os, "replace", replace)
    monkeypatch.setattr(atomic, "_snapshot", snapshot)
    return state


def test_recovery_refuses_change_during_restore_staging(target, monkeypatch):
    state = inject_readback_failure(target, monkeypatch)
    real_stage = atomic._stage
    concurrent = b"another update during recovery"

    def stage_and_change(*args):
        staged = real_stage(*args)
        if state["installed"]:
            target.write_bytes(concurrent)
        return staged

    monkeypatch.setattr(atomic, "_stage", stage_and_change)
    with pytest.raises(atomic.AtomicWriteError) as failure:
        atomic.atomic_write_utf8(target, "replacement")
    assert failure.value.receipt["recovery"] == "refused"
    assert failure.value.receipt["restored_sha"] is None
    assert_only_target(target, concurrent)


def test_recovery_replace_failure_retains_before_receipt(target, monkeypatch):
    state = inject_readback_failure(target, monkeypatch)
    replace = atomic.os.replace

    def fail_recovery(source, destination):
        if state["installed"]:
            raise PermissionError("injected recovery replacement failure")
        replace(source, destination)

    monkeypatch.setattr(atomic.os, "replace", fail_recovery)
    with pytest.raises(atomic.AtomicWriteError) as failure:
        atomic.atomic_write_utf8(target, "replacement")
    assert failure.value.receipt["recovery"] == "failed"
    assert failure.value.receipt["recovery_error"] == "PermissionError"
    assert failure.value.receipt["restored_sha"] is None
    assert failure.value.before_bytes == BEFORE
    assert_only_target(target, ATTEMPTED)


def test_unreadable_recovery_does_not_replace(target, monkeypatch):
    inject_readback_failure(target, monkeypatch, persistent=True)
    with pytest.raises(atomic.AtomicWriteError) as failure:
        atomic.atomic_write_utf8(target, "replacement")
    assert failure.value.receipt["recovery"] == "failed"
    assert failure.value.receipt["restored_sha"] is None
    assert_only_target(target, ATTEMPTED)


def test_new_file_readback_failure_retains_attempt(tmp_path, monkeypatch):
    target = tmp_path / "new.yaml"
    inject_readback_failure(target, monkeypatch)
    with pytest.raises(atomic.AtomicWriteError) as failure:
        atomic.atomic_write_utf8(target, "replacement")
    assert failure.value.receipt["before_sha"] is None
    assert failure.value.receipt["attempted_sha"] == digest(ATTEMPTED)
    assert failure.value.receipt["recovery"] == "not_available"
    assert failure.value.before_bytes is None
    assert_only_target(target, ATTEMPTED)


def test_identical_bytes_replaced_by_other_writer_not_recovered(target, monkeypatch):
    real_replace = atomic.os.replace

    def replace_then_other_inode(source, destination):
        real_replace(source, destination)
        other = target.with_name("other.yaml")
        other.write_bytes(ATTEMPTED)
        other.chmod(MODE)
        real_replace(other, target)

    monkeypatch.setattr(atomic.os, "replace", replace_then_other_inode)
    with pytest.raises(atomic.AtomicWriteError) as failure:
        atomic.atomic_write_utf8(target, "replacement")
    assert failure.value.receipt["recovery"] == "refused"
    assert_only_target(target, ATTEMPTED)


def test_staged_mode_mismatch_preserves_target(target, monkeypatch):
    real_stage = atomic._stage

    def stage_wrong_mode(*args):
        staged = real_stage(*args)
        staged.chmod(stat.S_IRUSR)
        return staged

    monkeypatch.setattr(atomic, "_stage", stage_wrong_mode)
    with pytest.raises(atomic.AtomicWriteError, match="replacement failed"):
        atomic.atomic_write_utf8(target, "replacement")
    assert_only_target(target)
    assert stat.S_IMODE(target.stat().st_mode) == MODE


@pytest.mark.parametrize("phase", ["replacement", "staging", "recovery"])
def test_cleanup_failure_preserves_primary_receipt(target, monkeypatch, phase):
    if phase == "recovery":
        state = inject_readback_failure(target, monkeypatch)
        replace = atomic.os.replace

        def fail_replace(source, destination):
            if state["installed"]:
                raise PermissionError("injected replacement failure")
            replace(source, destination)
    else:
        def fail_replace(source, destination):
            raise PermissionError("injected replacement failure")

    def fail_write(*args):
        raise OSError("injected staging failure")

    def fail_cleanup(*args, **kwargs):
        raise PermissionError("injected cleanup failure")

    with monkeypatch.context() as faults:
        faults.setattr(atomic.os, "replace", fail_replace)
        faults.setattr(Path, "unlink", fail_cleanup)
        if phase == "staging":
            faults.setattr(atomic.os, "write", fail_write)
        with pytest.raises(atomic.AtomicWriteError) as failure:
            atomic.atomic_write_utf8(target, "replacement")

    error = failure.value
    receipt = error.receipt
    assert error.before_bytes == BEFORE
    assert error.before_mode == MODE
    assert receipt["before_sha"] == digest(BEFORE)
    assert receipt["attempted_sha"] == digest(ATTEMPTED)
    assert receipt["written_sha"] is None
    assert receipt["restored_sha"] is None
    assert isinstance(error.__cause__, OSError)
    retained = set(target.parent.iterdir()) - {target}
    assert len(retained) == 1
    sibling = retained.pop()
    assert receipt["cleanup_errors"] == [
        {"error": "PermissionError", "retained_path": sibling.as_posix()}
    ]
    if phase == "recovery":
        assert receipt["recovery"] == "failed"
        assert receipt["recovery_error"] == "PermissionError"
    expected = ATTEMPTED if phase == "recovery" else BEFORE
    assert target.read_bytes() == expected
    assert stat.S_IMODE(target.stat().st_mode) == MODE
    assert sibling.read_bytes() == (
        b"" if phase == "staging" else BEFORE if phase == "recovery" else ATTEMPTED
    )
