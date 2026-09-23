"""Captured Git-tree and bootstrap security tests for scheduler equivalence."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_HELPER = ROOT / "scripts/lib/git_index_snapshot.py"


def load_snapshot_helper():
    spec = importlib.util.spec_from_file_location("git_index_snapshot_test", SNAPSHOT_HELPER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_post_capture_index_mutation_uses_captured_oids(tmp_path):
    helper = load_snapshot_helper()
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    payload = repo / "payload.txt"
    payload.write_text("captured\n", encoding="utf-8")
    subprocess.run(["git", "add", "payload.txt"], cwd=repo, check=True)
    tree_oid = subprocess.check_output(["git", "write-tree"], cwd=repo, text=True).strip()
    snapshot = helper.capture_tree(repo, tree_oid)
    payload.write_text("later\n", encoding="utf-8")
    subprocess.run(["git", "add", "payload.txt"], cwd=repo, check=True)
    assert snapshot.read_blob("payload.txt") == b"captured\n"


def _two_tree_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True)
    tree_a = subprocess.check_output(["git", "write-tree"], cwd=repo, text=True).strip()
    subprocess.run(["git", "rm", "-q", "--cached", "a.txt"], cwd=repo, check=True)
    (repo / "b.txt").write_text("b\n", encoding="utf-8")
    subprocess.run(["git", "add", "b.txt"], cwd=repo, check=True)
    tree_b = subprocess.check_output(["git", "write-tree"], cwd=repo, text=True).strip()
    return repo, tree_a, tree_b


def test_capture_tree_ignores_git_replace_refs(tmp_path):
    helper = load_snapshot_helper()
    repo, tree_a, tree_b = _two_tree_repo(tmp_path)
    subprocess.run(["git", "replace", tree_a, tree_b], cwd=repo, check=True)
    snapshot = helper.capture_tree(repo, tree_a)
    assert "a.txt" in snapshot.entries
    assert "b.txt" not in snapshot.entries


def test_frozen_index_is_built_from_captured_manifest(tmp_path):
    helper = load_snapshot_helper()
    repo, tree_a, tree_b = _two_tree_repo(tmp_path)
    snapshot = helper.capture_tree(repo, tree_a)
    subprocess.run(["git", "replace", tree_a, tree_b], cwd=repo, check=True)
    root = tmp_path / "isolated"
    root.mkdir()
    env = helper._frozen_git_env(snapshot, root, root / "index")
    paths = subprocess.check_output(
        ["git", "ls-files"], cwd=root, env=env, text=True
    ).splitlines()
    assert paths == ["a.txt"]


@pytest.mark.parametrize("staged_poison", [False, True])
def test_canonical_bootstrap_uses_captured_tree_not_working_files(
    tmp_path, staged_poison
):
    repo = tmp_path / "clone"
    subprocess.run(
        ["git", "-c", "core.longpaths=true", "clone", "-q", "--no-hardlinks",
         str(ROOT), str(repo)], check=True
    )
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=repo, check=True)
    helper_path = repo / "scripts/lib/git_index_snapshot.py"
    poison = b"\nraise SystemExit(97)\n"
    if staged_poison:
        helper_path.write_bytes(helper_path.read_bytes() + poison)
        subprocess.run(["git", "add", "scripts/lib/git_index_snapshot.py"], cwd=repo, check=True)
        clean = subprocess.check_output(
            ["git", "show", "HEAD:scripts/lib/git_index_snapshot.py"], cwd=repo
        )
        helper_path.write_bytes(clean)
    else:
        helper_path.write_bytes(helper_path.read_bytes() + poison)
    workflow = yaml.load(
        (repo / ".github/workflows/scheduler-mutation-main.yml").read_text(),
        Loader=yaml.BaseLoader,
    )
    command = next(
        step["run"] for step in workflow["jobs"]["scheduler-mutation-surfaces"]["steps"]
        if "run" in step
    )
    needle = "git --no-replace-objects rev-parse 'HEAD^{tree}'"
    command = command.replace(needle, "git --no-replace-objects write-tree")
    hostile = tmp_path / "hostile"
    hostile.mkdir()
    sentinel = tmp_path / "python-customization-ran"
    (hostile / "sitecustomize.py").write_text(
        f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('ran')\n",
        encoding="utf-8",
    )
    env = dict(os.environ, PYTHONPATH=str(hostile))
    hostile_uv_env = tmp_path / "hostile-uv-environment"
    env["UV_PROJECT_ENVIRONMENT"] = str(hostile_uv_env)
    env["UV_PYTHON"] = str(tmp_path / "attacker-python-does-not-exist")
    completed = subprocess.run(["bash", "-c", command], cwd=repo, env=env)
    assert completed.returncode == (1 if staged_poison else 0)
    assert not sentinel.exists()
    assert not hostile_uv_env.exists()


@pytest.mark.parametrize(
    "path",
    ["../escape", "/absolute", "C:/drive", "//server/share", "dir\\alias",
     "CON/file.txt", "trailing./file", "dir/file:stream", "dir/file?.txt",
     "dir/control\x01.txt", "COM¹.txt", "LPT².log"],
)
def test_materialization_rejects_unsafe_paths(path):
    helper = load_snapshot_helper()
    entry = helper.Entry("100644", "0" * 40, path)
    with pytest.raises(helper.SnapshotError):
        helper.validate_materialization_entries([entry])


@pytest.mark.parametrize(
    "paths",
    [("Dir/file.txt", "dir/FILE.txt"), ("node", "node/child")],
)
def test_materialization_rejects_collisions(paths):
    helper = load_snapshot_helper()
    entries = [helper.Entry("100644", str(index) * 40, path)
               for index, path in enumerate(paths)]
    with pytest.raises(helper.SnapshotError):
        helper.validate_materialization_entries(entries)
