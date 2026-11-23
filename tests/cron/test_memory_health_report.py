"""Tests for scripts/cron/memory-health-report.sh — TDD per #2313 plan."""

import os
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "memory-health-report.sh"


def _run(tmp_path: Path, dirs: list[Path], env_extra: dict | None = None):
    out_dir = tmp_path / "out"
    env = os.environ.copy()
    env["MEMORY_HEALTH_OUT_DIR"] = str(out_dir)
    env["MEMORY_HEALTH_WEEK"] = "2026-W16"
    env["MEMORY_HEALTH_DIRS"] = ":".join(str(d) for d in dirs)
    env["REPO_ROOT"] = str(tmp_path)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        ["bash", str(SCRIPT)],
        env=env, capture_output=True, text=True, timeout=15,
    )
    return r, out_dir / "memory-health-2026-W16.md"


def _mk_mem(base: Path, layout: dict[str, int], mtime_days_ago: int | None = None):
    """Create files under base with given sizes in KB. Optionally stomp mtime."""
    base.mkdir(parents=True, exist_ok=True)
    for name, kb in layout.items():
        p = base / name
        p.write_bytes(b"x" * (kb * 1024))
        if mtime_days_ago is not None:
            ts = time.time() - mtime_days_ago * 86400
            os.utime(p, (ts, ts))


def test_memory_health_green_when_small(tmp_path):
    d = tmp_path / "mem"
    _mk_mem(d, {"a.md": 100, "b.md": 50})
    r, report = _run(tmp_path, [d])
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** GREEN" in body


def test_memory_health_yellow_when_warn(tmp_path):
    d = tmp_path / "mem"
    _mk_mem(d, {"big.md": 6 * 1024})  # 6 MB > 5 MB warn
    r, report = _run(tmp_path, [d])
    assert r.returncode == 0
    body = report.read_text()
    assert "Status:** YELLOW" in body


def test_memory_health_red_when_block(tmp_path):
    d = tmp_path / "mem"
    _mk_mem(d, {"huge.md": 25 * 1024})  # 25 MB > 20 MB block
    r, report = _run(tmp_path, [d])
    assert r.returncode == 0
    body = report.read_text()
    assert "Status:** RED" in body


def test_memory_health_lists_top_10_by_size(tmp_path):
    d = tmp_path / "mem"
    _mk_mem(d, {f"f{i:02d}.md": i * 10 for i in range(1, 15)})
    r, report = _run(tmp_path, [d])
    assert r.returncode == 0
    body = report.read_text()
    top_section = body.split("## Top 10 largest", 1)[1].split("## ", 1)[0]
    rows = [ln for ln in top_section.splitlines() if ln.startswith("| ") and "Size (MB)" not in ln and "-----" not in ln]
    assert 1 <= len(rows) <= 10


def test_memory_health_flags_stale_entries(tmp_path):
    d = tmp_path / "mem"
    _mk_mem(d, {"old.md": 10}, mtime_days_ago=120)
    _mk_mem(d, {"new.md": 10}, mtime_days_ago=1)
    r, report = _run(tmp_path, [d])
    assert r.returncode == 0
    body = report.read_text()
    assert "old.md" in body
    stale_section = body.split("## Stale entries", 1)[1].split("## ", 1)[0]
    assert "old.md" in stale_section
    assert "new.md" not in stale_section


def test_memory_health_deduplicates_topics(tmp_path):
    d1 = tmp_path / "mem1"
    d2 = tmp_path / "mem2"
    _mk_mem(d1, {"topic_shared.md": 10, "unique1.md": 10})
    _mk_mem(d2, {"topic_shared.md": 10, "unique2.md": 10})
    r, report = _run(tmp_path, [d1, d2])
    assert r.returncode == 0
    body = report.read_text()
    dup_section = body.split("## Duplicate topics", 1)[1].split("## ", 1)[0]
    assert "topic_shared" in dup_section
    assert "unique1" not in dup_section
    assert "unique2" not in dup_section


def test_memory_health_handles_missing_dirs(tmp_path):
    d_missing = tmp_path / "does_not_exist"
    r, report = _run(tmp_path, [d_missing])
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** GREEN" in body
    assert "0 files" in body
