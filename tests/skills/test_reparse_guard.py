"""TDD tests for #3571 W3 — the reparse-point guard on shared-skill link tooling.

Incident class: a skills-link path materialized as an NTFS junction into
workspace-hub/.claude/skills was replaced via a child-enumerating delete, which
followed the reparse point and emptied the canonical tree. The guard's rule:
reparse-point nodes may only be removed with link-node-only primitives; any
recursive deletion on a path that probes as (or cannot be proven not to be) a
reparse point is refused, fail-closed.

Hermetic via the REPARSE_GUARD_FAKE seam — fixtures cannot mint real junctions.
"""

from __future__ import annotations

import datetime
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts" / "lib" / "reparse_guard.sh"
PROPAGATE = REPO_ROOT / "scripts" / "propagate-ecosystem.sh"
RESYNC = REPO_ROOT / "scripts" / "skills" / "resync-skill-links.sh"
RECONCILE = REPO_ROOT / "scripts" / "readiness" / "reconcile-ecosystem.sh"


def _bash(script: str, env: dict | None = None) -> subprocess.CompletedProcess:
    # Windows system dirs are load-bearing: without powershell.exe/fsutil on PATH
    # the probe returns "undetermined" and the guard (correctly) refuses everything.
    full_env = {"PATH": "/mingw64/bin:/usr/bin:/bin:/usr/local/bin"
                        ":/c/Windows/System32"
                        ":/c/Windows/System32/WindowsPowerShell/v1.0"}
    if env:
        full_env.update(env)
    return subprocess.run(["bash", "-c", script], env=full_env,
                          capture_output=True, text=True, timeout=60)


def _posix(p: Path) -> str:
    try:
        return subprocess.check_output(["cygpath", "-u", str(p)], text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return str(p)


def test_guarded_rm_rf_removes_plain_dir(tmp_path):
    d = tmp_path / "plain"
    (d / "child").mkdir(parents=True)
    res = _bash(f". '{_posix(GUARD)}'; guarded_rm_rf '{_posix(d)}'")
    assert res.returncode == 0, res.stderr
    assert not d.exists()


def test_guarded_rm_rf_refuses_reparse_point(tmp_path):
    d = tmp_path / "junction-like"
    (d / "canonical-child.md").parent.mkdir(parents=True)
    (d / "canonical-child.md").write_text("belongs to the link target")
    res = _bash(f". '{_posix(GUARD)}'; guarded_rm_rf '{_posix(d)}'",
                env={"REPARSE_GUARD_FAKE": _posix(d)})
    assert res.returncode == 1
    assert "reparse-guard: refusing" in res.stderr
    assert (d / "canonical-child.md").exists()          # nothing under it deleted


def test_is_reparse_point_absent_path_is_not_reparse(tmp_path):
    res = _bash(f". '{_posix(GUARD)}'; is_reparse_point '{_posix(tmp_path / 'nope')}'")
    assert res.returncode == 1


def test_propagate_backup_site_refuses_junctioned_backup(tmp_path):
    """The r2-finding-4 site: `rm -rf \"$backup\"` in propagate-ecosystem.sh.
    A leftover .bak-* entry that is a junction must be refused, with the
    (simulated) link target's children untouched — live --apply, not dry-run."""
    ws = tmp_path / "workspace-hub"
    (ws / "scripts" / "lib").mkdir(parents=True)
    (ws / "scripts" / "skills").mkdir(parents=True)
    shutil.copy(PROPAGATE, ws / "scripts" / "propagate-ecosystem.sh")
    shutil.copy(GUARD, ws / "scripts" / "lib" / "reparse_guard.sh")
    template = ws / ".claude" / "skills" / "_internal" / "guidelines"
    template.mkdir(parents=True)
    (template / "x.md").write_text("template")

    sib = tmp_path / "sibrepo"
    (sib / ".git").mkdir(parents=True)
    real = sib / ".claude" / "skills" / "guidelines"
    real.mkdir(parents=True)
    (real / "x.md").write_text("template")              # matches → backup path taken
    today = datetime.date.today().strftime("%Y%m%d")
    backup = sib / ".claude" / "skills" / f"guidelines.bak-{today}"
    backup.mkdir()
    (backup / "canonical.md").write_text("children belong to the link target")

    res = _bash(
        f"bash '{_posix(ws / 'scripts' / 'propagate-ecosystem.sh')}' "
        f"--skills-only --only sibrepo",
        env={"REPARSE_GUARD_FAKE": _posix(backup)})
    assert "reparse" in (res.stdout + res.stderr).lower(), res.stdout + res.stderr
    assert (backup / "canonical.md").exists()           # refusal fired BEFORE deletion
    assert (real / "x.md").exists()                     # slot untouched after refusal


def test_propagate_sources_the_guard():
    text = PROPAGATE.read_text(encoding="utf-8")
    assert "reparse_guard.sh" in text
    assert 'guarded_rm_rf "$backup"' in text            # the incident-class site
    assert '&& rm -rf "$backup"' not in text            # raw form must be gone


def test_resync_apply_path_is_covered_via_propagate():
    # resync --apply delegates every repair to propagate-ecosystem.sh --skills-only;
    # it must contain no recursive deletion of its own.
    text = RESYNC.read_text(encoding="utf-8")
    assert "rm -rf" not in text
    assert "propagate-ecosystem.sh" in text


def test_reconcile_skills_remediation_carries_linktype_warning():
    # The printed skills-DIVERGES remediation is the exact incident command shape;
    # it must warn the operator to check LinkType before running it.
    text = RECONCILE.read_text(encoding="utf-8")
    assert "LinkType" in text
