"""Small fail-closed retained-FD primitives used by genesis bootstrap."""
import fcntl
import os
import stat
import hashlib

SEALS = fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL

def fd_sha256(fd: int) -> str:
    h = hashlib.sha256()
    off = 0
    while True:
        chunk = os.pread(fd, 65536, off)
        if not chunk:
            return h.hexdigest()
        h.update(chunk)
        off += len(chunk)

def revalidate(fd: int, expected_sha256: str, expected_stat: os.stat_result | None = None) -> None:
    current = os.fstat(fd)
    if expected_stat and (current.st_dev, current.st_ino, current.st_mode, current.st_size, current.st_uid, current.st_nlink) != (expected_stat.st_dev, expected_stat.st_ino, expected_stat.st_mode, expected_stat.st_size, expected_stat.st_uid, expected_stat.st_nlink):
        raise PermissionError("retained identity changed")
    if fd_sha256(fd) != expected_sha256:
        raise PermissionError("retained digest changed")

def open_verified_bundle(members: dict[str, tuple[str, str]]) -> dict[str, int]:
    opened: dict[str, int] = {}
    try:
        for name, (path, digest) in members.items():
            fd = open_nofollow(path)
            try:
                st = os.fstat(fd)
                revalidate(fd, digest, st)
            except Exception:
                os.close(fd)
                raise
            opened[name] = fd
        return opened
    except Exception:
        for fd in opened.values():
            try:
                os.close(fd)
            except OSError:
                pass
        raise


def open_nofollow(path: str, mode: int = 0o600, max_size: int = 16384) -> int:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    st = os.fstat(fd)
    if (not stat.S_ISREG(st.st_mode) or st.st_uid != os.getuid()
            or stat.S_IMODE(st.st_mode) != mode or st.st_nlink != 1
            or st.st_size < 1 or st.st_size > max_size):
        os.close(fd)
        raise PermissionError("non-canonical retained input")
    os.set_inheritable(fd, True)
    return fd


def sealed_memfd(name: str, payload: bytes) -> int:
    fd = os.memfd_create(name, os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    view = memoryview(payload)
    while view:
        view = view[os.write(fd, view):]
    fcntl.fcntl(fd, fcntl.F_ADD_SEALS, SEALS)
    if fcntl.fcntl(fd, fcntl.F_GET_SEALS) != SEALS or os.pread(fd, len(payload), 0) != payload:
        os.close(fd)
        raise PermissionError("memfd seal/readback mismatch")
    return fd


def allowlist_fds(keep: set[int]) -> None:
    for name in os.listdir("/proc/self/fd"):
        if not name.isdigit():
            continue
        fd = int(name)
        if fd > 2 and fd not in keep:
            try:
                os.close(fd)
            except OSError:
                pass
        elif fd in keep:
            os.set_inheritable(fd, True)
