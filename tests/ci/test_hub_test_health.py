"""Collection-only examples: counts are literal functions in synthetic files.

Timeouts are test inputs, not engineering acceptance limits. Collection must
never execute a body (pytest usage documentation, accessed 2026-10-22).
"""

import importlib.util
import json
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/ci/hub_test_health.py"


def run_probe(tmp_path, code):
    root = tmp_path / "repo"
    root.mkdir()
    path = root / "test_sample.py"
    path.write_text(code, encoding="utf-8", newline="\n")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    command = [sys.executable, "-I", str(SCRIPT), "probe", "--root", str(root),
               "--scratch", str(scratch), "--result", str(scratch / "result.json"),
               "--files", "test_sample.py"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return result, json.loads((scratch / "result.json").read_text(encoding="utf-8"))


def test_collection_does_not_run_bodies(tmp_path):
    """Two literal test functions collect; raising bodies cannot run."""
    result, data = run_probe(tmp_path,
        "def test_one():\n    raise AssertionError('body ran')\n"
        "def test_two():\n    raise AssertionError('body ran')\n")
    assert result.returncode == 0
    assert data["collected"] == 2
    assert data["collection_status"] == "COLLECTABLE"


def test_collection_error_is_not_gating(tmp_path):
    _, data = run_probe(tmp_path, "import nonexistent_synthetic_dependency\n")
    assert data["collection_status"] == "NOT_GATING"
    assert "No module named 'nonexistent_synthetic_dependency'" in data["error"]


def test_collection_blocks_import_side_effects(tmp_path):
    """A top-level write outside scratch is denied before changing the tree."""
    _, data = run_probe(tmp_path, "from pathlib import Path\nPath('marker').write_text('bad', encoding='utf-8', newline=chr(10))\n")
    assert data["collection_status"] == "NOT_GATING"
    assert not (tmp_path / "repo/marker").exists()


def test_collection_blocks_network_and_processes(tmp_path):
    _, data = run_probe(tmp_path,
        "import subprocess\nsubprocess.run(['unavailable-command'])\n")
    assert data["collection_status"] == "NOT_GATING"
    assert "collection guard" in data["error"]


def test_resume_cache_and_required_timeout(tmp_path):
    spec = importlib.util.spec_from_file_location("hub_health", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cached = {"digest": "same", "collected": 2, "collection_status": "COLLECTABLE", "error": ""}
    path = tmp_path / "cached.json"
    path.write_text(json.dumps(cached), encoding="utf-8", newline="\n")
    assert module.cached_result(path, "same") == cached
    assert module.cached_result(path, "different") is None
    result = subprocess.run([sys.executable, "-I", str(SCRIPT), "generate"], capture_output=True, check=False)
    assert result.returncode != 0


def test_body_policy_defaults_to_not_evaluated(tmp_path):
    spec = importlib.util.spec_from_file_location("hub_health", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    policy = {"body_evaluated": ["tests/ci"], "comment": "Only synthetic CI tests reviewed."}
    assert module.body_status("tests/cron", policy) == "NOT_EVALUATED"
    assert module.body_status("tests/ci", policy) == "EVALUATED"


def test_timeout_returns_non_gating_result(tmp_path):
    spec = importlib.util.spec_from_file_location("hub_health", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    result = module.collect_family(tmp_path, ["test_sample.py"], tmp_path / "probe", 1, runner=timeout)
    assert result["collection_status"] == "NOT_GATING"
    assert result["collected"] is None
    assert "timeout" in result["error"]


@pytest.mark.parametrize("method", ["posix_spawn", "posix_spawnp"])
def test_collection_blocks_posix_spawn(tmp_path, method):
    if not hasattr(__import__("os"), method):
        pytest.skip(f"os.{method} is unavailable on this platform")
    _, data = run_probe(tmp_path,
        "import os, sys\n"
        "code = \"from pathlib import Path; Path('child-marker').write_text('ran', "
        "encoding='utf-8', newline=chr(10))\"\n"
        f"pid = os.{method}(sys.executable, [sys.executable, '-c', code], os.environ)\n"
        "os.waitpid(pid, 0)\n"
        "def test_one(): pass\n")
    assert not (tmp_path / "repo/child-marker").exists()
    assert data["collection_status"] == "NOT_GATING"
    assert "collection guard" in data["error"]


@pytest.mark.parametrize("location", ["scripts", "scripts/linked"])
def test_digest_ignores_directory_junctions(tmp_path, monkeypatch, location):
    spec = importlib.util.spec_from_file_location("hub_health", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    directory = tmp_path / location
    directory.mkdir(parents=True)
    payload = directory / "payload.py"
    payload.write_text("before", encoding="utf-8", newline="\n")
    original_lstat = Path.lstat
    monkeypatch.setattr(Path, "lstat", lambda path: SimpleNamespace(
        st_mode=stat.S_IFDIR, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
        if path == directory else original_lstat(path))
    before = module.input_digest(tmp_path, {}, {}, 1)
    payload.write_text("after", encoding="utf-8", newline="\n")
    assert module.input_digest(tmp_path, {}, {}, 1) == before
    ordinary = tmp_path / "src" / "ordinary.py"
    ordinary.parent.mkdir()
    ordinary.write_text("included", encoding="utf-8", newline="\n")
    assert module.input_digest(tmp_path, {}, {}, 1) != before
