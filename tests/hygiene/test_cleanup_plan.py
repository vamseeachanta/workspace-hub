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
      "ignored_other": 0, "head": "a" * 40, "head_on_remote": True, "kind": "worktree",
      "hidden_state": [], "unpublished_commits": 0}


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


def test_own_pytest_root_is_never_applied(cp):
    d = doc(caches=[{"name": "pytest-tmp", "path": "/h/tmp/pytest-of-me", "bytes": GB,
                     "newest_utc": "2026-01-01T00:00:00Z"}])
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


def test_untracked_data_advice_needs_positive_evidence(cp):
    old = "2026-01-01T00:00:00Z"

    def row(path, depth=1, denied=0):
        return {"path": path, "depth": depth, "bytes": 12 * GB, "git": "",
                "newest_utc": old, "denied": denied}

    roots = [{"root": "/w", "dirs": [row("/w/repo/data", 2), row("/w/loose"),
                                     row("/w/partial", denied=3), row("/w/_wt")]}]
    checkouts = [{**CO, "path": "/w/repo", "kind": "clone"},
                 {**CO, "path": "/w/_wt/one", "dirty": 2}]
    d = doc(checkouts=checkouts, roots=roots,
            git_scan={"done": True, "roots": ["/w"], "depth": 3})
    t = tiers(cp.plan(d, own_roots=["/w"]))
    assert "/w/repo/data" not in t   # inside a checkout: may be tracked
    assert t["/w/loose"] == "review"
    assert "/w/partial" not in t     # incomplete scan cannot support an idle claim
    assert "large idle folder" in {i["path"]: i["reason"] for i in
                                   cp.plan(d, own_roots=["/w"])}["/w/loose"]
    assert not any(i["path"] == "/w/_wt" and "large idle folder" in i["reason"]
                   for i in cp.plan(d, own_roots=["/w"]))  # it holds checkouts
    # Without git discovery there is no evidence at all.
    d_nogit = doc(roots=roots, git_scan={"done": False, "roots": [], "depth": 3})
    assert not [i for i in cp.plan(d_nogit, own_roots=["/w"])
                if "large idle folder" in i["reason"]]


def test_git_bindings_are_removed_from_apply_environment(monkeypatch):
    monkeypatch.setenv("GIT_DIR", "/somewhere/else")
    monkeypatch.setenv("GIT_INDEX_FILE", "/somewhere/index")
    mod = load()
    assert "GIT_DIR" not in mod.GIT_ENV and "GIT_INDEX_FILE" not in mod.GIT_ENV


def test_only_uv_is_applied_and_bound_to_the_planned_path(cp, tmp_path):
    cmd, _ = cp.cache_command("uv", str(tmp_path))
    if cmd:
        assert cmd[2] == "prune" and cmd[-2:] == ["--cache-dir", str(tmp_path)]
    for name in ("pip", "npm", "yarn"):
        assert cp.cache_command(name, str(tmp_path))[0] is None
    d = doc(caches=[{"name": "pip", "path": "/h/.cache/pip", "bytes": 2 * GB},
                    {"name": "npm", "path": "/h/.npm/_cacache", "bytes": 2 * GB}])
    assert set(tiers(cp.plan(d, own_roots=["/w"])).values()) == {"review"}


