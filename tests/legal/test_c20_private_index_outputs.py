"""Archive-drive indexes are local working files (owner decisions C20, S01).

The content index and the conference/document indexes are built on a host from
the private archive drive; they carry client names and the real archive paths
that later pipeline steps open. C20 moved them to a private data directory
named by ``WORKSPACE_HUB_PRIVATE_DATA_DIR`` and stopped every builder when it
was unset. S01 drops that host setting: the builders write to their usual path
in this checkout again, and the files stay git-ignored, so they are never
published. Redacting them instead would break the paths the pipeline reads.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

LOCAL_ONLY = [
    "data/content_index.json",
    "docs/CONTENT_INDEX.md",
    "data/document-index/conference-index-batch.jsonl",
    "data/document-index/conference-index.jsonl",
    "data/document-index/conference-phase-a-results.jsonl",
    "data/document-index/cross-drive-dedup-report.json",
]

BUILDERS = [
    "scripts/search/build_content_index.py",
    "scripts/data/document-index/prep-conference-index.py",
    "scripts/document-intelligence/index-conferences-lightweight.py",
    "scripts/data/document-index/batch-conference-phase-a.py",
    "scripts/data/document-index/cross-drive-dedup-audit.py",
    "scripts/data/document-index/conference-stats.py",
    "scripts/knowledge/run_batch_pack_2.py",
]


def _env(**extra):
    env = {k: v for k, v in os.environ.items()
           if k not in ("WORKSPACE_HUB_PRIVATE_DATA_DIR", "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")}
    env.update(extra)
    return env


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, env=_env())


def test_private_data_setting_is_gone():
    assert not (ROOT / "scripts" / "lib" / "private_data.py").exists()


@pytest.mark.parametrize("script", BUILDERS)
def test_builders_need_no_private_data_directory(script):
    text = (ROOT / script).read_text(encoding="utf-8")
    assert "WORKSPACE_HUB_PRIVATE_DATA_DIR" not in text, script
    assert "private_data" not in text, script


def test_content_index_builder_runs_without_the_private_directory(tmp_path):
    scan = tmp_path / "scan"
    (scan / "repo" / ".git").mkdir(parents=True)
    (scan / "repo" / "README.md").write_text("# r\n", encoding="utf-8")
    out_json, out_md = tmp_path / "content_index.json", tmp_path / "CONTENT_INDEX.md"
    r = subprocess.run([sys.executable, str(ROOT / "scripts/search/build_content_index.py"),
                        "--root", str(scan), "--output-json", str(out_json),
                        "--output-md", str(out_md)],
                       cwd=tmp_path, capture_output=True, text=True, env=_env())
    assert r.returncode == 0, r.stderr
    assert out_json.exists() and out_md.exists()


@pytest.mark.parametrize("rel", LOCAL_ONLY)
def test_index_file_is_local_only(rel):
    assert _git("ls-files", "--error-unmatch", rel).returncode != 0, rel
    assert _git("check-ignore", "-q", "--no-index", rel).returncode == 0, rel


def test_name_bearing_memory_snapshots_are_gone():
    """No tracked snapshot file NAME carries an identifier. The names are known
    only to the private list, so this runs where one is available."""
    spec = importlib.util.spec_from_file_location(
        "_c20_pr", ROOT / "scripts" / "legal" / "public_redaction.py")
    pr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pr)
    red = pr.load_redactor()
    ci = pr._gate()
    if not (os.environ.get(ci.PRIVATE_ENV) or os.path.isfile(ci.DEFAULT_PRIVATE)):
        pytest.skip("no private deny list available")
    listed = _git("ls-files", "config/agents").stdout.splitlines()
    bearing = [p for p in listed if red.redact(Path(p).name) != Path(p).name]
    assert bearing == [], f"{len(bearing)} tracked file name(s) carry an identifier"
