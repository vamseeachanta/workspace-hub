"""Tests for scripts/hygiene/cleanup_plan.py (#4532).

Includes one regression per finding of the Codex review of PR #4533.
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/hygiene/cleanup_plan.py"
GB = 1024 ** 3
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
CLEAN_ENV.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
                 GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")


def load():
    spec = importlib.util.spec_from_file_location("cleanup_plan", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cp():
    return load()


def doc(**kw):
    base = {"schema": 1, "label": "h", "os": "Linux", "generated_utc": "2026-11-25T00:00:00Z",
            "home": "/h", "disks": [], "roots": [], "stray": [], "caches": [], "checkouts": []}
    base.update(kw)
    return base


def tiers(items):
    return {i["path"]: i["tier"] for i in items}


CO = {"branch": "b", "stashes": 0, "locked": False, "origin": "u", "dirty": 0,
      "ignored_other": 0, "head": "a" * 40, "head_on_remote": True, "kind": "worktree"}


def test_cache_tiers(cp):
    d = doc(caches=[{"name": "uv", "path": "/h/.cache/uv", "bytes": 5 * GB},
                    {"name": "huggingface", "path": "/h/.cache/huggingface", "bytes": 9 * GB},
                    {"name": "yarn", "path": "/h/Library/Caches/Yarn", "bytes": 2 * GB},
                    {"name": "temp-dir", "path": "/tmp", "bytes": 1 * GB}])
    t = tiers(cp.plan(d, own_roots=["/w"]))
    assert t["/h/.cache/uv"] == "regenerable"
    assert t["/h/.cache/huggingface"] == "review"
    assert t["/h/Library/Caches/Yarn"] == "review"  # no path-bound clean command
    assert "/tmp" not in t


def test_other_users_pytest_root_is_never_regenerable(cp):
    d = doc(caches=[{"name": "pytest-tmp", "path": "/tmp/pytest-of-other", "bytes": GB,
                     "newest_utc": "2026-01-01T00:00:00Z"}])
    assert tiers(cp.plan(d, own_roots=["/w"]))["/tmp/pytest-of-other"] == "other-tenant"


def test_recent_pytest_root_is_review(cp):
    d = doc(caches=[{"name": "pytest-tmp", "path": "/h/tmp/pytest-of-me", "bytes": GB,
                     "newest_utc": "2026-11-24T20:00:00Z"}])
    assert tiers(cp.plan(d, own_roots=["/w"]))["/h/tmp/pytest-of-me"] == "review"


def test_checkout_tiers(cp):
    d = doc(checkouts=[
        {**CO, "path": "/w/_wt/clean"},
        {**CO, "path": "/w/_wt/dirty", "dirty": 3},
        {**CO, "path": "/w/_wt/local", "head_on_remote": False},
        {**CO, "path": "/w/_wt/locked", "locked": True},
        {**CO, "path": "/w/_wt/ignored", "ignored_other": 1, "ignored_sample": ["raw.bin"]},
        {**{k: v for k, v in CO.items() if k != "ignored_other"}, "path": "/w/_wt/unknown"},
        {**CO, "path": "/w/repo", "kind": "clone"},
    ])
    t = tiers(cp.plan(d, own_roots=["/w"]))
    assert t["/w/_wt/clean"] == "safe-checkout"
    assert t["/w/_wt/dirty"] == "review"
    assert t["/w/_wt/local"] == "review"
    assert t["/w/_wt/locked"] == "keep"
    assert t["/w/_wt/ignored"] == "review"   # ignored measurement protects the checkout
    assert t["/w/_wt/unknown"] == "review"   # missing evidence is not clean
    assert "/w/repo" not in t


def test_traversal_and_relative_paths_are_not_safe(cp):
    d = doc(checkouts=[{**CO, "path": "/w/../other/wt"}, {**CO, "path": "w/rel"}])
    t = tiers(cp.plan(d, own_roots=["/w"]))
    assert t["/w/../other/wt"] == "review"
    assert t["w/rel"] == "review"


def test_posix_backslash_is_literal(cp):
    d = doc(checkouts=[{**CO, "path": "/w\\x"}])
    assert tiers(cp.plan(d, own_roots=["/w"]))["/w\\x"] == "other-tenant"


def test_preserved_head_counts_as_archived(cp):
    d = doc(checkouts=[{**CO, "path": "/w/_wt/old", "head_on_remote": False}])
    items = cp.plan(d, own_roots=["/w"], preserved={"a" * 40})
    assert items[0]["tier"] == "safe-checkout" and "archive" in items[0]["reason"]


def test_paths_outside_own_roots_are_other_tenant(cp):
    d = doc(os="Windows", home="C:/Users/me",
            stray=[{"path": "C:/CM_Projects", "reason": "unclassified", "bytes": 4 * GB},
                   {"path": "C:/tmp", "reason": "posix-path-leak", "bytes": 2 * GB}])
    t = tiers(cp.plan(d, own_roots=["C:/tmp", "D:/ws"]))
    assert t["C:/CM_Projects"] == "other-tenant"
    assert t["C:/tmp"] == "review"


def test_tracked_data_inside_a_clean_clone_is_not_called_untracked(cp):
    old = "2026-01-01T00:00:00Z"
    d = doc(checkouts=[{**CO, "path": "/w/repo", "kind": "clone"}],
            roots=[{"root": "/w", "dirs": [
                {"path": "/w/repo/data", "depth": 2, "bytes": 12 * GB, "git": "",
                 "newest_utc": old, "denied": 0},
                {"path": "/w/loose", "depth": 1, "bytes": 12 * GB, "git": "",
                 "newest_utc": old, "denied": 0},
                {"path": "/w/partial", "depth": 1, "bytes": 12 * GB, "git": "",
                 "newest_utc": old, "denied": 3}]}])
    t = tiers(cp.plan(d, own_roots=["/w"]))
    assert "/w/repo/data" not in t
    assert t["/w/loose"] == "review"
    assert "/w/partial" not in t  # an incomplete scan cannot support an idle claim


def test_git_bindings_are_removed_from_apply_environment(monkeypatch):
    monkeypatch.setenv("GIT_DIR", "/somewhere/else")
    monkeypatch.setenv("GIT_INDEX_FILE", "/somewhere/index")
    mod = load()
    assert "GIT_DIR" not in mod.GIT_ENV and "GIT_INDEX_FILE" not in mod.GIT_ENV


def test_cache_commands_are_bound_to_the_planned_path(cp, tmp_path):
    cmd, env = cp.cache_command("pip", str(tmp_path))
    assert env["PIP_CACHE_DIR"] == str(tmp_path)
    cmd, _ = cp.cache_command("uv", str(tmp_path))
    if cmd:
        assert cmd[-2:] == ["--cache-dir", str(tmp_path)]
    cmd, _ = cp.cache_command("yarn", str(tmp_path))
    assert cmd is None


def test_guarded_rmtree_does_not_follow_links(cp, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.txt").write_text("k", encoding="utf-8")
    victim = tmp_path / "pytest-of-me"
    (victim / "run").mkdir(parents=True)
    (victim / "run" / "f").write_text("x", encoding="utf-8")
    try:
        os.symlink(outside, victim / "run" / "link", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted")
    result, _ = cp.guarded_rmtree(str(victim))
    assert result == "removed"
    assert not victim.exists()
    assert (outside / "keep.txt").exists()


# ---------------------------------------------------------------- apply integration

def g(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, env=CLEAN_ENV, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@pytest.fixture
def pushed_worktree(tmp_path, cp):
    if subprocess.run(["git", "--version"], capture_output=True).returncode:
        pytest.skip("git unavailable")
    origin = tmp_path / "origin.git"
    g("init", "--bare", "-q", "-b", "main", str(origin), cwd=tmp_path)
    repo = tmp_path / "repo"
    g("init", "-q", "-b", "main", str(repo), cwd=tmp_path)
    (repo / "a").write_text("a", encoding="utf-8")
    g("add", "a", cwd=repo)
    g("commit", "-qm", "1", cwd=repo)
    g("remote", "add", "origin", str(origin), cwd=repo)
    g("push", "-q", "origin", "main", cwd=repo)
    g("fetch", "-q", "origin", cwd=repo)
    wt = tmp_path / "wt"
    g("worktree", "add", "-q", "--detach", str(wt), "main", cwd=repo)
    head = subprocess.run(["git", "-C", str(wt), "rev-parse", "HEAD"], env=CLEAN_ENV,
                          capture_output=True, text=True, check=True).stdout.strip()
    return tmp_path, wt, head


def run_apply(tmp_path, d, *extra):
    p = tmp_path / "b.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    log = tmp_path / "log.jsonl"
    proc = subprocess.run([sys.executable, "-I", str(SCRIPT), str(p), "--own-roots",
                           tmp_path.as_posix(), "--apply", "--tiers", "safe-checkout",
                           "--this-host", d["label"], "--log", str(log), *extra],
                          capture_output=True, text=True, env=CLEAN_ENV)
    recs = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    return proc, recs


def wt_doc(cp, wt, head, **kw):
    return doc(label="me", host_id=cp.HB.host_id(), home=None, os=cp.HB.platform.system(),
               checkouts=[{**CO, "path": wt.as_posix(), "head": head, **kw}])


def test_apply_refuses_label_or_host_mismatch(tmp_path, cp):
    proc, _ = run_apply(tmp_path, doc(label="x", host_id="0" * 16))
    assert proc.returncode == 2 and "host_id" in proc.stderr
    p = tmp_path / "c.json"
    p.write_text(json.dumps(doc(label="other")), encoding="utf-8")
    proc = subprocess.run([sys.executable, "-I", str(SCRIPT), str(p), "--own-roots", "/w",
                           "--apply", "--this-host", "me", "--log", str(tmp_path / "l")],
                          capture_output=True, text=True)
    assert proc.returncode == 2 and "label" in proc.stderr


def test_apply_removes_verified_clean_worktree(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    proc, recs = run_apply(tmp_path, wt_doc(cp, wt, head))
    assert proc.returncode == 0, proc.stderr
    assert recs[-1]["result"] == "removed", recs
    assert not wt.exists()


def test_apply_refuses_when_head_moved_after_plan(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    (wt / "b").write_text("b", encoding="utf-8")
    g("add", "b", cwd=wt)
    g("commit", "-qm", "local only", cwd=wt)
    proc, recs = run_apply(tmp_path, wt_doc(cp, wt, head))
    assert recs[-1]["result"] == "refused" and wt.exists()


def test_apply_refuses_ignored_measurement(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    (wt / ".gitignore").write_text("measurements/\n", encoding="utf-8")
    g("add", ".gitignore", cwd=wt)
    g("commit", "-qm", "ignore", cwd=wt)
    g("push", "-q", "origin", "HEAD:refs/heads/ign", cwd=wt)
    head = subprocess.run(["git", "-C", str(wt), "rev-parse", "HEAD"], env=CLEAN_ENV,
                          capture_output=True, text=True, check=True).stdout.strip()
    (wt / "measurements").mkdir()
    (wt / "measurements" / "raw.bin").write_bytes(b"only copy")
    proc, recs = run_apply(tmp_path, wt_doc(cp, wt, head))
    assert recs[-1]["result"] == "refused", recs
    assert (wt / "measurements" / "raw.bin").exists()


def test_apply_refuses_head_absent_from_remote(pushed_worktree, cp):
    tmp_path, wt, _ = pushed_worktree
    (wt / "c").write_text("c", encoding="utf-8")
    g("add", "c", cwd=wt)
    g("commit", "-qm", "unpushed", cwd=wt)
    head = subprocess.run(["git", "-C", str(wt), "rev-parse", "HEAD"], env=CLEAN_ENV,
                          capture_output=True, text=True, check=True).stdout.strip()
    # A stale plan that claims the head is on the remote must still be refused.
    proc, recs = run_apply(tmp_path, wt_doc(cp, wt, head))
    assert recs[-1]["result"] == "refused" and wt.exists()
