import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from genesis_broker import allowlist_fds, fd_sha256, open_nofollow, revalidate, sealed_memfd


def test_open_nofollow_rejects_symlink(tmp_path):
    target = tmp_path / "x"
    target.write_bytes(b"x")
    target.chmod(0o600)
    link = tmp_path / "l"
    link.symlink_to(target)
    try:
        open_nofollow(str(link))
    except OSError:
        pass
    else:
        raise AssertionError("symlink accepted")


def test_open_nofollow_bounds_owner_and_inheritable(tmp_path):
    path = tmp_path / "record"
    path.write_bytes(b"x")
    path.chmod(0o600)
    fd = open_nofollow(str(path))
    try:
        assert os.get_inheritable(fd)
    finally:
        os.close(fd)
    path.write_bytes(b"x" * 16385)
    try:
        open_nofollow(str(path))
    except OSError:
        pass
    else:
        raise AssertionError("oversize record accepted")


def test_sealed_memfd_roundtrip():
    fd = sealed_memfd("identity", b"abc\n")
    try:
        assert os.pread(fd, 4, 0) == b"abc\n"
    finally:
        os.close(fd)


def test_revalidate_hash_and_identity(tmp_path):
    path = tmp_path / "record"
    payload = b"canonical\n"
    path.write_bytes(payload)
    path.chmod(0o600)
    fd = open_nofollow(str(path))
    try:
        st = os.fstat(fd)
        digest = fd_sha256(fd)
        revalidate(fd, digest, st)
        os.write(os.open(str(path), os.O_WRONLY), b"x")
        try:
            revalidate(fd, digest, st)
        except PermissionError:
            pass
        else:
            raise AssertionError("changed retained input accepted")
    finally:
        os.close(fd)


def test_allowlist_closes_unrelated_fd():
    extra = os.open("/dev/null", os.O_RDONLY)
    allowlist_fds(set())
    try:
        os.fstat(extra)
    except OSError:
        pass
    else:
        raise AssertionError("unrelated fd retained")
