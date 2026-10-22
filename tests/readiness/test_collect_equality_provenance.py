"""Checkout provenance regressions, independent of collector serialization tests."""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import time
from pathlib import Path

import yaml
from collector_support import (
    BASH_PATH,
    GIT_BINDINGS,
    SCRIPT,
    _fixture,
    collector_env,
)
from collector_support import (
    bash_path as _bash_path,
)

# ── #2851 freshness guard: checkout-provenance block ────────────────────────
MEASURED_PATH = ("scripts", "readiness", "harness-config.yaml")  # in the MEASURED allowlist


def _git(ws: Path, *args: str) -> None:
    """Run a git command in the fixture with deterministic identity."""
    env = {**{k: v for k, v in os.environ.items() if k not in GIT_BINDINGS},
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t" + "@" + "example.test",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t" + "@" + "example.test",
           "HOME": str(ws.parent), "TEST_ROOT": str(ws.parent)}
    subprocess.run(["git", "-C", str(ws), *args], env=collector_env(env), check=True,
                   capture_output=True, timeout=60)


def _git_fixture(tmp_path: Path) -> Path:
    """A WORKSPACE_HUB fixture that is also a committed git repo with an origin/main ref.

    The repo is clean and current → fresh provenance by default. A measured-path file
    (harness-config.yaml) is tracked so dirty-flag tests can toggle it.
    """
    ws = _fixture(tmp_path)
    (ws / "scripts" / "readiness").mkdir(parents=True, exist_ok=True)
    (ws / "scripts" / "readiness" / "harness-config.yaml").write_text("workstations: {}\n")
    _git(ws, "init", "-q", "-b", "main")
    _git(ws, "config", "core.autocrlf", "false")
    _git(ws, "add", "-A")
    _git(ws, "commit", "-q", "-m", "init")
    _git(ws, "update-ref", "refs/remotes/origin/main", "HEAD")   # current with main → behind=0
    return ws


def _stdout_prov(ws: Path, *args: str, env_extra: dict | None = None) -> dict:
    env = {"WORKSPACE_HUB": _bash_path(ws), "PATH": BASH_PATH, "HOME": str(ws.parent)}
    if env_extra:
        env.update(env_extra)
    res = subprocess.run(
        ["bash", _bash_path(SCRIPT), "--stdout", "--machine", "dev-primary", *args],
        env=collector_env(env), capture_output=True, text=True, timeout=60, check=False)
    assert res.returncode == 0, res.stderr
    return yaml.safe_load(res.stdout)["provenance"]


def test_collect_emits_provenance(tmp_path):
    # report carries a top-level provenance block with the four freshness fields
    p = _stdout_prov(_git_fixture(tmp_path))
    assert set(p) >= {"checkout_sha", "dirty", "behind_main", "origin_ref_age_h"}


def test_collect_dirty_false_on_clean(tmp_path):
    # a clean, current checkout → dirty false
    p = _stdout_prov(_git_fixture(tmp_path))
    assert p["dirty"] is False


def test_collect_behind_main_zero_when_current(tmp_path):
    # origin/main ref == HEAD → behind_main 0 (not "unknown")
    p = _stdout_prov(_git_fixture(tmp_path))
    assert p["behind_main"] == 0


def test_collect_dirty_true_on_measured_path(tmp_path):
    # modify a tracked MEASURED-allowlist file → dirty true (BC1)
    ws = _git_fixture(tmp_path)
    (ws.joinpath(*MEASURED_PATH)).write_text("workstations: {dev-primary: {}}\n# changed\n")
    p = _stdout_prov(ws)
    assert p["dirty"] is True


def test_collect_dirty_false_on_unrelated_edit(tmp_path):
    # edit a tracked file OUTSIDE the measured allowlist (.claude/state/*) → dirty FALSE (BC1)
    ws = _git_fixture(tmp_path)
    (ws / ".claude" / "state" / "harness-readiness-dev-primary.yaml").write_text(
        "overall: fail\npass_count: 99\n")        # tracked, but not a measured path
    p = _stdout_prov(ws)
    assert p["dirty"] is False


def test_collect_dirty_false_on_untracked_noise(tmp_path):
    # Untracked cruft (.DS_Store, __pycache__, swap files) inside a MEASURED dir must NOT
    # false-STALE a healthy machine — dirty reflects TRACKED changes only (--untracked-files=no).
    ws = _git_fixture(tmp_path)
    (ws / ".claude" / "skills" / ".DS_Store").write_text("\x00")          # untracked noise
    (ws / "scripts" / "readiness" / "__pycache__").mkdir(exist_ok=True)
    (ws / "scripts" / "readiness" / "__pycache__" / "x.pyc").write_text("x")
    p = _stdout_prov(ws)
    assert p["dirty"] is False