def test_uv_cache_with_linked_entry_is_refused(cp, tmp_path):
    cache = tmp_path / "uv"
    (cache / "wheels-v5").mkdir(parents=True)
    other = tmp_path / "other-team"
    other.mkdir()
    try:
        os.symlink(other, cache / "archive-v0", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted")
    result, detail = cp.apply_item({"tier": "regenerable", "path": str(cache), "cache": "uv"},
                                   set(), 48)
    assert result == "refused" and "link" in detail


def test_min_idle_hours_must_be_finite_and_nonnegative(tmp_path):
    p = tmp_path / "b.json"
    p.write_text(json.dumps(doc()), encoding="utf-8")
    for bad in ("nan", "inf", "-1"):
        proc = subprocess.run([sys.executable, "-I", str(SCRIPT), str(p), "--own-roots", "/w",
                               "--min-idle-hours", bad], capture_output=True, text=True)
        assert proc.returncode == 2, bad


def test_clone_with_unpublished_branch_or_hidden_state_is_listed(cp):
    d = doc(checkouts=[{**CO, "path": "/w/a", "kind": "clone", "unpublished_commits": 3},
                       {**CO, "path": "/w/b", "kind": "clone",
                        "hidden_state": ["operation in progress: rebase-merge"]},
                       {**CO, "path": "/w/_wt/c", "hidden_state": ["1 assume-unchanged/"
                                                                   "skip-worktree index entries"]}])
    t = tiers(cp.plan(d, own_roots=["/w"]))
    assert t == {"/w/a": "review", "/w/b": "review", "/w/_wt/c": "review"}


def test_out_never_overwrites(cp, tmp_path):
    base = tmp_path / "b.json"
    base.write_text(json.dumps(doc()), encoding="utf-8")
    proc = subprocess.run([sys.executable, "-I", str(SCRIPT), str(base), "--own-roots", "/w",
                           "--out", str(base)], capture_output=True, text=True)
    assert proc.returncode == 2
    assert json.loads(base.read_text(encoding="utf-8"))["schema"] == 1


def test_no_recursive_delete_helper_exists(cp):
    # Recursive deletion was removed from apply on review; keep it that way.
    assert not hasattr(cp, "guarded_rmtree")


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
                           "--this-host", d["label"], "--log", str(log),
                           # fixtures are seconds old; a later --min-idle-hours in
                           # `extra` overrides this (argparse keeps the last value)
                           "--min-idle-hours", "0", *extra],
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
    leftover = subprocess.run(["git", "-C", str(tmp_path / "repo"), "for-each-ref",
                               "refs/hygiene-verify"], env=CLEAN_ENV, capture_output=True,
                              text=True, check=True).stdout
    assert leftover.strip() == ""  # the private verification namespace is cleaned up


def test_stale_remote_tracking_ref_cannot_vouch(pushed_worktree, cp):
    tmp_path, wt, _ = pushed_worktree
    (wt / "t").write_text("t", encoding="utf-8")
    g("add", "t", cwd=wt)
    g("commit", "-qm", "topic", cwd=wt)
    g("push", "-q", "origin", "HEAD:refs/heads/topic", cwd=wt)
    g("fetch", "-q", "origin", cwd=tmp_path / "repo")          # origin/topic now local
    g("--git-dir", str(tmp_path / "origin.git"), "update-ref", "-d", "refs/heads/topic",
      cwd=tmp_path)                                             # deleted on the remote only
    head = subprocess.run(["git", "-C", str(wt), "rev-parse", "HEAD"], env=CLEAN_ENV,
                          capture_output=True, text=True, check=True).stdout.strip()
    proc, recs = run_apply(tmp_path, wt_doc(cp, wt, head))
    assert recs[-1]["result"] == "refused", recs
    assert wt.exists()


