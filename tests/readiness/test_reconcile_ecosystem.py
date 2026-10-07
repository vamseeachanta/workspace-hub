"""Safety + contract tests for reconcile-ecosystem.sh (the corrective-action driver).

The script performs (opt-in) destructive git operations across the repo ecosystem, so
the load-bearing tests are STATIC safety invariants on the script text plus a hermetic
read-only smoke run. We deliberately do not exercise --apply against real repos here;
the guard (worktree_guard.py, separately tested) is the runtime backstop.
"""
from __future__ import annotations

import re
import subprocess
import json
import os
import shutil
import sys
import shlex
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "readiness" / "reconcile-ecosystem.sh"
TEXT = SCRIPT.read_text()


def fixture_git(root, env, *args):
    return subprocess.run(["git", "-C", str(root), *args], env=env,
                          capture_output=True, text=True, check=True)


def fixture_repo(tmp_path, name="owner root"):
    root = tmp_path / name
    dependencies = ["scripts/readiness/reconcile-ecosystem.sh",
                    "scripts/readiness/lib/machine-identity.sh",
                    "scripts/lib/reparse_guard.sh", "scripts/skills/native_skill_root.py"]
    for relative in dependencies:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / relative, target)
    matrix = root / "scripts/readiness/build-equality-matrix.py"
    matrix.write_text('print(\'{"skills": "DIVERGES"}\')\n', encoding="utf-8")
    bins = tmp_path / "bins"
    bins.mkdir()
    interpreter = shlex.quote(Path(sys.executable).as_posix())
    launcher = '#!/usr/bin/env bash\nexec ' + interpreter + ' "$@"\n'
    for name in ("python", "python3"):
        (bins / name).write_text(launcher, encoding="utf-8", newline="\n")
        (bins / name).chmod(0o755)
    uv = ('#!/usr/bin/env bash\nwhile [[ "$1" == -* || "$1" == run || '
          '"$1" == python ]]; do shift; done\nexec ' + interpreter + ' "$@"\n')
    (bins / "uv").write_text(uv, encoding="utf-8", newline="\n")
    (bins / "uv").chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(PATH=str(bins) + os.pathsep + env["PATH"], HOME=str(tmp_path / "home"),
               GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               RECONCILE_MACHINE="fixture", EQ_MACHINE="fixture")
    fixture_git(root, env, "init", "-q")
    fixture_git(root, env, "config", "core.symlinks", "false")
    for provider in (".codex", ".gemini"):
        path = root / provider / "skills"
        path.parent.mkdir()
        path.write_text("indexed sentinel\n", encoding="utf-8")
        fixture_git(root, env, "add", "--", provider + "/skills")
        path.write_text("working sentinel\n", encoding="utf-8")
    return root, env


def skills_advice(root, env):
    result = subprocess.run(["bash", str(root / "scripts/readiness/reconcile-ecosystem.sh"),
                             "--json"], env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    entries = [x for x in json.loads(result.stdout)["plan"] if "[skills]" in x["action"]]
    assert len(entries) == 1, result.stdout
    return entries[0]


def execute_advice(advice, cwd, env):
    return subprocess.run(["bash", "-c", advice["command"]], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=30)


@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize("name", ["owner root", "owner's root"])
def test_generated_advice_binds_root_and_preserves_foreign_cwd(tmp_path, native, name):
    root, env = fixture_repo(tmp_path, name)
    if native:
        (root / ".agents/skills").mkdir(parents=True)
    foreign = tmp_path / "foreign"
    for provider in (".codex", ".gemini"):
        path = foreign / provider / "skills"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"foreign sentinel")
    advice = skills_advice(root, env)
    result = execute_advice(advice, foreign, env)
    assert result.returncode == 0, result.stderr
    for provider in (".codex", ".gemini"):
        assert (foreign / provider / "skills").read_bytes() == b"foreign sentinel"
    expected = "working sentinel\n" if native else "indexed sentinel\n"
    assert (root / ".codex/skills").read_text() == expected
    assert (root / ".gemini/skills").read_text() == "indexed sentinel\n"


