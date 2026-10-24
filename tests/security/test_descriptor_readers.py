"""Bounded probes for issue #3439; synthetic fixtures need no external data.

Expected rejection follows POSIX.1-2024 open(): O_NONBLOCK opens a read FIFO
without waiting for a writer, O_NOFOLLOW rejects a final symlink, and regular
file consumers must reject FIFO, socket, directory and character-device modes.
The five-second subprocess watchdog follows bootstrap_git's existing Git
timeout; it bounds a defective reader, rather than measuring performance.
"""

from __future__ import annotations

import os
import socket
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/legal"))

READERS = (
    "tree", "claims", "links", "bound_manifest", "layout", "config",
    "contract", "clone_verify", "clone_normalize", "packed_refs",
    "private", "transaction", "marker", "authority", "broker", "runtime", "runtime_path",
)


def _exercise(reader: str, kind: str, root: Path) -> None:
    import genesis_broker as broker
    import manage_rule_authority as authority
    from client_llm_wiki import (
        bootstrap_attestation as attestation,
    )
    from client_llm_wiki import (
        bootstrap_bound_manifest as bound_manifest,
    )
    from client_llm_wiki import (
        bootstrap_clone_setup as clone_setup,
    )
    from client_llm_wiki import (
        bootstrap_contract as contract,
    )
    from client_llm_wiki import (
        bootstrap_finalizer as finalizer,
    )
    from client_llm_wiki import (
        bootstrap_git as git,
    )
    from client_llm_wiki import (
        bootstrap_layout as layout,
    )
    from client_llm_wiki import (
        bootstrap_manifest as manifest,
    )
    from cron import cron_runtime as runtime
    from rule_authority import codec, private_io

    root.chmod(0o700)
    leaf = root / "input"
    # Synthetic modes repeat the existing private-file contract, not a new limit.
    if kind == "fifo":
        os.mkfifo(leaf, 0o600)
    elif kind == "directory":
        leaf.mkdir()
    elif kind == "symlink":
        leaf.symlink_to(os.devnull)
    elif kind == "socket":
        endpoint = socket.socket(socket.AF_UNIX)
        endpoint.bind(str(leaf))
    elif kind in {"device", "replaced_fifo"}:
        leaf.touch()  # Redirect the leaf open to the real null device below.
    else:
        raise AssertionError(kind)

    transaction = "12345678-1234-4234-9234-123456789abc"
    if reader == "transaction":
        (root / "COMPLETE").touch()
        (root / "marker").touch()
    elif reader == "marker":
        incomplete = root / f".incomplete.{transaction}"
        incomplete.mkdir(mode=0o700)
        (incomplete / "marker").touch()

    real_open, real_read, real_fdopen = os.open, os.read, os.fdopen
    rejected_fds: set[int] = set()
    attempts: list[int] = []

    def tracked_open(path, flags, *args, **kwargs):
        if not flags & os.O_DIRECTORY:
            if kind == "replaced_fifo" and not attempts:
                leaf.rename(root / "original")
                os.mkfifo(leaf, 0o600)
            path = os.devnull if kind == "device" else leaf
            attempts.append(flags)
        fd = real_open(path, flags, *args, **kwargs)
        if not flags & os.O_DIRECTORY:
            rejected_fds.add(fd)
        return fd

    def guarded_read(fd, *args, **kwargs):
        assert fd not in rejected_fds, "non-regular descriptor reached read"
        return real_read(fd, *args, **kwargs)

    def guarded_fdopen(fd, *args, **kwargs):
        stream = real_fdopen(fd, *args, **kwargs)

        class GuardedStream:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return stream.__exit__(*exc)

            def fileno(self):
                return stream.fileno()

            def read(self, *args, **kwargs):
                assert fd not in rejected_fds, "non-regular descriptor reached read"
                return stream.read(*args, **kwargs)

        return GuardedStream()

    os.open, os.read, os.fdopen = tracked_open, guarded_read, guarded_fdopen
    directory = real_open(root, os.O_RDONLY | os.O_DIRECTORY)
    clone = SimpleNamespace(git_fd=directory, root_fd=directory, parent_fd=directory)
    # No config may be handed to a Git child before regular-file validation.
    git.subprocess.run = lambda *args, **kwargs: pytest.fail("Git received unsafe config")
    errors = (OSError, attestation.BootstrapManifestError,
              bound_manifest.BoundManifestError, git.BootstrapGitError,
              contract.BootstrapContractError, finalizer.BootstrapFinalizerError,
              codec.AuthorityError)
    try:
        with pytest.raises(errors):
            if reader == "tree":
                attestation._scan_member(directory, "input", "input", {}, {}, attestation._Budget(), 0)
            elif reader == "claims":
                manifest._read_claims(directory, "input")
            elif reader == "links":
                manifest._verify_links(directory, "input", "input", b"")
            elif reader == "bound_manifest":
                with bound_manifest.bind_validation_context(clone, leaf, "", "", ""):
                    pytest.fail("non-regular manifest accepted")
            elif reader == "layout":
                (root / ".git").mkdir()
                with layout.bind_clone(root):
                    pytest.fail("non-regular config accepted")
            elif reader == "config":
                fd = manifest._open_config(clone)
                os.close(fd)
            elif reader == "contract":
                contract._verify_named_git = lambda _clone: None
                contract._verify_bound_clone(clone, "")
            elif reader == "clone_verify":
                info = os.stat(root)
                clone.git_id = SimpleNamespace(device=info.st_dev, inode=info.st_ino,
                                               file_type=stat.S_IFDIR)
                (root / ".git").mkdir()
                clone.git_id.inode = (root / ".git").stat().st_ino
                clone_setup._strict_verify(clone, "")
            elif reader == "clone_normalize":
                clone_setup._require = lambda *args: "refs/heads/main" if args[1] == "symbolic-ref" else ""
                clone_setup._run = lambda *args: SimpleNamespace(returncode=1)
                clone_setup._authorize_and_normalize(clone, "")
            elif reader == "packed_refs":
                finalizer._reject_replacements(clone)
            elif reader == "private":
                private_io.read_private_file(leaf, len(b"input"))
            elif reader == "transaction":
                private_io.verify_complete_transaction(root, b"synthetic")
            elif reader == "marker":
                private_io.cleanup_incomplete(root, transaction)
            elif reader == "authority":
                authority._read(leaf, len(b"input"))
            elif reader == "broker":
                fd = broker.open_nofollow(str(leaf))
                os.close(fd)
            elif reader in {"runtime", "runtime_path"}:
                parent_fd = directory if reader == "runtime" else None
                assert runtime._read_json(leaf, dir_fd=parent_fd) == {"_invalid": True}
                raise OSError("structured rejection verified")
        assert attempts, "reader never attempted the input open"
        for fd in rejected_fds:
            with pytest.raises(OSError):
                os.fstat(fd)
    finally:
        os.close(directory)


