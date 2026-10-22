"""Cache and interruption fixtures have independently specified I/O expectations."""

import json
import os

import pytest
from dedupe import _common
from dedupe.hash_inventory import run


def setup(tmp_path):
    root = tmp_path / "input"
    root.mkdir()
    (root / "a").write_bytes(b"same")
    (root / "b").write_bytes(b"same")
    return {"roots": [str(root)]}, root, tmp_path / "out.jsonl", tmp_path / "cache.json"


def test_cache_hit_avoids_hashing(tmp_path):
    config, _root, out, cache = setup(tmp_path)
    first, _ = run(config, "A", out, cache=cache)

    def forbidden(*args, **kwargs):
        pytest.fail("unchanged hashes should be cached")

    second, meta = run(config, "A", out, cache=cache, opener=forbidden)
    assert second == first and meta["complete"]


def test_changed_mtime_rehashes(tmp_path):
    config, root, out, cache = setup(tmp_path)
    run(config, "A", out, cache=cache)
    path = root / "a"
    info = path.stat()
    os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns + 1))
    opened = []

    def counting(path, mode):
        opened.append(path.name)
        return open(path, mode)

    _, meta = run(config, "A", out, cache=cache, opener=counting)
    assert meta["complete"]
    assert "a" in opened and "b" not in opened


def test_cache_bound_to_roots(tmp_path):
    config, _, out, cache = setup(tmp_path)
    first, _ = run(config, "A", out, cache=cache)
    other = tmp_path / "other"
    other.mkdir()
    for name in ["a", "b"]:
        (other / name).write_bytes(b"diff")
    rows, _ = run({"roots": [str(other)]}, "A", out, cache=cache)
    assert rows[0]["sha256"] != first[0]["sha256"]


def test_budget_writes_partial_manifest_and_can_resume(tmp_path):
    config, _, out, cache = setup(tmp_path)
    tick = 0

    def clock():
        nonlocal tick
        tick += 1
        return tick

    _rows, meta = run(config, "A", out, cache=cache, clock=clock, max_seconds=3)
    assert not meta["complete"] and meta["stop_reason"] == "budget"
    assert not json.loads(out.read_text().splitlines()[0])["complete"]
    _, resumed = run(config, "A", out, cache=cache)
    assert resumed["complete"]


def test_interrupted_write_preserves_previous_output(tmp_path, monkeypatch):
    config, _, out, _ = setup(tmp_path)
    out.write_text("previous manifest\n")

    def interrupted(*args):
        raise OSError("synthetic interruption")

    monkeypatch.setattr(_common.os, "replace", interrupted)
    with pytest.raises(OSError):
        run(config, "A", out)
    assert out.read_text() == "previous manifest\n"


def test_cache_output_in_scan_rejected(tmp_path):
    config, root, out, _ = setup(tmp_path)
    with pytest.raises(ValueError):
        run(config, "A", out, cache=root / "a")
    assert (root / "a").read_bytes() == b"same"


def test_cached_sample_upgrades_when_new_collision_appears(tmp_path):
    config, root, out, cache = setup(tmp_path)
    (root / "b").write_bytes(b"diff")
    rows, _ = run(config, "A", out, cache=cache)
    assert all(r["stage"] == "sample" for r in rows)
    (root / "c").write_bytes(b"same")
    rows, _ = run(config, "A", out, cache=cache)
    assert rows[0]["stage"] == "full" and rows[2]["stage"] == "full"
    assert rows[0]["sha256"] == rows[2]["sha256"]


def test_hashes_finished_before_budget_are_cached(tmp_path):
    config, _, out, cache = setup(tmp_path)
    calls = 0

    def clock():
        nonlocal calls
        calls += 1
        return calls

    rows, meta = run(config, "A", out, cache=cache, clock=clock, max_seconds=8)
    assert not meta["complete"]
    assert any(r["sample_sha256"] for r in rows)
    opened = []

    def counting(path, mode):
        opened.append(path.name)
        return open(path, mode)

    run(config, "A", out, cache=cache, opener=counting)
    # A sampled row needs only its full read, rather than sample and full reads.
    assert len(opened) < 4


def test_cached_hash_does_not_promote_current_size_singleton(tmp_path):
    """Changing b from four to five bytes leaves a singleton of each size."""
    config, root, out, cache = setup(tmp_path)
    run(config, "A", out, cache=cache)
    (root / "b").write_bytes(b"other")
    rows, meta = run(config, "A", out, cache=cache)
    assert meta["complete"]
    assert all(r["stage"] == "size" and r["sha256"] is None for r in rows)
