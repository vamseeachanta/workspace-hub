"""TDD tests for publish-equality.sh — the sparse-worktree equality publisher.

Contract: equality artifacts ALWAYS reach origin/main so the matrix compares every
machine equally — independent of the interactive checkout's state (dirty, diverged,
mid-rebase). Only evidence strictly NEWER than origin's copy is published (a machine
with a stale view can never clobber a peer's fresher state), staged paths are
allowlist-guarded, and the temp worktree is always cleaned up.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "readiness" / "publish-equality.sh"

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@example.com",
}


def _git(*args: str, cwd: Path) -> str:
    res = subprocess.run(["git", *args], cwd=cwd, env=GIT_ENV,
                         capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, f"git {' '.join(args)}: {res.stderr}"
    return res.stdout


def _yaml(machine: str, stamp: str) -> str:
    return f'generated_at: "{stamp}"\nmachine: "{machine}"\n'


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    """Bare origin + working clone. Origin main seeds: self evidence (old stamp),
    peer evidence (fresh stamp), empty docs/reports, empty scripts/readiness."""
    origin = tmp_path / "origin.git"
    _git("init", "--bare", "-b", "main", str(origin), cwd=tmp_path)
    seed = tmp_path / "seed"
    _git("clone", str(origin), str(seed), cwd=tmp_path)
    (seed / ".claude" / "state").mkdir(parents=True)
    (seed / "docs" / "reports").mkdir(parents=True)
    (seed / "scripts" / "readiness").mkdir(parents=True)
    (seed / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-06-01T00:00:00"))
    (seed / ".claude" / "state" / "equality-peer.yaml").write_text(
        _yaml("peer", "2026-06-20T00:00:00"))
    (seed / "docs" / "reports" / ".gitkeep").write_text("")
    (seed / "scripts" / "readiness" / ".gitkeep").write_text("")
    _git("add", "-A", cwd=seed)
    _git("commit", "-m", "seed", cwd=seed)
    _git("push", "origin", "main", cwd=seed)

    clone = tmp_path / "clone"
    _git("clone", str(origin), str(clone), cwd=tmp_path)
    return origin, clone


def _run(clone: Path, *args: str, expect_rc: int = 0) -> subprocess.CompletedProcess:
    res = subprocess.run(["bash", str(SCRIPT), "--repo", str(clone), *args],
                         env=GIT_ENV, capture_output=True, text=True, timeout=120)
    assert res.returncode == expect_rc, f"rc={res.returncode}\n{res.stdout}\n{res.stderr}"
    return res


def _origin_file(origin: Path, path: str) -> str:
    res = subprocess.run(["git", "show", f"main:{path}"], cwd=origin, env=GIT_ENV,
                         capture_output=True, text=True, timeout=60)
    return res.stdout if res.returncode == 0 else ""


def test_publishes_newer_local_evidence(tmp_path):
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    _run(clone)
    assert "2026-07-01T12:00:00" in _origin_file(
        origin, ".claude/state/equality-dev-primary.yaml")


def test_does_not_clobber_fresher_origin_evidence(tmp_path):
    # Local copy of the PEER's evidence is older than origin's — must never regress it.
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-peer.yaml").write_text(
        _yaml("peer", "2026-06-10T00:00:00"))
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))       # something newer, so a commit happens
    _run(clone)
    assert "2026-06-20T00:00:00" in _origin_file(origin, ".claude/state/equality-peer.yaml")


def test_noop_when_nothing_newer(tmp_path):
    origin, clone = _fixture(tmp_path)
    before = _git("rev-parse", "main", cwd=origin).strip()
    res = _run(clone)
    assert "no commit needed" in res.stdout
    assert _git("rev-parse", "main", cwd=origin).strip() == before


def test_publishes_even_when_local_checkout_diverged_and_dirty(tmp_path):
    # The core value: a diverged + dirty interactive checkout must not block publishing.
    origin, clone = _fixture(tmp_path)
    seed = tmp_path / "seed"
    (seed / "docs" / "reports" / "advance.txt").write_text("x")
    _git("add", "-A", cwd=seed); _git("commit", "-m", "advance", cwd=seed)
    _git("push", "origin", "main", cwd=seed)               # origin moves ahead of clone
    (clone / "local.txt").write_text("local")
    _git("add", "local.txt", cwd=clone)
    _git("commit", "-m", "local-divergence", cwd=clone)    # clone moves ahead of origin
    (clone / "dirty.txt").write_text("dirty")              # …and is dirty on top
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    _run(clone)
    assert "2026-07-01T12:00:00" in _origin_file(
        origin, ".claude/state/equality-dev-primary.yaml")
    # the clone's own divergence/dirt is untouched
    assert (clone / "dirty.txt").exists()
    assert "local-divergence" in _git("log", "-1", "--format=%s", cwd=clone)


STUB_BUILDER = """\
from pathlib import Path
root = Path(__file__).resolve().parents[2]
(root / "docs" / "reports" / "machine-equality-matrix.html").write_text("<html>stub</html>")
"""


def test_rebuild_renders_matrix_inside_worktree(tmp_path):
    origin, clone = _fixture(tmp_path)
    seed = tmp_path / "seed"
    _git("pull", "origin", "main", cwd=seed)
    (seed / "scripts" / "readiness" / "build-equality-matrix.py").write_text(STUB_BUILDER)
    _git("add", "-A", cwd=seed); _git("commit", "-m", "stub builder", cwd=seed)
    _git("push", "origin", "main", cwd=seed)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    _run(clone, "--rebuild")
    assert "stub" in _origin_file(origin, "docs/reports/machine-equality-matrix.html")


def test_refuses_unexpected_staged_paths(tmp_path):
    # A builder that writes outside the artifact allowlist must abort the publish.
    origin, clone = _fixture(tmp_path)
    seed = tmp_path / "seed"
    _git("pull", "origin", "main", cwd=seed)
    (seed / "scripts" / "readiness" / "build-equality-matrix.py").write_text(
        STUB_BUILDER.replace("machine-equality-matrix.html", "evil.txt"))
    _git("add", "-A", cwd=seed); _git("commit", "-m", "evil builder", cwd=seed)
    _git("push", "origin", "main", cwd=seed)
    before = _git("rev-parse", "main", cwd=origin).strip()
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    _run(clone, "--rebuild", expect_rc=1)
    assert _git("rev-parse", "main", cwd=origin).strip() == before


def test_dry_run_pushes_nothing(tmp_path):
    origin, clone = _fixture(tmp_path)
    before = _git("rev-parse", "main", cwd=origin).strip()
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    res = _run(clone, "--dry-run")
    assert "would push" in res.stdout
    assert _git("rev-parse", "main", cwd=origin).strip() == before


def test_worktree_always_cleaned_up(tmp_path):
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    _run(clone)
    wts = _git("worktree", "list", "--porcelain", cwd=clone)
    assert wts.count("worktree ") == 1        # only the main checkout remains


# ── #3571: mkdir-lock fallback (flock is absent on Git for Windows bash) ──────
# Behavioral cases force the fallback via PUBLISH_EQUALITY_LOCK=mkdir (also the
# operator escape hatch — a mkdir lock is a real lock on any host). Auto-detect
# is asserted statically: command-not-found must never collapse into the
# lock-held skip path again.


def _host_lock_dir(tmp_path: Path) -> Path:
    host = subprocess.run(["hostname"], capture_output=True, text=True,
                          timeout=30).stdout.strip().lower()
    return tmp_path / f"publish-equality-{host}.lock.d"


def _run_mkdir_lock(clone: Path, tmp_path: Path, *args: str,
                    expect_rc: int = 0) -> subprocess.CompletedProcess:
    env = {**GIT_ENV, "PUBLISH_EQUALITY_LOCK": "mkdir", "TMPDIR": str(tmp_path)}
    res = subprocess.run(["bash", str(SCRIPT), "--repo", str(clone), *args],
                         env=env, capture_output=True, text=True, timeout=120)
    assert res.returncode == expect_rc, f"rc={res.returncode}\n{res.stdout}\n{res.stderr}"
    return res


def test_mkdir_lock_publishes(tmp_path):
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    _run_mkdir_lock(clone, tmp_path)
    assert "2026-07-01T12:00:00" in _origin_file(
        origin, ".claude/state/equality-dev-primary.yaml")
    assert not _host_lock_dir(tmp_path).exists()      # lock released on exit


def test_mkdir_lock_held_skips_exit_zero(tmp_path):
    origin, clone = _fixture(tmp_path)
    before = _git("rev-parse", "main", cwd=origin).strip()
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    _host_lock_dir(tmp_path).mkdir(parents=True)      # a live holder
    res = _run_mkdir_lock(clone, tmp_path)            # exit 0, like flock -n
    assert "another publish in flight" in res.stdout
    assert _git("rev-parse", "main", cwd=origin).strip() == before
    assert _host_lock_dir(tmp_path).exists()          # holder's lock untouched


def test_mkdir_lock_stale_is_stolen_and_publish_proceeds(tmp_path):
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    lock = _host_lock_dir(tmp_path)
    lock.mkdir(parents=True)
    two_hours_ago = 7200
    import time
    os.utime(lock, (time.time() - two_hours_ago, time.time() - two_hours_ago))
    res = _run_mkdir_lock(clone, tmp_path)
    assert "stale" in res.stdout                      # loud steal
    assert "2026-07-01T12:00:00" in _origin_file(
        origin, ".claude/state/equality-dev-primary.yaml")
    assert not lock.exists()
    assert not list(tmp_path.glob("publish-equality-*.lock.d.stale.*"))


def test_mkdir_lock_released_with_worktree_on_failure(tmp_path):
    # Reuse the evil-builder failure: rc=1 must still clean BOTH worktree and lock.
    origin, clone = _fixture(tmp_path)
    seed = tmp_path / "seed"
    _git("pull", "origin", "main", cwd=seed)
    (seed / "scripts" / "readiness" / "build-equality-matrix.py").write_text(
        STUB_BUILDER.replace("machine-equality-matrix.html", "evil.txt"))
    _git("add", "-A", cwd=seed); _git("commit", "-m", "evil builder", cwd=seed)
    _git("push", "origin", "main", cwd=seed)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    _run_mkdir_lock(clone, tmp_path, "--rebuild", expect_rc=1)
    assert not _host_lock_dir(tmp_path).exists()
    wts = _git("worktree", "list", "--porcelain", cwd=clone)
    assert wts.count("worktree ") == 1


LOCK_PROBE_BUILDER = """\
import glob, os
from pathlib import Path
root = Path(__file__).resolve().parents[2]
held = bool(glob.glob(os.path.join(os.environ.get("TMPDIR", "/tmp"),
                                   "publish-equality-*.lock.d")))
