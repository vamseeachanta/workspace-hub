"""Tests for SOUL.runtime.md auto-load wiring (#2725).

6 cases verifying the wiring layer added in Phases 1-3 of #2725:
  - @file import directive present in CLAUDE.md and GEMINI.md
  - target runtime artifacts exist on disk
  - sentinel rule from SHARED_SOUL.md propagates through build into runtime
    artifacts (cross-check for drift between SHARED source and built artifact)
  - drift script returns exit 0 in clean state (integrates the auto-load
    wiring assertion added by Phase 3)

These tests cannot verify that a LIVE Claude or Gemini session actually
loads the runtime artifact into its system prompt — that requires a fresh
session and is captured per the §Empirical Session Test Protocol in
docs/sessions/2026-05-XX-2725-fresh-session-test-{claude,gemini}.md. The
tests here verify the wiring is *in place*; the transcripts verify the
wiring *resolves*.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
GEMINI_MD = REPO_ROOT / "GEMINI.md"
CLAUDE_RUNTIME = REPO_ROOT / "config" / "agents" / "claude" / "SOUL.runtime.md"
GEMINI_RUNTIME = REPO_ROOT / "config" / "agents" / "gemini" / "SOUL.runtime.md"
SHARED_SOUL = REPO_ROOT / "config" / "agents" / "SHARED_SOUL.md"
DRIFT_SCRIPT = REPO_ROOT / "scripts" / "enforcement" / "check-soul-runtime-drift.sh"

CLAUDE_IMPORT = "@config/agents/claude/SOUL.runtime.md"
GEMINI_IMPORT = "@config/agents/gemini/SOUL.runtime.md"

# Stable sentinel rule that existed before #2724 (line 63 of SHARED_SOUL.md
# at HEAD `4676f6d6b`). Chosen because it's a stable rule unlikely to be
# renamed and is unique to SHARED_SOUL.md (not present in standard rules).
SENTINEL = "Subagent Write phantom hazard"


def _file_contains_line(path: Path, line: str) -> bool:
    """Return True if `path` contains `line` as an exact line (matches grep -Fxq)."""
    if not path.exists():
        return False
    with path.open("r", encoding="utf-8") as fh:
        return any(raw.rstrip("\n") == line for raw in fh)


def test_claude_md_has_autoload_directive():
    """CLAUDE.md must contain the @file import directive for SOUL.runtime.md."""
    assert _file_contains_line(CLAUDE_MD, CLAUDE_IMPORT), (
        f"CLAUDE.md missing literal line: {CLAUDE_IMPORT!r}. "
        f"Without this, the Must-Fire Rules from SHARED_SOUL.md do not reach "
        f"Claude Code sessions. See #2725."
    )


def test_gemini_md_has_autoload_directive():
    """GEMINI.md must contain the @file.md import directive for SOUL.runtime.md."""
    assert _file_contains_line(GEMINI_MD, GEMINI_IMPORT), (
        f"GEMINI.md missing literal line: {GEMINI_IMPORT!r}. "
        f"Without this, the Must-Fire Rules from SHARED_SOUL.md do not reach "
        f"Gemini CLI sessions. See #2725."
    )


def test_claude_runtime_artifact_target_exists():
    """The path CLAUDE.md @-imports must resolve to an existing file."""
    assert CLAUDE_RUNTIME.exists(), (
        f"CLAUDE.md imports {CLAUDE_IMPORT} but the target file does not exist. "
        f"Run: bash scripts/agents/build-soul-runtime.sh"
    )


def test_gemini_runtime_artifact_target_exists():
    """The path GEMINI.md @-imports must resolve to an existing file."""
    assert GEMINI_RUNTIME.exists(), (
        f"GEMINI.md imports {GEMINI_IMPORT} but the target file does not exist. "
        f"Run: bash scripts/agents/build-soul-runtime.sh"
    )


def test_sentinel_propagates_from_shared_to_both_runtime_artifacts():
    """A sentinel rule in SHARED_SOUL.md must appear in both runtime artifacts.

    This is the build-pipeline check: if scripts/agents/build-soul-runtime.sh
    has drifted from SHARED_SOUL.md, the sentinel won't propagate. Redundant
    with check-soul-runtime-drift.sh's diff-based check but explicit and
    catches the case where the runtime artifacts exist but were built from
    a stale SHARED_SOUL.md.
    """
    shared_content = SHARED_SOUL.read_text(encoding="utf-8")
    claude_content = CLAUDE_RUNTIME.read_text(encoding="utf-8")
    gemini_content = GEMINI_RUNTIME.read_text(encoding="utf-8")

    assert SENTINEL in shared_content, (
        f"Sentinel {SENTINEL!r} not found in SHARED_SOUL.md. The test sentinel "
        f"may have been renamed; update SENTINEL at top of test_soul_auto_load.py."
    )
    assert SENTINEL in claude_content, (
        f"Sentinel {SENTINEL!r} present in SHARED_SOUL.md but missing from "
        f"claude/SOUL.runtime.md. Build pipeline drift; "
        f"run: bash scripts/agents/build-soul-runtime.sh"
    )
    assert SENTINEL in gemini_content, (
        f"Sentinel {SENTINEL!r} present in SHARED_SOUL.md but missing from "
        f"gemini/SOUL.runtime.md. Build pipeline drift; "
        f"run: bash scripts/agents/build-soul-runtime.sh"
    )


def test_drift_script_returns_zero_in_clean_state():
    """check-soul-runtime-drift.sh must exit 0 when all wiring is in place.

    This is the integration check: positive case of Phase 3's auto-load
    wiring assertion. The negative case (script returns 1 when wiring is
    broken) is verified manually per the plan's §Drift-check regression
    test because it requires destructive working-tree edits which are
    not test-safe.
    """
    result = subprocess.run(
        ["bash", str(DRIFT_SCRIPT), "--quiet"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        f"check-soul-runtime-drift.sh returned exit {result.returncode} "
        f"in what should be a clean state.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
