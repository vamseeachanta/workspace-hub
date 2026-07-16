"""Small fail-closed retained-FD primitives used by genesis bootstrap."""
import fcntl
import os
import stat

SEALS = fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL


def open_nofollow(path: str, mode: int = 0o600) -> int:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode) != mode or st.st_nlink != 1:
        os.close(fd)
        raise PermissionError("non-canonical retained input")
    return fd


def sealed_memfd(name: str, payload: bytes) -> int:
    fd = os.memfd_create(name, os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    os.write(fd, payload)
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
