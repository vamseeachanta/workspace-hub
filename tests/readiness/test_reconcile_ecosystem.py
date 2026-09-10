"""Safety + contract tests for reconcile-ecosystem.sh (the corrective-action driver).

The script performs (opt-in) destructive git operations across the repo ecosystem, so
the load-bearing tests are STATIC safety invariants on the script text plus a hermetic
read-only smoke run. We deliberately do not exercise --apply against real repos here;
the guard (worktree_guard.py, separately tested) is the runtime backstop.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "readiness" / "reconcile-ecosystem.sh"
TEXT = SCRIPT.read_text()


def test_script_exists_and_is_executable():
    assert SCRIPT.exists()
    assert SCRIPT.stat().st_mode & 0o111, "reconcile-ecosystem.sh must be executable"


def test_bash_syntax_is_valid():
    r = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("danger", [
    r"reset\s+--hard",          # never blow away history/working tree
    r"clean\s+-[a-zA-Z]*f",     # never rm untracked en masse
    r"push\s+.*--force",        # never force-push
    r"checkout\s+--\s+\.",      # never discard the whole working tree
    r"stash\s+(drop|clear)",    # never destroy stashed work
])
def test_no_dangerous_git_patterns(danger):
    assert not re.search(danger, TEXT), f"reconciler must not contain `{danger}`"


def test_force_delete_only_for_pr_merged_branches():
    # `git branch -D` (force) is permitted ONLY to remove squash-merged branches whose PR is
    # MERGED — GitHub squash-merge breaks ancestry, so `-d` would refuse a branch whose work IS
    # in main. It must be co-located with the gh merged-PR guard AND the worktree guard.
    if re.search(r"branch\s+-D\b", TEXT):
        assert "pr list --state merged" in TEXT, "force-delete must be gated by a merged-PR check"
        assert "safe-delete-branch" in TEXT, "force-delete must also pass the worktree guard"


def test_squash_merge_detection_degrades_without_gh():
    # The squash-merge pass must be guarded by a `command -v gh` check so absence of gh is a
    # graceful no-op (ancestry pass still runs), not a crash.
    assert "command -v gh" in TEXT


def test_destructive_ops_are_guard_gated():
    # Branch / worktree disposal must route through the deny-by-default guard.
    assert "worktree_guard.py" in TEXT
    assert "safe-delete-branch" in TEXT
    assert "safe-remove-worktree" in TEXT


def test_guard_is_invoked_in_target_repo_cwd():
    # worktree_guard reads `git worktree list` from CWD, so for a SIBLING repo it must run
    # with that repo as cwd — otherwise it checks workspace-hub's worktrees (wrong repo) and
    # a sibling branch checked out in a worktree would wrongly pass the guard.
    assert re.search(r"cd \"\$repo\" && python3 \"\$GUARD\" safe-delete-branch", TEXT), \
        "guard execution must be repo-scoped (cd \"$repo\")"
    # the printed NEEDS-APPROVAL command must be repo-scoped too
    assert "cd '$repo' && python3 '$GUARD' safe-delete-branch" in TEXT


def test_dirty_work_is_never_silently_discarded():
    # The only thing the driver does with a dirty tree is `stash push` (recoverable) or surface it.
    assert "stash push" in TEXT
    # A bare `git restore`/`checkout .` discard of dirty paths must not appear.
    assert not re.search(r"git[^\n]*restore[^\n]*--worktree", TEXT)


def test_default_mode_is_report_only():
    # APPLY must default off; the apply block must be gated on it.
    assert "APPLY=0" in TEXT
    assert 'if [ "$APPLY" = 1 ]' in TEXT


def test_primary_host_is_destructive_locked():
    # dev-primary (intentional-worktree automation host) must default to report-only disposal.
    assert 'MACHINE" = "dev-primary"' in TEXT
    assert "DESTRUCTIVE_OK=0" in TEXT


def test_read_only_smoke_run_mutates_nothing(tmp_path):
    """A default (no-flag) run is read-only: a clean throwaway repo stays clean and the
    script exits 0. Runs the driver with REPO_ROOT redirected via a fake script dir is not
    feasible (paths are git-derived), so we assert the contract holds for THIS checkout:
    capture porcelain before/after a --json run (which never reaches the apply block)."""
    before = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
                            capture_output=True, text=True).stdout
    r = subprocess.run(["bash", str(SCRIPT), "--json"], capture_output=True, text=True,
                       timeout=300)
    assert r.returncode == 0, r.stderr[-2000:]
    after = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
                           capture_output=True, text=True).stdout
    assert before == after, "read-only run must not change the working tree"
    assert '"machine"' in r.stdout and '"plan"' in r.stdout


def test_machine_slug_mapping_matches_collector():
    # The slug case-map must mirror collect-equality.sh so a box reconciles its own column.
    for host_alias, slug in [("ace-linux-1", "dev-primary"), ("ace-linux-2", "dev-secondary")]:
        assert slug in TEXT
        assert host_alias in TEXT
    # Windows boxes: assert the SHAPE of the case arm (own hostname -> own slug, plus the
    # WF0 licensed-win-* back-compat alias) rather than pinning the real computer names —
    # config/workstations/registry.yaml is the SSOT for hostname aliases.
    for n in (1, 2):
        arm = re.search(rf'^\s*ace-win-{n}\*[^)]*\)\s*MACHINE="ace-win-{n}"', TEXT, re.M)
        assert arm, f"ace-win-{n} must have a case arm mapping its own hostname to its slug"
        assert f"licensed-win-{n}*" in arm.group(0), \
            f"ace-win-{n} case arm must keep the licensed-win-{n} back-compat alias"