@pytest.mark.skipif(sys.platform != "linux", reason="descriptor and FIFO probes use Linux")
@pytest.mark.parametrize("reader", READERS)
@pytest.mark.parametrize("kind", ["fifo", "symlink", "device", "socket", "directory", "replaced_fifo"])
def test_nonregular_rejected_before_read(tmp_path, reader, kind):
    if reader == "tree" and kind == "directory":
        pytest.skip("tree scanner intentionally accepts directories")
    result = subprocess.run(
        [sys.executable, __file__, reader, kind, str(tmp_path)],
        capture_output=True, text=True, timeout=5, check=False,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("reader", ["private", "authority", "broker", "digest"])
def test_size_boundary(tmp_path, reader):
    """Independent hand calculation: len(b'abc') = 3; 3 > 2, 3 == 3.

    Limits are explicit test inputs. No production default is inferred.
    At the exact limit the bytes are accepted; one byte below rejects.
    """
    import genesis_broker as broker
    import manage_rule_authority as authority
    from client_llm_wiki import bootstrap_attestation as attestation
    from rule_authority import codec, private_io

    tmp_path.chmod(0o700)
    leaf = tmp_path / "input"
    leaf.write_bytes(b"abc")
    leaf.chmod(0o600)

    def read(limit):
        if reader == "private":
            return private_io.read_private_file(leaf, limit)
        if reader == "authority":
            return authority._read(leaf, limit)
        if reader == "broker":
            fd = broker.open_nofollow(str(leaf), max_size=limit)
            try:
                return os.read(fd, len(b"abc"))
            finally:
                os.close(fd)
        with leaf.open("rb") as stream:
            return attestation.stable_digest(stream.fileno(), os.fstat(stream.fileno()), limit)[2]

    assert read(len(b"abc")) == b"abc"
    with pytest.raises((OSError, codec.AuthorityError, attestation.BootstrapManifestError)):
        read(len(b"ab"))


if __name__ == "__main__":
    _exercise(sys.argv[1], sys.argv[2], Path(sys.argv[3]))
