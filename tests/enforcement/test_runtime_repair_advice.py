"""Execute generated advice only in disposable repositories.

Expected scope follows issue 3866: target outputs change, caller bytes do not.
No empirical coefficients or numerical acceptance thresholds are used.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = "scripts/enforcement/check-soul-runtime-drift.sh"
OUTPUTS = [f"config/agents/{provider}/{name}" for provider, name in (
    ("hermes", "SOUL.runtime.md"), ("claude", "SOUL.runtime.md"),
    ("codex", "SOUL.runtime.md"), ("codex", "AGENTS.runtime.md"),
    ("gemini", "SOUL.runtime.md"), ("agy", "SOUL.runtime.md"),
)]


def run(args, cwd, env):
    return subprocess.run(args, check=False, cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=60)


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


@pytest.fixture
def repair(tmp_path):
    target = tmp_path / "target 'quoted' $cash; space"
    caller = tmp_path / "foreign repository"
    inputs = [CHECKER, "scripts/agents/build-soul-runtime.sh",
              "scripts/agents/soul-runtime-lib.sh", "config/agents/SHARED_SOUL.md",
              ".claude/rules/coding-style.md", ".claude/rules/patterns.md", "GEMINI.md"]
    inputs += [f"config/agents/{p}/" + ("SOUL.md" if p == "hermes" else "SOUL.delta.md")
               for p in ("hermes", "claude", "codex", "gemini", "agy")]
    for relative in inputs:
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, dest)
    caller.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    for repo in (target, caller):
        result = run(["git", "-c", "init.templateDir=", "init", "-q", str(repo)], repo, env)
        assert result.returncode == 0, result.stderr
    # A caller-side executable makes an accidental relative invocation observable.
    bait = caller / "scripts/agents/build-soul-runtime.sh"
    bait.parent.mkdir(parents=True)
    bait.write_text("printf damaged > sentinel\n", encoding="utf-8")
    (caller / "sentinel").write_bytes(b"preserve caller")
    (target / "config/agents/unrelated.runtime.md").write_bytes(b"do not stage")
    result = run(["bash", str(target / CHECKER), "--quiet"], caller, env)
    assert result.returncode == 1, result.stdout + result.stderr
    advice, = [line.removeprefix("Fix: ") for line in result.stdout.splitlines()
               if line.startswith("Fix: ")]
    return target, caller, env, advice


@pytest.mark.parametrize("bindings", [False, True])
def test_repair_targets_only_verified_repository(repair, bindings):
    """Hand-derived scope: six declared outputs staged; caller and extra file excluded."""
    target, caller, env, advice = repair
    before = snapshot(caller)
    if bindings:
        env.update(GIT_DIR=str(caller / ".git"), GIT_WORK_TREE=str(caller),
                   GIT_COMMON_DIR=str(caller / ".git"),
                   GIT_INDEX_FILE=str(caller / ".git/alternate-index"))
    result = run(["bash", "-c", advice], caller, env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert snapshot(caller) == before
    clean_env = {k: v for k, v in env.items() if not k.startswith("GIT_")}
    staged = run(["git", "diff", "--cached", "--name-only"], target, clean_env)
    assert set(staged.stdout.splitlines()) == set(OUTPUTS)
    assert all((target / path).is_file() for path in OUTPUTS)
    checked = run(["bash", str(target / CHECKER), "--quiet"], caller, env)
    assert checked.returncode == 0, checked.stdout + checked.stderr


def test_failed_target_entry_leaves_caller_unchanged(repair):
    """An unavailable target must short-circuit before rebuild, staging or readback."""
    target, caller, env, advice = repair
    target.rename(target.with_name("relocated target"))
    before = snapshot(caller)
    result = run(["bash", "-c", advice], caller, env)
    assert result.returncode != 0
    assert snapshot(caller) == before


def test_failed_rebuild_does_not_stage_or_read_back(repair):
    """A failed producer cannot authorize staging existing or partial outputs."""
    target, caller, env, advice = repair
    (target / "scripts/agents/build-soul-runtime.sh").write_text("exit 1\n", encoding="utf-8")
    before = snapshot(caller)
    result = run(["bash", "-c", advice], caller, env)
    assert result.returncode != 0
    assert snapshot(caller) == before
    staged = run(["git", "diff", "--cached", "--name-only"], target, env)
    assert staged.stdout == ""
