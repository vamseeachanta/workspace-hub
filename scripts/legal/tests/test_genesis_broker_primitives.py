import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from genesis_broker import allowlist_fds, open_nofollow, sealed_memfd


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


def test_sealed_memfd_roundtrip():
    fd = sealed_memfd("identity", b"abc\n")
    try:
        assert os.pread(fd, 4, 0) == b"abc\n"
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
