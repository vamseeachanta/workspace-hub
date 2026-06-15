"""TDD for #3137: capture Skill-tool calls (id -> short_name resolution).

Two surfaces under test:

1. ``scripts/skills/_skill_identity.normalize_skill_id`` — a pure resolver from a
   raw Skill-tool id (``<plugin>:<name>`` or bare) to the canonical workspace-hub
   short_name plus a source flag. Plugin-only / unresolved ids are recorded-and-
   flagged (raw id preserved), never silently dropped, never fabricated.

2. ``.claude/hooks/session-logger.sh`` — on a ``Skill`` PostToolUse payload it
   emits ``skill_name`` (resolved short_name when the id maps into the synthetic
   skills tree) + ``skill_id`` (raw) + ``skill_source`` flag, reading the id from
   ``.tool_input.skill`` (the empirically-confirmed field; 1080/1080 transcript
   records) with ``.tool_input.skill_name`` as a defensive fallback. Non-Skill,
   non-Read calls emit no skill_name.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

REPO = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], cwd=Path(__file__).parent, text=True
    ).strip()
)
SKILLS_DIR = REPO / "scripts" / "skills"
LIB = SKILLS_DIR / "_skill_identity.py"
SCRIPT = REPO / ".claude" / "hooks" / "session-logger.sh"


# --------------------------------------------------------------------------- #
# normalize_skill_id (pure resolver)
# --------------------------------------------------------------------------- #
@pytest.fixture
def ident():
    assert LIB.exists(), f"shared lib not yet written: {LIB}"
    if str(SKILLS_DIR) not in sys.path:
        sys.path.insert(0, str(SKILLS_DIR))
    spec = importlib.util.spec_from_file_location("_skill_identity", LIB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def tree(tmp_path):
    """A small skills tree mirroring the real layout.

    - corporate-tax-form-fill: bare, dir basename == short_name
    - workspace-hub/repo-sync: namespaced workspace-hub:repo-sync should resolve
    - dev/fancy: frontmatter name differs from dir basename (name-based resolve)
    - _archive/ghost: excluded universe member must NOT resolve
    """
    root = tmp_path / "skills"
    cases = {
        "corporate-tax-form-fill": "---\nname: corporate-tax-form-fill\n---\n",
        "workspace-hub/repo-sync": "---\nname: repo-sync\n---\n",
        "dev/fancy": "---\nname: Fancy Skill\n---\n",
        "_archive/ghost": "---\nname: ghost\n---\n",
    }
    for rel, body in cases.items():
        p = root / rel
        p.mkdir(parents=True)
        (p / "SKILL.md").write_text(body)
    return root


def test_normalize_bare_resolved(ident, tree):
    r = ident.normalize_skill_id("corporate-tax-form-fill", tree)
    assert r["skill_name"] == "corporate-tax-form-fill"
    assert r["skill_source"] == "workspace-hub"
    assert r["skill_id"] == "corporate-tax-form-fill"


def test_normalize_namespaced_workspace_hub(ident, tree):
    r = ident.normalize_skill_id("workspace-hub:repo-sync", tree)
    assert r["skill_name"] == "repo-sync"
    assert r["skill_source"] == "workspace-hub"
    assert r["skill_id"] == "workspace-hub:repo-sync"


def test_normalize_plugin_unresolved(ident, tree):
    # codex:rescue has no counterpart in the wshub tree -> flagged, not dropped.
    r = ident.normalize_skill_id("codex:rescue", tree)
    assert r["skill_name"] == ""
    assert r["skill_source"] == "plugin"
    assert r["skill_id"] == "codex:rescue"


def test_normalize_superpowers_unmirrored(ident, tree):
    r = ident.normalize_skill_id("superpowers:writing-plans", tree)
    assert r["skill_name"] == ""
    assert r["skill_source"] == "plugin"
    assert r["skill_id"] == "superpowers:writing-plans"


def test_normalize_bare_unresolved(ident, tree):
    # A bare id that maps to nothing (e.g. a slash-command, not a SKILL.md):
    # recorded-and-flagged as unresolved, raw id preserved, no fabrication.
    r = ident.normalize_skill_id("whats-next", tree)
    assert r["skill_name"] == ""
    assert r["skill_source"] == "unresolved"
    assert r["skill_id"] == "whats-next"


def test_normalize_frontmatter_name(ident, tree):
    # dir basename is 'fancy' but frontmatter name is 'Fancy Skill'.
    # The canonical short_name is the lowercased frontmatter name.
    r = ident.normalize_skill_id("fancy", tree)
    assert r["skill_name"] == "fancy skill"
    assert r["skill_source"] == "workspace-hub"


def test_normalize_archived_does_not_resolve(ident, tree):
    # An excluded (_archive) skill must NOT resolve.
    r = ident.normalize_skill_id("ghost", tree)
    assert r["skill_name"] == ""
    assert r["skill_source"] == "unresolved"
    assert r["skill_id"] == "ghost"


def test_normalize_empty_id(ident, tree):
    r = ident.normalize_skill_id("", tree)
    assert r["skill_name"] == ""
    assert r["skill_source"] == "unresolved"
    assert r["skill_id"] == ""


# --------------------------------------------------------------------------- #
# session-logger.sh Skill-tool emit
# --------------------------------------------------------------------------- #
def _make_repo(tmp_path: Path) -> Path:
    """A throwaway repo with the hook + a synthetic skills tree."""
    repo = tmp_path / "repo-under-test"
    (repo / ".claude" / "hooks").mkdir(parents=True)
    shutil.copy2(SCRIPT, repo / ".claude" / "hooks" / "session-logger.sh")
    (repo / "scripts" / "ai").mkdir(parents=True)
    (repo / "scripts" / "ai" / "session-params.py").write_text("print('')\n", encoding="utf-8")
    (repo / ".git").mkdir()
    # synthetic skills tree
    for rel, name in [
        ("workspace-hub/repo-sync", "repo-sync"),
        ("corporate-tax-form-fill", "corporate-tax-form-fill"),
    ]:
        d = repo / ".claude" / "skills" / rel
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"---\nname: {name}\n---\n", encoding="utf-8")
    return repo


def _run_hook(repo: Path, payload: dict) -> list[dict]:
    env = os.environ.copy()
    env["WORKSPACE_HUB"] = str(repo)
    env["CLAUDE_SESSION_LOGGING"] = "true"
    script_path = repo / ".claude" / "hooks" / "session-logger.sh"
    result = subprocess.run(
        ["bash", str(script_path), "post"],
        cwd=repo,
        env=env,
        input=json.dumps(payload) + "\n",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    day = datetime.now().strftime("%Y%m%d")
    state_log = repo / ".claude" / "state" / "sessions" / f"session_{day}.jsonl"
    assert state_log.exists()
    return [
        json.loads(line)
        for line in state_log.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_emit_field_is_skill_resolved(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    entries = _run_hook(
        repo, {"session_id": "s1", "tool_name": "Skill", "tool_input": {"skill": "repo-sync"}}
    )
    e = next(x for x in entries if x.get("tool") == "Skill")
    assert e["skill_id"] == "repo-sync"
    assert e["skill_name"] == "repo-sync"
    assert e["skill_source"] == "workspace-hub"


def test_emit_namespaced_workspace_hub(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    entries = _run_hook(
        repo,
        {"tool_name": "Skill", "tool_input": {"skill": "workspace-hub:repo-sync"}},
    )
    e = next(x for x in entries if x.get("tool") == "Skill")
    assert e["skill_id"] == "workspace-hub:repo-sync"
    assert e["skill_name"] == "repo-sync"
    assert e["skill_source"] == "workspace-hub"


def test_emit_plugin_recorded_not_dropped(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    entries = _run_hook(
        repo, {"tool_name": "Skill", "tool_input": {"skill": "codex:rescue"}}
    )
    e = next(x for x in entries if x.get("tool") == "Skill")
    # plugin id is logged + flagged, raw id preserved, no fabricated skill_name.
    assert e["skill_id"] == "codex:rescue"
    assert e.get("skill_name", "") == ""
    assert e["skill_source"] == "plugin"


def test_emit_defensive_fallback_skill_name(tmp_path: Path) -> None:
    # If a future harness puts the id under .tool_input.skill_name, fall back.
    repo = _make_repo(tmp_path)
    entries = _run_hook(
        repo, {"tool_name": "Skill", "tool_input": {"skill_name": "repo-sync"}}
    )
    e = next(x for x in entries if x.get("tool") == "Skill")
    assert e["skill_id"] == "repo-sync"
    assert e["skill_source"] == "workspace-hub"


def test_emit_no_skill_field_safe(tmp_path: Path) -> None:
    # Missing both fields: no crash, no skill_name/skill_id emitted.
    repo = _make_repo(tmp_path)
    entries = _run_hook(repo, {"tool_name": "Skill", "tool_input": {}})
    e = next(x for x in entries if x.get("tool") == "Skill")
    assert "skill_name" not in e
    assert "skill_id" not in e


def test_non_skill_non_read_emits_no_skill_name(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    entries = _run_hook(
        repo,
        {"tool_name": "Bash", "tool_input": {"command": "git status"}},
    )
    e = next(x for x in entries if x.get("tool") == "Bash")
    assert "skill_name" not in e
    assert "skill_id" not in e
    assert "skill_source" not in e


def test_read_of_skill_md_still_emits_relpath(tmp_path: Path) -> None:
    # Regression: the #3112 Read-of-SKILL.md path must still emit a rel-path
    # skill_name (and must NOT emit skill_id/skill_source — that's Skill-only).
    repo = _make_repo(tmp_path)
    fp = str(repo / ".claude" / "skills" / "workspace-hub" / "repo-sync" / "SKILL.md")
    entries = _run_hook(
        repo, {"tool_name": "Read", "tool_input": {"file_path": fp}}
    )
    e = next(x for x in entries if x.get("tool") == "Read")
    assert e["skill_name"] == "workspace-hub/repo-sync"
    assert "skill_id" not in e
    assert "skill_source" not in e
