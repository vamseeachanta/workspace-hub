"""RED contracts for canonical private/public descriptor bundle handling."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
from genesis_broker import open_verified_bundle  # noqa: F401


def test_bundle_opens_all_members_and_revalidates_digest(tmp_path):
    members = {}
    for name, data in (("approval", b"approval"), ("contract", b"contract"),
                       ("execution_manifest", b"manifest"), ("verifier", b"verifier")):
        path = tmp_path / f"{name}.json"
        path.write_bytes(data)
        path.chmod(0o600)
        members[name] = (str(path), __import__("hashlib").sha256(data).hexdigest())
    bundle = open_verified_bundle(members)
    try:
        assert set(bundle) == set(members)
        assert all(__import__("os").get_inheritable(fd) for fd in bundle.values())
    finally:
        for fd in bundle.values():
            __import__("os").close(fd)


def test_bundle_rejects_symlink_and_digest_mismatch(tmp_path):
    target = tmp_path / "real"
    target.write_bytes(b"x")
    target.chmod(0o600)
    link = tmp_path / "link"
    link.symlink_to(target)
    with pytest.raises(OSError):
        open_verified_bundle({"approval": (str(link), "00" * 32)})
    with pytest.raises(OSError):
        open_verified_bundle({"approval": (str(target), "00" * 32)})


def test_bundle_failure_closes_current_member(tmp_path):
    path = tmp_path / "record"
    path.write_bytes(b"x")
    path.chmod(0o600)
    before = set(int(p.name) for p in Path("/proc/self/fd").iterdir() if p.name.isdigit())
    with pytest.raises(OSError):
        open_verified_bundle({"approval": (str(path), "00" * 32)})
    after = set(int(p.name) for p in Path("/proc/self/fd").iterdir() if p.name.isdigit())
    assert after <= before | {0, 1, 2}