def test_collect_origin_ref_age_recorded(tmp_path):
    # origin_ref_age_h is a number (just-created ref → small, well under the 12h window)
    p = _stdout_prov(_git_fixture(tmp_path))
    assert isinstance(p["origin_ref_age_h"], (int, float))
    assert 0 <= p["origin_ref_age_h"] <= 12


def test_collect_fetch_head_freshness_requires_origin_main_sha_match(tmp_path):
    ws = _git_fixture(tmp_path)
    _git(ws, "commit", "-q", "--allow-empty", "-m", "advance local head")
    head_sha = subprocess.check_output(["git", "-C", str(ws), "rev-parse", "HEAD"], text=True).strip()
    common_dir = subprocess.check_output(
        ["git", "-C", str(ws), "rev-parse", "--git-common-dir"], text=True).strip()
    git_dir = Path(common_dir)
    if not git_dir.is_absolute():
        git_dir = ws / git_dir
    origin_ref = git_dir / "refs" / "remotes" / "origin" / "main"
    fetch_head = git_dir / "FETCH_HEAD"
    fetch_head.write_text(f"{head_sha}\t\tbranch 'main' of https://example.invalid/repo\n")
    stale_time = time.time() - (26 * 3600)
    os.utime(origin_ref, (stale_time, stale_time))

    p = _stdout_prov(ws)
    assert p["ahead_main"] == 1
    assert p["origin_ref_age_h"] >= 24


def test_collect_provenance_unknown_when_not_git(tmp_path):
    # the non-git fixture (no .git) → fail-closed unknowns, never a crash
    p = _stdout_prov(_fixture(tmp_path))
    assert p["checkout_sha"] == "unknown"
    assert p["behind_main"] == "unknown"
    assert p["origin_ref_age_h"] == "unknown"


def test_collect_ahead_main_recorded(tmp_path):
    # ahead_main is emitted; current-with-main fixture → 0 (not "unknown")
    p = _stdout_prov(_git_fixture(tmp_path))
    assert p["ahead_main"] == 0


def test_collect_ahead_main_counts_local_commits(tmp_path):
    # a local commit ahead of origin/main → ahead_main > 0 (the unpushed-checkout case)
    ws = _git_fixture(tmp_path)
    _git(ws, "commit", "-q", "--allow-empty", "-m", "local ahead")   # HEAD ahead, origin/main not moved
    p = _stdout_prov(ws)
    assert p["ahead_main"] == 1
    assert p["behind_main"] == 0


def test_collect_sha_excluded_from_hash(tmp_path):
    # A1: a checkout_sha change ALONE → NO rewrite. To change sha WITHOUT changing ahead/behind
    # (which ARE hashed), advance origin/main in lockstep with HEAD — i.e. a normal pull where
    # local and remote move together. Only checkout_sha differs → canonical payload identical.
    ws = _git_fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-dev-primary.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws.parent)}
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "dev-primary"], env=collector_env(env), timeout=60, check=True)
    first_mtime = out.stat().st_mtime_ns
    _git(ws, "commit", "-q", "--allow-empty", "-m", "advance sha")
    _git(ws, "update-ref", "refs/remotes/origin/main", "HEAD")       # origin advances too → ahead=behind=0
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "dev-primary"], env=collector_env(env), timeout=60, check=True)
    assert out.stat().st_mtime_ns == first_mtime     # only sha changed → must not rewrite


def test_collect_dirty_change_forces_rewrite(tmp_path):
    # A1: a clean→dirty transition (same emitted dims) MUST rewrite, so the committed report
    # cannot keep a stale dirty:false that fools the matrix.
    ws = _git_fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-dev-primary.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws.parent)}
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "dev-primary"], env=collector_env(env), timeout=60, check=True)
    assert "dirty: false" in out.read_text()
    (ws.joinpath(*MEASURED_PATH)).write_text("workstations: {}\n# now dirty\n")
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "dev-primary"], env=collector_env(env), timeout=60, check=True)
    assert "dirty: true" in out.read_text()          # transition was hashed → rewrite happened


def test_collect_dirty_no_self_trigger(tmp_path):
    # A3: the collector's OWN output (.claude/state/equality-*.yaml) must not make dirty true.
    # dirty is captured pre-write AND .claude/state is outside the measured allowlist.
    ws = _git_fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-dev-primary.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws.parent)}
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "dev-primary"], env=collector_env(env), timeout=60, check=True)
    assert "dirty: false" in out.read_text()         # writing its own report didn't self-dirty


def test_collect_origin_ref_age_in_worktree(tmp_path):
    # Worktree-safety (#2851): refs/remotes/origin/main + FETCH_HEAD live in --git-common-dir,
    # NOT the per-worktree --git-dir. The collector must resolve the common dir, else every
    # worktree-based collection fail-closes to origin_ref_age_h=unknown → false STALE-CHECKOUT.
    main_ws = _git_fixture(tmp_path)
    wt = tmp_path / "wt"
    _git(main_ws, "worktree", "add", "-q", "--detach", str(wt))   # full checkout (committed .claude tree)
    p = _stdout_prov(wt)
    assert isinstance(p["origin_ref_age_h"], (int, float)) and not isinstance(p["origin_ref_age_h"], bool), p
    assert 0 <= p["origin_ref_age_h"] <= 12
    assert p["behind_main"] == 0          # worktree HEAD == origin/main → current, not unknown