def test_apply_refuses_recently_active_worktree(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    proc, recs = run_apply(tmp_path, wt_doc(cp, wt, head), "--min-idle-hours", "48")
    assert recs[-1]["result"] == "refused" and "recently active" in recs[-1]["detail"]
    assert wt.exists()


# Idle tests: creation time cannot be backdated, so instead of faking age the tests set
# everything up, wait SETTLE seconds, make the one write under test, and check with a
# minimum idle time of MIN_IDLE_S. Anything older than the pause is idle; the write is not.
SETTLE = 2.5
MIN_IDLE_S = 1.5
MIN_IDLE_H = str(MIN_IDLE_S / 3600)


def settle():
    __import__("time").sleep(SETTLE)


def test_idle_worktree_is_removed(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    settle()
    proc, recs = run_apply(tmp_path, wt_doc(cp, wt, head), "--min-idle-hours", MIN_IDLE_H)
    assert recs[-1]["result"] == "removed", recs


def test_nested_ignored_activity_counts(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    (wt / ".gitignore").write_text(".pytest_cache/\n", encoding="utf-8")
    g("add", ".gitignore", cwd=wt)
    g("commit", "-qm", "ignore", cwd=wt)
    g("push", "-q", "origin", "HEAD:refs/heads/main", cwd=wt)
    head = subprocess.run(["git", "-C", str(wt), "rev-parse", "HEAD"], env=CLEAN_ENV,
                          capture_output=True, text=True, check=True).stdout.strip()
    nested = wt / ".pytest_cache" / "v" / "cache" / "nodeids"
    nested.parent.mkdir(parents=True)
    nested.write_text("[]", encoding="utf-8")
    settle()
    with open(nested, "a", encoding="utf-8") as fh:  # a job appends deep inside, now;
        fh.write("[1]")                                # no folder mtime changes
    proc, recs = run_apply(tmp_path, wt_doc(cp, wt, head), "--min-idle-hours", MIN_IDLE_H)
    assert recs[-1]["result"] == "refused" and "recently active" in recs[-1]["detail"]


def test_activity_inside_nested_git_folder_counts(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    trace = wt / "scratch" / "fixture" / ".git" / "trace"
    trace.parent.mkdir(parents=True)
    trace.write_text("start", encoding="utf-8")
    settle()
    assert cp.check_idle(str(wt), str(wt), MIN_IDLE_S / 3600) is None   # idle before
    with open(trace, "a", encoding="utf-8") as fh:                     # append: only
        fh.write(" more")                                              # the file moves
    assert cp.check_idle(str(wt), str(wt), MIN_IDLE_S / 3600) is not None


def test_backdated_copy_counts_through_ctime(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    settle()
    f = wt / "copied.bin"
    f.write_bytes(b"x")
    old = __import__("time").time() - 10 * 86400
    os.utime(f, (old, old))                  # like `cp -p`: preserved old mtime
    os.utime(wt, (old, old))                 # and the folder's mtime set old too
    assert cp.check_idle(str(wt), str(wt), MIN_IDLE_S / 3600) is not None


def test_in_place_overwrite_with_restored_mtime_counts(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    f = wt / "cache.bin"
    f.write_bytes(b"old")
    settle()
    assert cp.check_idle(str(wt), str(wt), MIN_IDLE_S / 3600) is None   # idle before
    st = f.stat()
    with open(f, "r+b") as fh:                    # overwrite the EXISTING file in place
        fh.write(b"new")
    os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns))   # ...and restore its old mtime
    assert cp.check_idle(str(wt), str(wt), MIN_IDLE_S / 3600) is not None


@pytest.mark.skipif(os.name != "nt", reason="MAX_PATH applies to the Windows API only")
def test_change_time_reads_paths_longer_than_max_path(tmp_path, cp):
    deep = str(tmp_path)
    while len(deep) < 280:
        deep = os.path.join(deep, "d" * 40)
    long_file = os.path.join(deep, "f.txt")
    assert len(long_file) > 260
    os.makedirs("\\\\?\\" + deep)
    with open("\\\\?\\" + long_file, "w", encoding="utf-8") as fh:
        fh.write("x")
    assert cp._change_time(long_file) > 0


def test_replace_ref_cannot_fake_remote_containment(pushed_worktree, cp):
    tmp_path, wt, _ = pushed_worktree
    repo = tmp_path / "repo"
    (wt / "l").write_text("local only", encoding="utf-8")
    g("add", "l", cwd=wt)
    g("commit", "-qm", "L", cwd=wt)
    local = subprocess.run(["git", "-C", str(wt), "rev-parse", "HEAD"], env=CLEAN_ENV,
                           capture_output=True, text=True, check=True).stdout.strip()
    (repo / "r").write_text("r", encoding="utf-8")
    g("add", "r", cwd=repo)
    g("commit", "-qm", "R", cwd=repo)
    g("push", "-q", "origin", "main", cwd=repo)
    remote_tip = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], env=CLEAN_ENV,
                                capture_output=True, text=True, check=True).stdout.strip()
    g("replace", "--graft", remote_tip, local, cwd=repo)      # local lie: R's parent is L
    proc, recs = run_apply(tmp_path, wt_doc(cp, wt, local))
    assert recs[-1]["result"] == "refused", recs
    assert wt.exists()


def test_apply_refuses_assume_unchanged_edit(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    g("update-index", "--assume-unchanged", "a", cwd=wt)
    (wt / "a").write_text("edited measurement", encoding="utf-8")   # hidden from status
    proc, recs = run_apply(tmp_path, wt_doc(cp, wt, head))
    assert recs[-1]["result"] == "refused", recs
    assert (wt / "a").read_text(encoding="utf-8") == "edited measurement"


def test_apply_refuses_operation_in_progress(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    gd = subprocess.run(["git", "-C", str(wt), "rev-parse", "--absolute-git-dir"],
                        env=CLEAN_ENV, capture_output=True, text=True, check=True).stdout.strip()
    (Path(gd) / "rebase-merge").mkdir()                              # paused rebase state
    proc, recs = run_apply(tmp_path, wt_doc(cp, wt, head))
    assert recs[-1]["result"] == "refused" and "rebase-merge" in recs[-1]["detail"]
    assert wt.exists()


def test_one_failing_item_does_not_stop_the_rest(pushed_worktree, cp):
    tmp_path, wt, head = pushed_worktree
    d = wt_doc(cp, wt, head)
    d["checkouts"].insert(0, {**CO, "path": (tmp_path / "gone").as_posix(), "head": head})
    proc, recs = run_apply(tmp_path, d)
    assert proc.returncode == 0, proc.stderr
    by = {r["path"]: r["result"] for r in recs}
    assert by[(tmp_path / "gone").as_posix()] in ("refused", "error")
    assert by[wt.as_posix()] == "removed"


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
