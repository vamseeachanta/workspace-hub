"""Tests for scripts/hygiene/cleanup_plan.py (#4532)."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/hygiene/cleanup_plan.py"
GB = 1024 ** 3


def load():
    spec = importlib.util.spec_from_file_location("cleanup_plan", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def doc(**kw):
    base = {"schema": 1, "label": "h", "os": "Linux", "generated_utc": "2026-11-25T00:00:00Z",
            "disks": [], "roots": [], "stray": [], "caches": [], "checkouts": []}
    base.update(kw)
    return base


def tiers(items):
    return {i["path"]: i["tier"] for i in items}


def test_package_caches_are_regenerable_model_caches_are_review():
    cp = load()
    d = doc(caches=[{"name": "uv", "path": "/h/.cache/uv", "bytes": 5 * GB},
                    {"name": "huggingface", "path": "/h/.cache/huggingface", "bytes": 9 * GB},
                    {"name": "temp-dir", "path": "/tmp", "bytes": 1 * GB}])
    t = tiers(cp.plan(d, own_roots=["/h"]))
    assert t["/h/.cache/uv"] == "regenerable"
    assert t["/h/.cache/huggingface"] == "review"
    assert "/tmp" not in t  # the whole temp dir is never a cleanup target


def test_checkout_tiers():
    cp = load()
    base = {"branch": "b", "stashes": 0, "locked": False, "origin": "u"}
    d = doc(checkouts=[
        {**base, "path": "/w/_wt/clean", "kind": "worktree", "dirty": 0, "head_on_remote": True},
        {**base, "path": "/w/_wt/dirty", "kind": "worktree", "dirty": 3, "head_on_remote": True},
        {**base, "path": "/w/_wt/local", "kind": "worktree", "dirty": 0, "head_on_remote": False},
        {**base, "path": "/w/_wt/locked", "kind": "worktree", "dirty": 0, "head_on_remote": True,
         "locked": True},
        {**base, "path": "/w/repo", "kind": "clone", "dirty": 0, "head_on_remote": True},
    ])
    t = tiers(cp.plan(d, own_roots=["/w"]))
    assert t["/w/_wt/clean"] == "safe-checkout"
    assert t["/w/_wt/dirty"] == "review"
    assert t["/w/_wt/local"] == "review"
    assert t["/w/_wt/locked"] == "keep"
    assert "/w/repo" not in t  # canonical clones are kept and not listed


def test_preserved_head_is_reported_as_archived_not_unpushed():
    cp = load()
    d = doc(checkouts=[{"path": "/w/_wt/old", "kind": "worktree", "dirty": 0,
                        "head_on_remote": False, "head": "abc123", "locked": False}])
    items = cp.plan(d, own_roots=["/w"], preserved={"abc123"})
    assert items[0]["tier"] == "safe-checkout"
    assert "archive" in items[0]["reason"]


def test_paths_outside_own_roots_are_other_tenant():
    cp = load()
    d = doc(stray=[{"path": "C:/CM_Projects", "reason": "unclassified", "bytes": 4 * GB},
                   {"path": "C:/tmp", "reason": "posix-path-leak", "bytes": 2 * GB}],
            os="Windows")
    t = tiers(cp.plan(d, own_roots=["C:/tmp", "D:/ws"]))
    assert t["C:/CM_Projects"] == "other-tenant"
    assert t["C:/tmp"] == "review"


def test_apply_refuses_when_label_differs(tmp_path):
    d = doc(label="other-host")
    p = tmp_path / "b.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    proc = subprocess.run([sys.executable, "-I", str(SCRIPT), str(p), "--own-roots", "/w",
                           "--apply", "--this-host", "me", "--log", str(tmp_path / "log.jsonl")],
                          capture_output=True, text=True)
    assert proc.returncode == 2
    assert "label" in proc.stderr


def test_apply_removes_clean_worktree_and_logs(tmp_path):
    if subprocess.run(["git", "--version"], capture_output=True).returncode:
        pytest.skip("git unavailable")
    repo = tmp_path / "repo"
    env_args = ["-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    (repo / "a").write_text("a", encoding="utf-8")
    subprocess.run(["git", *env_args, "-C", str(repo), "add", "a"], check=True)
    subprocess.run(["git", *env_args, "-C", str(repo), "commit", "-qm", "1"], check=True)
    wt = tmp_path / "wt"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", str(wt)], check=True)
    d = doc(label="me", checkouts=[{"path": wt.as_posix(), "kind": "worktree", "dirty": 0,
                                    "head_on_remote": True, "locked": False}])
    p = tmp_path / "b.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    log = tmp_path / "log.jsonl"
    proc = subprocess.run([sys.executable, "-I", str(SCRIPT), str(p), "--own-roots",
                           tmp_path.as_posix(), "--apply", "--tiers", "safe-checkout",
                           "--this-host", "me", "--log", str(log)],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert not wt.exists()
    rec = json.loads(log.read_text(encoding="utf-8").splitlines()[-1])
    assert rec["path"] == wt.as_posix() and rec["result"] == "removed"