def test_winabs_guard_classifies_windows_drive_paths():
    # #2816 W4 worktree-freshness fix (Windows): a linked-worktree --git-common-dir on Windows is
    # an absolute drive-letter path (C:/repo/.git or C:\repo\.git) that does NOT start with "/", so
    # the bare "!= /*" guard alone would treat it as RELATIVE and corrupt it (WS/C:/repo/.git) ->
    # FETCH_HEAD unfound -> origin_ref_age_h "unknown" -> matrix false-STALEs every worktree run on
    # Windows. The Linux-only test_collect_origin_ref_age_in_worktree above cannot reproduce this
    # (Linux common-dirs are relative or "/"-absolute). Bind this test to the REAL winabs pattern
    # extracted from the script (not a copy) so weakening the guard fails CI.
    src = (SCRIPT.parent / "lib/collect-provenance.sh").read_text()
    m = re.search(r"winabs='([^']*)'", src)
    assert m, "winabs guard missing from collect-equality.sh (#2816 W4 worktree-freshness fix)"
    winabs = m.group(1)

    def classify(gd: str) -> str:
        prog = (f"winabs={shlex.quote(winabs)}\n"
                'if [[ -n "$1" && "$1" != /* && ! "$1" =~ $winabs ]]; then echo relative; '
                'else echo absolute; fi')
        return subprocess.run(["bash", "-c", prog, "_", gd],
                              capture_output=True, text=True, timeout=30, check=False).stdout.strip()

    # Windows linked-worktree common-dir (forward AND back slash) must classify ABSOLUTE -> no join
    assert classify("C:/workspace-hub/.git") == "absolute"
    assert classify(r"C:\workspace-hub\.git") == "absolute"
    # POSIX absolute stays absolute; genuine relative paths still join to WS
    assert classify("/srv/repo/.git") == "absolute"
    assert classify(".git") == "relative"
    assert classify("worktrees/x/.git") == "relative"


def test_collect_origin_ref_age_refreshed_not_frozen(tmp_path):
    # origin_ref_age_h is HASHED (A1: only checkout_sha is excluded from the canonical payload),
    # so a stale freshness value can never be frozen into the committed report and fool the
    # matrix. Tamper the committed age to a huge stale value; the next run MUST rewrite it back.
    ws = _git_fixture(tmp_path)
    out = ws / ".claude" / "state" / "equality-dev-primary.yaml"
    env = {"WORKSPACE_HUB": str(ws), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(ws.parent)}
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "dev-primary"], env=collector_env(env), timeout=60, check=True)
    assert re.search(r"origin_ref_age_h: \d", out.read_text())          # live numeric value
    out.write_text(re.sub(r"origin_ref_age_h: .*", "origin_ref_age_h: 999", out.read_text()))
    subprocess.run(["bash", _bash_path(SCRIPT), "--machine", "dev-primary"], env=collector_env(env), timeout=60, check=True)
    assert "origin_ref_age_h: 999" not in out.read_text()               # refreshed, not frozen




def test_fixture_ignores_inherited_repository_bindings(tmp_path, monkeypatch):
    """A child fixture shall preserve the caller's tracked files and Git metadata."""
    caller = _git_fixture(tmp_path / "caller")
    sentinel = caller.joinpath(*MEASURED_PATH)
    metadata = caller / ".git"
    before = (sentinel.read_bytes(), (metadata / "HEAD").read_bytes(),
              (metadata / "index").read_bytes())
    monkeypatch.setenv("GIT_DIR", str(metadata))
    monkeypatch.setenv("GIT_WORK_TREE", str(caller))
    monkeypatch.setenv("GIT_COMMON_DIR", str(metadata))
    child = _git_fixture(tmp_path / "child with spaces")
    assert _stdout_prov(child)["dirty"] is False
    child.joinpath(*MEASURED_PATH).write_text("workstations: {}\n# changed\n")
    assert _stdout_prov(child)["dirty"] is True
    assert before == (sentinel.read_bytes(), (metadata / "HEAD").read_bytes(),
                      (metadata / "index").read_bytes())


def test_fixture_ignores_user_line_ending_configuration(tmp_path):
    """Independent Git example: clean index -> false, changed tracked bytes -> true."""
    (tmp_path / ".gitconfig").write_text("[core]\n\tautocrlf = true\n")
    workspace = _git_fixture(tmp_path)
    assert _stdout_prov(workspace)["dirty"] is False
    workspace.joinpath(*MEASURED_PATH).write_text("workstations: {}\n# changed\n")
    assert _stdout_prov(workspace)["dirty"] is True