(root / "docs" / "reports" / "machine-equality-matrix.html").write_text(
    "lock-held" if held else "lock-missing")
"""


def test_mkdir_lock_stays_held_throughout_publish(tmp_path):
    # Codex r2-code MAJOR: attempt() used to start by releasing the lock, so the
    # entire fetch/copy/commit/push ran unlocked. A builder stub that runs INSIDE
    # the publish observes whether the lock dir still exists at that point.
    origin, clone = _fixture(tmp_path)
    seed = tmp_path / "seed"
    _git("pull", "origin", "main", cwd=seed)
    (seed / "scripts" / "readiness" / "build-equality-matrix.py").write_text(
        LOCK_PROBE_BUILDER)
    _git("add", "-A", cwd=seed); _git("commit", "-m", "probe builder", cwd=seed)
    _git("push", "origin", "main", cwd=seed)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    _run_mkdir_lock(clone, tmp_path, "--rebuild")
    assert _origin_file(origin, "docs/reports/machine-equality-matrix.html") == "lock-held"
    assert not _host_lock_dir(tmp_path).exists()      # …and released at exit


def test_commit_subject_uses_public_label_not_hostname(tmp_path):
    # 2026-07-18 leak (#3571): the publish commit subject serialized the raw OS
    # hostname onto public main. With an identity file (or EQ_MACHINE), the
    # subject must carry the fleet label; the hostname must appear nowhere.
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    idf = tmp_path / "machine-identity.yaml"
    idf.write_text('machine: "ace-win-1"\npublic_host: "ace-win-1"\n')
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    hostname = fake_bin / "hostname"
    hostname.write_text("#!/usr/bin/env bash\nprintf '%s\\n' private-ci-host\n")
    hostname.chmod(0o755)
    env = {
        **GIT_ENV,
        "WORKSPACE_HUB_MACHINE_IDENTITY": str(idf),
        "PATH": f"{fake_bin.as_posix()}:{GIT_ENV.get('PATH', '')}",
    }
    res = subprocess.run(["bash", str(SCRIPT), "--repo", str(clone)],
                         env=env, capture_output=True, text=True, timeout=120)
    assert res.returncode == 0, f"{res.stdout}\n{res.stderr}"
    subject = _git("log", "-1", "--format=%s", cwd=origin)
    assert "from ace-win-1" in subject
    assert "private-ci-host" not in subject.lower()


def test_commit_subject_honors_eq_machine_env(tmp_path):
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-01T12:00:00"))
    env = {**GIT_ENV, "EQ_MACHINE": "ace-win-2"}
    res = subprocess.run(["bash", str(SCRIPT), "--repo", str(clone)],
                         env=env, capture_output=True, text=True, timeout=120)
    assert res.returncode == 0, f"{res.stdout}\n{res.stderr}"
    assert "from ace-win-2" in _git("log", "-1", "--format=%s", cwd=origin)


def test_lock_autodetect_gates_on_command_v_not_exit_code():
    # Static contract: detection must be `command -v flock`; a bare `flock -n || skip`
    # conflates command-not-found with lock-held (the #3571 silent no-op).
    text = SCRIPT.read_text(encoding="utf-8")
    assert "command -v flock" in text
    assert "PUBLISH_EQUALITY_LOCK" in text


def test_unstamped_local_evidence_is_not_published(tmp_path):
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        "machine: dev-primary\n")             # no generated_at ⇒ not publishable
    res = _run(clone)
    assert "no commit needed" in res.stdout
    assert "2026-06-01T00:00:00" in _origin_file(
        origin, ".claude/state/equality-dev-primary.yaml")
