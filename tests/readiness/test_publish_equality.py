"""TDD tests for publish-equality.sh — the sparse-worktree equality publisher.

Contract: equality artifacts ALWAYS reach origin/main so the matrix compares every
machine equally — independent of the interactive checkout's state (dirty, diverged,
mid-rebase). Only evidence strictly NEWER than origin's copy is published (a machine
with a stale view can never clobber a peer's fresher state), staged paths are
allowlist-guarded, and the temp worktree is always cleaned up.
"""

from __future__ import annotations

import os
import shutil
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


def _shell_path(path: Path | str) -> str:
    if shutil.which("cygpath"):
        return subprocess.check_output(
            ["cygpath", "-u", str(path)], text=True,
        ).strip()
    return str(path)


def _publisher_env(tmp_path: Path, **updates: str) -> dict[str, str]:
    publisher_tmp = tmp_path / "publisher-tmp"
    publisher_tmp.mkdir(exist_ok=True)
    return {
        **GIT_ENV,
        "TMPDIR": _shell_path(publisher_tmp),
        **updates,
    }


def _assert_no_publisher_residue(tmp_path: Path, *clones: Path) -> None:
    assert not list((tmp_path / "publisher-tmp").glob("publish-equality-wt.*"))
    for clone in clones:
        assert not list((clone / ".git").rglob("*.lock"))
        assert _git("worktree", "list", "--porcelain", cwd=clone).count("worktree ") == 1


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


