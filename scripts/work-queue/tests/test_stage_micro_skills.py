"""
WRK-1142: Stage micro-skill auto-load tests.

Tests:
  T50: start_stage.py stdout includes stage-04 micro-skill content
  T51: stage-N-prompt.md includes stage-10 micro-skill content (exit 0, fresh artifact)
  T52: missing micro-skill → warning string, no crash
  T53: duplicate micro-skill files → RuntimeError / non-zero exit
  T54: all 20 micro-skills have ≥5 content lines
  T55: work-queue-workflow/SKILL.md ≤150 lines after migration
"""
from __future__ import annotations

import glob
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[3]
START_STAGE = BASE / "scripts" / "work-queue" / "start_stage.py"
STAGES_DIR = BASE / ".claude" / "skills" / "workspace-hub" / "stages"
SKILL_MD = BASE / ".claude" / "skills" / "workspace-hub" / "work-queue-workflow" / "SKILL.md"
ASSETS_DIR = BASE / ".claude" / "work-queue" / "assets"


def _run_start_stage(wrk_id: str, stage: int, extra_env: dict | None = None) -> tuple[str, int]:
    """Run start_stage.py and return (stdout+stderr, exit_code)."""
    import os
    env = os.environ.copy()
    env["WORKSPACE_HUB"] = str(BASE)
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        [sys.executable, str(START_STAGE), wrk_id, str(stage)],
        capture_output=True, text=True, env=env,
    )
    return result.stdout + result.stderr, result.returncode


def test_T50_start_stage_stdout_includes_stage04_micro_skill():
    """T50: start_stage.py WRK-1142 4 stdout contains unique stage-04 micro-skill text.

    Checks for 'scripts-over-LLM' and asserts exit code 0.
    """
    out, rc = _run_start_stage("WRK-1142", 4)
    assert rc == 0, f"start_stage.py exited {rc} for stage 4.\nOutput:\n{out[:800]}"
    assert "scripts-over-LLM" in out or "Scripts-over-LLM" in out, (
        f"Expected 'scripts-over-LLM' in start_stage.py stdout for stage 4 "
        f"(proves micro-skill was loaded).\nGot:\n{out[:800]}"
    )


def test_T51_prompt_package_includes_stage10_micro_skill():
    """T51: stage-N-prompt.md written by start_stage.py includes stage-10 unique content.

    Checks for 'TDD MANDATORY' which is in stage-10 micro-skill but not stage-04.
    Deletes any stale artifact before running so the test cannot pass on old output.
    Asserts exit code 0.
    """
    prompt_path = ASSETS_DIR / "WRK-1142" / "stage-10-prompt.md"
    if prompt_path.exists():
        prompt_path.unlink()

    out, rc = _run_start_stage("WRK-1142", 10)
    assert rc == 0, f"start_stage.py exited {rc} for stage 10.\nOutput:\n{out[:800]}"
    assert prompt_path.exists(), f"stage-10-prompt.md not written to {prompt_path}"
    content = prompt_path.read_text()
    assert "TDD MANDATORY" in content, (
        f"Expected 'TDD MANDATORY' (stage-10 unique) in stage-10-prompt.md.\n"
        f"Got first 500 chars:\n{content[:500]}"
    )


def test_T52_missing_micro_skill_warns_no_crash():
    """T52: valid stage contract + absent micro-skill → warning, no crash."""
    spec = importlib.util.spec_from_file_location("start_stage", START_STAGE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    result = mod._load_stage_micro_skill(99, str(BASE))
    assert "not found" in result.lower() or "stage micro-skill" in result.lower(), (
        f"Expected warning message for missing micro-skill, got: {result!r}"
    )


def test_T53_duplicate_micro_skill_raises_error():
    """T53: two stage-04-*.md files → RuntimeError from _load_stage_micro_skill."""
    spec = importlib.util.spec_from_file_location("start_stage", START_STAGE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir) / ".claude" / "skills" / "workspace-hub" / "stages"
        skill_dir.mkdir(parents=True)
        (skill_dir / "stage-04-plan-draft.md").write_text("# dup 1")
        (skill_dir / "stage-04-plan-draft-extra.md").write_text("# dup 2")

        import pytest
        with pytest.raises(RuntimeError, match="(?i)multiple"):
            mod._load_stage_micro_skill(4, tmpdir)


def test_T54_all_20_micro_skills_have_5_or_more_content_lines():
    """T54: all 20 stage micro-skill files have ≥5 non-blank lines."""
    for n in range(1, 21):
        pattern = str(STAGES_DIR / f"stage-{n:02d}-*.md")
        matches = glob.glob(pattern)
        assert len(matches) == 1, f"Expected exactly 1 file for stage {n:02d}, found: {matches}"
        path = Path(matches[0])
        content_lines = [l for l in path.read_text().splitlines() if l.strip()]
        assert len(content_lines) >= 5, (
            f"{path.name}: only {len(content_lines)} non-blank lines (need ≥5)"
        )


def test_T55_work_queue_workflow_skill_md_at_most_150_lines():
    """T55: work-queue-workflow/SKILL.md ≤150 lines after migration."""
    assert SKILL_MD.exists(), f"SKILL.md not found at {SKILL_MD}"
    n = len(SKILL_MD.read_text().splitlines())
    assert n <= 150, f"SKILL.md has {n} lines (limit: 150 after migration)"