def test_advice_never_expands_initial_provider_set(tmp_path):
    root, env = fixture_repo(tmp_path)
    (root / ".agents/skills").mkdir(parents=True)
    advice = skills_advice(root, env)
    (root / ".agents/skills").rmdir()
    result = execute_advice(advice, tmp_path, env)
    assert result.returncode == 0, result.stderr
    assert (root / ".codex/skills").read_text() == "working sentinel\n"


def test_stale_advice_blocks_before_any_mutation(tmp_path):
    root, env = fixture_repo(tmp_path)
    advice = skills_advice(root, env)
    (root / ".agents/skills").mkdir(parents=True)
    result = execute_advice(advice, tmp_path, env)
    assert result.returncode != 0
    assert fixture_git(root, env, "config", "--get", "core.symlinks").stdout.strip() == "false"
    for provider in (".codex", ".gemini"):
        assert (root / provider / "skills").read_text() == "working sentinel\n"


def test_missing_selected_root_refuses_foreign_mutation(tmp_path):
    root, env = fixture_repo(tmp_path)
    advice = skills_advice(root, env)
    root.rename(tmp_path / "moved")
    result = execute_advice(advice, tmp_path, env)
    assert result.returncode != 0


def test_generated_advice_refuses_failed_runner(tmp_path):
    root, env = fixture_repo(tmp_path)
    advice = skills_advice(root, env)
    (tmp_path / "bins/uv").write_text("#!/usr/bin/env bash\nexit 127\n",
                                       encoding="utf-8", newline="\n")
    result = execute_advice(advice, tmp_path, env)
    assert result.returncode != 0
    for provider in (".codex", ".gemini"):
        assert (root / provider / "skills").read_text() == "working sentinel\n"


def test_advice_restores_tracked_gemini_symlink(tmp_path):
    root, env = fixture_repo(tmp_path)
    (root / ".agents/skills").mkdir(parents=True)
    (root / "target").write_text("target payload", encoding="utf-8")
    blob = subprocess.run(["git", "-C", str(root), "hash-object", "-w", "--stdin"],
                          input="../target", text=True, env=env, capture_output=True, check=True).stdout.strip()
    fixture_git(root, env, "update-index", "--cacheinfo", f"120000,{blob},.gemini/skills")
    result = execute_advice(skills_advice(root, env), tmp_path, env)
    assert result.returncode == 0, result.stderr
    assert (root / ".gemini/skills").is_symlink()
    assert (root / ".gemini/skills").read_text() == "target payload"
    assert (root / ".codex/skills").read_text() == "working sentinel\n"


@pytest.mark.parametrize("reply,exit_code", [("native", 3), ("absent", 2), ("garbage", 0)])
def test_bad_probe_reply_excludes_codex(tmp_path, reply, exit_code):
    root, env = fixture_repo(tmp_path)
    helper = root / "scripts/skills/native_skill_root.py"
    helper.write_text(f"print({reply!r})\nraise SystemExit({exit_code})\n", encoding="utf-8")
    advice = skills_advice(root, env)
    assert "blocked" in advice["action"].lower()
    assert ".codex/skills" not in advice["command"]


def test_script_exists_and_is_executable():
    assert SCRIPT.exists()
    if os.name == "nt":
        pytest.skip("Windows stat has no POSIX executable bits; canonical Git mode is reviewed separately")
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
    assert re.search(r"cd \"\$repo\" && \"\$PY\" \"\$GUARD\" safe-delete-branch", TEXT), \
        "guard execution must be repo-scoped (cd \"$repo\")"
    # The existing squash-merged printed arm is scoped; the other arm is follow-on 3866.
    assert "cd '$repo' && $PY '$GUARD' safe-delete-branch" in TEXT


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
    root, env = fixture_repo(tmp_path)
    before = fixture_git(root, env, "status", "--porcelain").stdout
    assert skills_advice(root, env)["class"] == "NEEDS-APPROVAL"
    assert fixture_git(root, env, "status", "--porcelain").stdout == before


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