def _run(
    clone: Path,
    *args: str,
    expect_rc: int = 0,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    res = subprocess.run(["bash", str(SCRIPT), "--repo", str(clone), *args],
                         env=env or GIT_ENV, capture_output=True, text=True, timeout=120)
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


def test_publishes_when_flock_is_unavailable(tmp_path):
    assert "flock" not in SCRIPT.read_text()
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-02T12:00:00"))
    bindir = tmp_path / "bin"
    bindir.mkdir()
    poison = bindir / "flock"
    poison.write_text("#!/usr/bin/env bash\nexit 88\n")
    poison.chmod(0o755)
    env = _publisher_env(
        tmp_path, PATH=f"{_shell_path(bindir)}:{GIT_ENV['PATH']}",
    )
    _run(clone, env=env)
    assert "2026-07-02T12:00:00" in _origin_file(
        origin, ".claude/state/equality-dev-primary.yaml")
    _assert_no_publisher_residue(tmp_path, clone)


@pytest.mark.parametrize(
    "args",
    [
        ("--max-attempts", "0"),
        ("--max-attempts", "nope"),
        ("--retry-delay-seconds", "-1"),
        ("--retry-delay-seconds", "nope"),
        ("--max-attempts",),
        ("--unknown-option",),
    ],
)
def test_invalid_retry_configuration_fails_before_git_mutation(tmp_path, args):
    origin, clone = _fixture(tmp_path)
    before = _git("rev-parse", "main", cwd=origin).strip()
    _run(clone, *args, expect_rc=2)
    assert _git("rev-parse", "main", cwd=origin).strip() == before


def test_same_checkout_concurrent_publishers_converge(tmp_path):
    origin, clone = _fixture(tmp_path)
    stamp = "2026-07-02T12:00:00"
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", stamp))
    cmd = [
        "bash", str(SCRIPT), "--repo", str(clone),
        "--max-attempts", "5", "--retry-delay-seconds", "0",
    ]
    env = _publisher_env(tmp_path)
    procs = [
        subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
        for _ in range(2)
    ]
    results = [p.communicate(timeout=120) + (p.returncode,) for p in procs]
    assert all(rc == 0 for _out, _err, rc in results), results
    assert any("no commit needed" in out for out, _err, _rc in results), results
    assert stamp in _origin_file(origin, ".claude/state/equality-dev-primary.yaml")
    _assert_no_publisher_residue(tmp_path, clone)


def test_concurrent_publishers_converge(tmp_path):
    origin, first = _fixture(tmp_path)
    seed = tmp_path / "seed"
    builder = seed / "scripts" / "readiness" / "build-equality-matrix.py"
    builder.write_text(
        "from pathlib import Path\n"
        "root = Path(__file__).resolve().parents[2]\n"
        "names = sorted(p.name for p in (root / '.claude/state').glob('equality-*.yaml'))\n"
        "(root / 'docs/reports/machine-equality-matrix.html').write_text('\\n'.join(names))\n"
    )
    _git("add", str(builder.relative_to(seed)), cwd=seed)
    _git("commit", "-m", "add race builder", cwd=seed)
    _git("push", "origin", "main", cwd=seed)
    second = tmp_path / "clone-second"
    _git("clone", str(origin), str(second), cwd=tmp_path)
    (first / ".claude" / "state" / "equality-first.yaml").write_text(
        _yaml("first", "2026-07-02T12:00:00"))
    (second / ".claude" / "state" / "equality-second.yaml").write_text(
        _yaml("second", "2026-07-02T12:00:01"))

    markers = [tmp_path / "push-first", tmp_path / "push-second"]
    bash_markers = [_shell_path(path) for path in markers]
    for clone, own, peer in zip(
        (first, second), bash_markers, reversed(bash_markers), strict=True,
    ):
        hook = clone / ".git" / "hooks" / "pre-push"
        hook.write_text(
            "#!/usr/bin/env bash\n"
            f"touch {own!r}\n"
            f"for _ in $(seq 1 1000); do [[ -f {peer!r} ]] && exit 0; sleep 0.02; done\n"
            "exit 97\n"
        )
        hook.chmod(0o755)

    commands = [
        ["bash", str(SCRIPT), "--repo", str(clone),
         "--rebuild", "--max-attempts", "5", "--retry-delay-seconds", "0"]
        for clone in (first, second)
    ]
    env = _publisher_env(tmp_path)
    procs = [
        subprocess.Popen(command, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
        for command in commands
    ]
    results = [proc.communicate(timeout=120) + (proc.returncode,) for proc in procs]
    assert all(rc == 0 for _out, _err, rc in results), results
    assert any("attempt 1 failed" in out for out, _err, _rc in results), results
    assert "2026-07-02T12:00:00" in _origin_file(
        origin, ".claude/state/equality-first.yaml")
    assert "2026-07-02T12:00:01" in _origin_file(
        origin, ".claude/state/equality-second.yaml")
    matrix = _origin_file(origin, "docs/reports/machine-equality-matrix.html")
    assert "equality-first.yaml" in matrix
    assert "equality-second.yaml" in matrix
    _assert_no_publisher_residue(tmp_path, first, second)


def test_retry_exhaustion_fails_loud(tmp_path):
    _origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-02T12:00:00"))
    bindir = tmp_path / "bin"
    bindir.mkdir()
    real_git = _shell_path(shutil.which("git") or "git")
    git_stub = bindir / "git"
    git_stub.write_text(
        "#!/usr/bin/env bash\n"
        "for arg in \"$@\"; do [[ \"$arg\" == push ]] && exit 1; done\n"
        f"exec {real_git!r} \"$@\"\n"
    )
    git_stub.chmod(0o755)
    notify_log = tmp_path / "notify.log"
    notify = clone / "scripts" / "notify.sh"
    notify.write_text("#!/usr/bin/env bash\nprintf '%s\\n' \"$*\" >> \"$NOTIFY_LOG\"\n")
    notify.chmod(0o755)
    env = _publisher_env(
        tmp_path,
        PATH=f"{_shell_path(bindir)}:{GIT_ENV['PATH']}",
        NOTIFY_LOG=_shell_path(notify_log),
    )
    res = _run(
        clone, "--max-attempts", "2", "--retry-delay-seconds", "0",
        expect_rc=1, env=env,
    )
    assert "could not publish" in res.stderr
    assert "done (" not in res.stdout
    assert "equality-publish fail" in notify_log.read_text()
    _assert_no_publisher_residue(tmp_path, clone)


def test_cleanup_failure_is_not_reported_as_success(tmp_path):
    _origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-02T12:00:00"))
    bindir = tmp_path / "bin"
    bindir.mkdir()
    real_git = _shell_path(shutil.which("git") or "git")
    git_stub = bindir / "git"
    git_stub.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$*\" == *\"worktree remove\"* ]]; then exit 23; fi\n"
        f"exec {real_git!r} \"$@\"\n"
    )
    git_stub.chmod(0o755)
    env = _publisher_env(
        tmp_path, PATH=f"{_shell_path(bindir)}:{GIT_ENV['PATH']}",
    )
    res = _run(clone, expect_rc=1, env=env)
    assert "cleanup" in res.stderr
    assert "done (" not in res.stdout


def test_transient_worktree_add_failure_retries_from_clean_state(tmp_path):
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-02T12:00:00"))
    bindir = tmp_path / "bin"
    bindir.mkdir()
    marker = _shell_path(tmp_path / "add-failed-once")
    real_git = _shell_path(shutil.which("git") or "git")
    git_stub = bindir / "git"
    git_stub.write_text(
        "#!/usr/bin/env bash\n"
        f"if [[ \"$*\" == *\"worktree add\"* && ! -f {marker!r} ]]; then "
        f"touch {marker!r}; exit 31; fi\n"
        f"exec {real_git!r} \"$@\"\n"
    )
    git_stub.chmod(0o755)
    env = _publisher_env(
        tmp_path, PATH=f"{_shell_path(bindir)}:{GIT_ENV['PATH']}",
    )
    _run(
        clone, "--max-attempts", "3", "--retry-delay-seconds", "0", env=env,
    )
    assert "2026-07-02T12:00:00" in _origin_file(
        origin, ".claude/state/equality-dev-primary.yaml")
    _assert_no_publisher_residue(tmp_path, clone)


def test_transient_rmdir_failure_retries_from_clean_state(tmp_path):
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        _yaml("dev-primary", "2026-07-02T12:00:00"))
    bindir = tmp_path / "bin"
    bindir.mkdir()
    marker = _shell_path(tmp_path / "rmdir-failed-once")
    rmdir_stub = bindir / "rmdir"
    rmdir_stub.write_text(
        "#!/usr/bin/env bash\n"
        f"if [[ ! -f {marker!r} ]]; then touch {marker!r}; exit 32; fi\n"
        "exec /usr/bin/rmdir \"$@\"\n"
    )
    rmdir_stub.chmod(0o755)
    env = _publisher_env(
        tmp_path, PATH=f"{_shell_path(bindir)}:{GIT_ENV['PATH']}",
    )
    _run(
        clone, "--max-attempts", "3", "--retry-delay-seconds", "0", env=env,
    )
    assert "2026-07-02T12:00:00" in _origin_file(
        origin, ".claude/state/equality-dev-primary.yaml")
    _assert_no_publisher_residue(tmp_path, clone)


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


def test_unstamped_local_evidence_is_not_published(tmp_path):
    origin, clone = _fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        "machine: dev-primary\n")             # no generated_at ⇒ not publishable
    res = _run(clone)
    assert "no commit needed" in res.stdout
    assert "2026-06-01T00:00:00" in _origin_file(
        origin, ".claude/state/equality-dev-primary.yaml")
