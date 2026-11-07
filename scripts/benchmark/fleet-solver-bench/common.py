"""Shared helpers for the fleet solver benchmark.

Host profile (W0), result records and timing. Records carry the fleet LABEL only,
never the physical host name: this repository is public, and the label-to-host
map is private (scripts/fleet/fleet_snapshot_labels.py).
"""

from __future__ import annotations

import ctypes
import datetime as dt
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from statistics import median

SCHEMA_VERSION = 1
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]

# Same approved-label rule as scripts/fleet/fleet_snapshot_labels.py.
LABEL_RE = re.compile(
    r"^(?:ace-(?:linux|win)-[0-9]+|gpu-claw|fleet-collector|mac-[0-9]+|spark-[0-9]+)$"
)


def is_public_label(value: object) -> bool:
    return isinstance(value, str) and bool(LABEL_RE.match(value))


def require_label(label: str) -> str:
    if not is_public_label(label):
        raise SystemExit(
            f"refusing label {label!r}: use an approved fleet label "
            "(ace-win-N, ace-linux-N, gpu-claw, ...), never a physical host name"
        )
    return label


def default_out_dir(label: str) -> Path:
    """Results live outside the repository by default, so nothing is committed by accident."""
    root = os.environ.get("FLEET_BENCH_ROOT") or str(Path.home() / "fleet-bench-results")
    return Path(root) / label


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def repo_commit() -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--short=12", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


# ---------------------------------------------------------------- memory


def _meminfo_linux() -> tuple[int, int] | None:
    try:
        fields = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, _, rest = line.partition(":")
            fields[key] = int(rest.split()[0]) * 1024
        return fields["MemTotal"], fields.get("MemAvailable", fields["MemFree"])
    except (OSError, KeyError, ValueError, IndexError):
        return None


def _meminfo_windows() -> tuple[int, int] | None:
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    try:
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):  # type: ignore[attr-defined]
            return None
        return int(stat.ullTotalPhys), int(stat.ullAvailPhys)
    except (AttributeError, OSError):
        return None


def memory_bytes() -> tuple[int, int] | None:
    """(total, available) physical memory in bytes, or None when unreadable."""
    if sys.platform.startswith("win"):
        return _meminfo_windows()
    if sys.platform.startswith("linux"):
        return _meminfo_linux()
    return None


def free_ram_fraction() -> float | None:
    mem = memory_bytes()
    if not mem or not mem[0]:
        return None
    return mem[1] / mem[0]


# ---------------------------------------------------------------- profile


def cpu_model() -> str:
    if sys.platform.startswith("linux"):
        try:
            for line in Path("/proc/cpuinfo").read_text().splitlines():
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
        except OSError:
            pass
    if sys.platform.startswith("win"):
        ident = os.environ.get("PROCESSOR_IDENTIFIER")
        if ident:
            return ident
    return platform.processor() or platform.machine()


def orcaflex_dll_version() -> str | None:
    """Import only — no Model() is constructed, so no licence seat is taken."""
    try:
        import OrcFxAPI  # noqa: PLC0415

        return str(OrcFxAPI.DLLVersion())
    except Exception:  # noqa: BLE001 — absent or broken binding both mean "not available"
        return None


def host_profile(label: str, out_dir: Path) -> dict:
    mem = memory_bytes()
    disk_root = out_dir if out_dir.exists() else Path.home()
    try:
        numpy_version = __import__("numpy").__version__
    except ImportError:
        numpy_version = None
    return {
        "label": label,
        "os": platform.system(),
        "os_release": platform.release(),
        "python": platform.python_version(),
        "cpu_model": cpu_model(),
        "logical_cores": os.cpu_count(),
        "ram_gb": round(mem[0] / 2**30, 1) if mem else None,
        "ram_free_gb": round(mem[1] / 2**30, 1) if mem else None,
        "disk_free_gb": round(shutil.disk_usage(disk_root).free / 2**30, 1),
        "numpy": numpy_version,
        "orcaflex_dll": orcaflex_dll_version(),
        "repo_commit": repo_commit(),
        "collected_utc": utc_now(),
    }


# ---------------------------------------------------------------- timing


def summarise(times: list[float]) -> dict:
    return {
        "times_s": [round(t, 4) for t in times],
        "median_s": round(median(times), 4),
        "min_s": round(min(times), 4),
        "max_s": round(max(times), 4),
    }


class Stopwatch:
    def __enter__(self) -> "Stopwatch":
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc: object) -> None:
        self.elapsed = time.perf_counter() - self.start


def write_record(out_dir: Path, name: str, record: dict) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.json"
    record = {"schema_version": SCHEMA_VERSION, **record}
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return path
