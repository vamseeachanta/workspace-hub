"""TDD tests for scripts/memory/resolve-auto-memory.sh :: resolve_claude_memory_dir().

WHY THIS EXISTS. bridge-hermes-claude.sh derived Claude's auto-memory directory by
slugifying the CURRENT repo root:

    _project_slug="$(cd "${REPO_ROOT}" && pwd | tr '/' '-')"
    CLAUDE_MEM_DIR="${HOME}/.claude/projects/${_project_slug}/memory"

When the ecosystem moved from /mnt/local-analysis/workspace-hub to
/mnt/ace/ws/workspace-hub, that started resolving to a directory that does not
exist -- Claude Code keeps writing to the ORIGINAL slug, because the harness
pins the project path at session start. The snapshot block is guarded by a bare
`if [[ -f "${CLAUDE_AUTO}" ]]` with no else, so the bridge silently mirrored
nothing while still printing a tick for the stale file it left in place.

Two failures, and the second is the worse one:
  1. the path no longer resolves after a workspace move;
  2. an unresolvable path is INDISTINGUISHABLE FROM SUCCESS.

The helper takes repo root and home as PARAMETERS rather than reading script
globals, matching the precedent set for bridge_commit_and_push (r1/r2 finding on
#3384), so it is drivable from a temp fixture.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
LIB = REPO_ROOT / "scripts" / "memory" / "resolve-auto-memory.sh"
BRIDGE = REPO_ROOT / "scripts" / "memory" / "bridge-hermes-claude.sh"


def _resolve(repo_root: Path, home: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "-c",
         f'source "{LIB}"; resolve_claude_memory_dir "{repo_root}" "{home}"'],
        capture_output=True, text=True,
    )


def _seed(home: Path, slug: str, *, with_index: bool = True) -> Path:
    d = home / ".claude" / "projects" / slug / "memory"
    d.mkdir(parents=True)
    if with_index:
        (d / "MEMORY.md").write_text("# index\n", encoding="utf-8")
    return d


def test_resolves_the_exact_slug_when_it_exists(tmp_path: Path) -> None:
    home = tmp_path / "home"
    repo = tmp_path / "mnt" / "ace" / "ws" / "workspace-hub"
    repo.mkdir(parents=True)
    want = _seed(home, str(repo).replace("/", "-"))

    r = _resolve(repo, home)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == str(want)


def test_falls_back_to_the_pre_migration_slug(tmp_path: Path) -> None:
    """The live defect: repo moved, Claude Code still writes to the old slug."""
    home = tmp_path / "home"
    repo = tmp_path / "mnt" / "ace" / "ws" / "workspace-hub"
    repo.mkdir(parents=True)
    legacy = _seed(home, str(tmp_path / "mnt" / "local-analysis" / "workspace-hub").replace("/", "-"))

    r = _resolve(repo, home)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == str(legacy), "must fall back to the legacy slug"


def test_prefers_the_exact_slug_over_a_legacy_one(tmp_path: Path) -> None:
    """After a real migration completes, the current path must win."""
    home = tmp_path / "home"
    repo = tmp_path / "mnt" / "ace" / "ws" / "workspace-hub"
    repo.mkdir(parents=True)
    _seed(home, str(tmp_path / "mnt" / "local-analysis" / "workspace-hub").replace("/", "-"))
    exact = _seed(home, str(repo).replace("/", "-"))

    r = _resolve(repo, home)
    assert r.stdout.strip() == str(exact)


def test_ignores_a_candidate_with_no_memory_index(tmp_path: Path) -> None:
    """An empty directory is not a memory store; falling into it would mirror nothing."""
    home = tmp_path / "home"
    repo = tmp_path / "mnt" / "ace" / "ws" / "workspace-hub"
    repo.mkdir(parents=True)
    _seed(home, str(repo).replace("/", "-"), with_index=False)
    legacy = _seed(home, str(tmp_path / "mnt" / "local-analysis" / "workspace-hub").replace("/", "-"))

    r = _resolve(repo, home)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == str(legacy)


def test_fails_loudly_when_nothing_resolves(tmp_path: Path) -> None:
    """The core fix: unresolvable must NOT look like success.

    The old code's bare `if [[ -f ... ]]` with no else made a missing source
    indistinguishable from a completed mirror.
    """
    home = tmp_path / "home"
    (home / ".claude" / "projects").mkdir(parents=True)
    repo = tmp_path / "nowhere"
    repo.mkdir()

    r = _resolve(repo, home)
    assert r.returncode != 0, "must exit non-zero when no memory dir resolves"
    assert not r.stdout.strip(), "must not emit a path it could not verify"
    assert "auto-memory" in r.stderr.lower() or "memory" in r.stderr.lower(), r.stderr


def test_bridge_uses_the_resolver_and_warns_instead_of_skipping_silently() -> None:
    """Wiring guard: the bridge must consume the helper and not re-derive the slug inline."""
    text = BRIDGE.read_text(encoding="utf-8")

    assert "resolve-auto-memory.sh" in text, "bridge must source the resolver"
    assert "resolve_claude_memory_dir" in text, "bridge must call the resolver"
    assert 'pwd | tr \'/\' \'-\'' not in text, (
        "bridge must not still derive the slug inline -- that is the defect"
    )
    # The silent-skip shape: a bare existence test on the snapshot source with no warning.
    assert "WARN" in text or "warning" in text.lower(), (
        "bridge must warn when auto-memory cannot be resolved, not skip silently"
    )


def test_ambiguous_basename_collision_is_fatal(tmp_path: Path) -> None:
    """Codex r1 MAJOR: '-workspace-hub' also suffix-matches '-my-workspace-hub'.

    Slugification maps '/' and '-' to the same character, so the two are
    genuinely indistinguishable by shape. Picking the newest MEMORY.md -- the
    original tiebreak -- let an unrelated repo's store win. Ambiguity must be
    fatal, not resolved by a guess.
    """
    home = tmp_path / "home"
    repo = tmp_path / "mnt" / "ace" / "ws" / "workspace-hub"
    repo.mkdir(parents=True)
    _seed(home, str(tmp_path / "elsewhere" / "my-workspace-hub").replace("/", "-"))
    _seed(home, str(tmp_path / "other" / "workspace-hub").replace("/", "-"))

    r = _resolve(repo, home)
    assert r.returncode != 0, "two suffix candidates must be fatal, not a guess"
    assert not r.stdout.strip()
    assert "candidate" in r.stderr.lower()


def test_a_colliding_repo_does_not_win_on_mtime(tmp_path: Path) -> None:
    """The specific wrong-store selection Codex demonstrated."""
    home = tmp_path / "home"
    repo = tmp_path / "mnt" / "ace" / "ws" / "workspace-hub"
    repo.mkdir(parents=True)
    intruder = _seed(home, str(tmp_path / "x" / "my-workspace-hub").replace("/", "-"))

    r = _resolve(repo, home)
    # Sole candidate, so it resolves -- but it must announce the guess on stderr
    # so a wrong pick is visible rather than silent.
    if r.returncode == 0:
        assert r.stdout.strip() == str(intruder)
        assert "verify" in r.stderr.lower(), "a fallback guess must be announced"


def test_alias_rewrite_is_anchored_to_a_leading_prefix(tmp_path: Path) -> None:
    """Codex r1 MINOR: substring replacement rewrote paths that merely CONTAIN the prefix."""
    home = tmp_path / "home"
    (home / ".claude" / "projects").mkdir(parents=True)
    # A path containing '/mnt/ace/ws/' in the middle, not at the root.
    repo = tmp_path / "srv" / "mnt" / "ace" / "ws" / "thing"
    repo.mkdir(parents=True)
    # Seed the store that a naive substring rewrite would wrongly reach for.
    _seed(home, str(tmp_path / "srv" / "mnt" / "local-analysis" / "thing").replace("/", "-"))

    r = _resolve(repo, home)
    # The alias must not fire. It shares a basename with the repo, so the
    # last-resort search can still reach it -- the discriminator is HOW: an
    # alias hit returns silently, a fallback hit must announce itself.
    if r.returncode == 0:
        assert "falling back" in r.stderr.lower(), (
            "resolved silently, so the mid-path prefix wrongly triggered the alias rewrite"
        )


def test_repo_outside_any_known_prefix_fails_cleanly(tmp_path: Path) -> None:
    home = tmp_path / "home"
    (home / ".claude" / "projects").mkdir(parents=True)
    repo = tmp_path / "opt" / "somewhere" / "proj"
    repo.mkdir(parents=True)

    r = _resolve(repo, home)
    assert r.returncode != 0
    assert not r.stdout.strip()


def test_helper_name_is_namespaced(tmp_path: Path) -> None:
    """Codex r1 MINOR: a generic `_has_memory` defined in-function leaks globally."""
    text = LIB.read_text(encoding="utf-8")
    assert "_auto_memory_has_index" in text
    assert "_has_memory()" not in text, "generic helper name would leak into the caller's shell"
