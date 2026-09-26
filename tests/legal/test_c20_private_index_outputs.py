"""C20: archive-drive indexes and name-bearing memory snapshots live privately.

The content index and the conference/document indexes are built on a host from
the private archive drive, and they carry client names. Owner decision C20
moves them to a private repository. Their builders now resolve the output (and
their readers the input) through ``scripts/lib/private_data.py``: the private
data directory named by ``WORKSPACE_HUB_PRIVATE_DATA_DIR``, never a path in this
public checkout. Unset, missing or inside this repository -- the builder stops.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "scripts" / "lib" / "private_data.py"

MOVED = [
    "data/content_index.json",
    "docs/CONTENT_INDEX.md",
    "data/document-index/conference-index-batch.jsonl",
    "data/document-index/conference-index.jsonl",
    "data/document-index/conference-phase-a-results.jsonl",
    "data/document-index/cross-drive-dedup-report.json",
]

WRITERS = {
    "scripts/search/build_content_index.py": ["content_index.json", "CONTENT_INDEX.md"],
    "scripts/data/document-index/prep-conference-index.py": ["conference-index-batch.jsonl"],
    "scripts/document-intelligence/index-conferences-lightweight.py": ["conference-index.jsonl"],
    "scripts/data/document-index/batch-conference-phase-a.py": [
        "conference-index-batch.jsonl", "conference-phase-a-results.jsonl"],
    "scripts/data/document-index/cross-drive-dedup-audit.py": ["cross-drive-dedup-report.json"],
    "scripts/data/document-index/conference-stats.py": ["conference-index-batch.jsonl"],
    "scripts/knowledge/run_batch_pack_2.py": ["conference-phase-a-results.jsonl"],
}


def load_lib():
    spec = importlib.util.spec_from_file_location("private_data_under_test", LIB)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_unset_directory_is_refused(monkeypatch):
    monkeypatch.delenv("WORKSPACE_HUB_PRIVATE_DATA_DIR", raising=False)
    mod = load_lib()
    with pytest.raises(mod.PrivateDataUnavailable):
        mod.private_data_path("data/content_index.json")


def test_missing_directory_is_refused(monkeypatch, tmp_path):
    monkeypatch.setenv("WORKSPACE_HUB_PRIVATE_DATA_DIR", str(tmp_path / "absent"))
    mod = load_lib()
    with pytest.raises(mod.PrivateDataUnavailable):
        mod.private_data_path("data/content_index.json")


def test_directory_inside_this_repository_is_refused(monkeypatch):
    monkeypatch.setenv("WORKSPACE_HUB_PRIVATE_DATA_DIR", str(ROOT / "data"))
    mod = load_lib()
    with pytest.raises(mod.PrivateDataUnavailable):
        mod.private_data_path("data/content_index.json")


def test_relative_directory_is_refused(monkeypatch):
    monkeypatch.setenv("WORKSPACE_HUB_PRIVATE_DATA_DIR", "relative/dir")
    mod = load_lib()
    with pytest.raises(mod.PrivateDataUnavailable):
        mod.private_data_path("x")


def test_valid_directory_resolves(monkeypatch, tmp_path):
    monkeypatch.setenv("WORKSPACE_HUB_PRIVATE_DATA_DIR", str(tmp_path))
    mod = load_lib()
    p = mod.private_data_path("data/document-index/conference-index.jsonl")
    assert p == tmp_path / "data" / "document-index" / "conference-index.jsonl"


def test_explicit_output_inside_this_repository_is_refused():
    mod = load_lib()
    with pytest.raises(mod.PrivateDataUnavailable):
        mod.require_outside_repo(ROOT / "data" / "content_index.json")


def test_message_never_quotes_the_path(monkeypatch, tmp_path):
    secret_dir = tmp_path / "zorblaxcorp-archive"
    monkeypatch.setenv("WORKSPACE_HUB_PRIVATE_DATA_DIR", str(secret_dir))
    mod = load_lib()
    with pytest.raises(mod.PrivateDataUnavailable) as exc:
        mod.private_data_path("x")
    assert "zorblaxcorp" not in str(exc.value)


def _env(**extra):
    env = {k: v for k, v in os.environ.items()
           if k not in ("WORKSPACE_HUB_PRIVATE_DATA_DIR", "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")}
    env.update(extra)
    return env


def _snapshot(paths):
    return {p: (p.read_bytes() if p.exists() else None) for p in paths}


def test_content_index_builder_stops_without_the_private_directory(tmp_path):
    # Run from a scratch directory: an old relative default would write there,
    # not into this checkout. The checkout copies are compared byte for byte.
    (tmp_path / "scan").mkdir()
    guarded = [ROOT / "data" / "content_index.json", ROOT / "docs" / "CONTENT_INDEX.md"]
    before = _snapshot(guarded)
    r = subprocess.run([sys.executable, str(ROOT / "scripts/search/build_content_index.py"),
                        "--root", str(tmp_path / "scan")],
                       cwd=tmp_path, capture_output=True, text=True, env=_env())
    assert r.returncode != 0
    assert not (tmp_path / "data" / "content_index.json").exists()
    assert not (tmp_path / "docs" / "CONTENT_INDEX.md").exists()
    assert _snapshot(guarded) == before


def test_content_index_builder_writes_to_the_private_directory(tmp_path):
    scan = tmp_path / "scan"
    (scan / "repo" / ".git").mkdir(parents=True)
    (scan / "repo" / "README.md").write_text("# r\n", encoding="utf-8")
    private = tmp_path / "private"
    private.mkdir()
    r = subprocess.run([sys.executable, str(ROOT / "scripts/search/build_content_index.py"),
                        "--root", str(scan)],
                       cwd=tmp_path, capture_output=True, text=True,
                       env=_env(WORKSPACE_HUB_PRIVATE_DATA_DIR=str(private)))
    assert r.returncode == 0, r.stderr
    assert (private / "data" / "content_index.json").exists()
    assert (private / "docs" / "CONTENT_INDEX.md").exists()


def test_content_index_builder_refuses_an_explicit_public_output(tmp_path):
    (tmp_path / "scan").mkdir()
    target = ROOT / "data" / "c20-probe-content-index.json"
    assert not target.exists()
    try:
        r = subprocess.run([sys.executable, str(ROOT / "scripts/search/build_content_index.py"),
                            "--root", str(tmp_path / "scan"),
                            "--output-json", str(target),
                            "--output-md", str(tmp_path / "x.md")],
                           cwd=tmp_path, capture_output=True, text=True, env=_env())
        assert r.returncode != 0
        assert not target.exists()
    finally:
        if target.exists():
            target.unlink()


@pytest.mark.parametrize("script,names", sorted(WRITERS.items()))
def test_builders_resolve_moved_files_privately(script, names):
    """No builder or reader keeps a default path to a moved file in this
    checkout; each resolves it through private_data."""
    text = (ROOT / script).read_text(encoding="utf-8")
    assert "private_data" in text, script
    for name in names:
        for line in text.splitlines():
            if name not in line or "private_data" in line:
                continue
            if "ROOT" in line or "Path(" in line or "default=" in line:
                pytest.fail(f"{script} still defaults {name} into the public tree: {line.strip()}")


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, env=_env())


@pytest.mark.parametrize("rel", MOVED)
def test_moved_file_is_untracked_and_ignored(rel):
    assert _git("ls-files", "--error-unmatch", rel).returncode != 0, rel
    assert _git("check-ignore", "-q", "--no-index", rel).returncode == 0, rel


def test_name_bearing_memory_snapshots_are_gone():
    listed = _git("ls-files", "config/agents/claude/memory-snapshots").stdout.splitlines()
    assert not [p for p in listed if Path(p).name.startswith("crossprovider_hermes_")
                and ("data-lifecycle-uses-promotion" in p or "have-divergent-output-form" in p)]
