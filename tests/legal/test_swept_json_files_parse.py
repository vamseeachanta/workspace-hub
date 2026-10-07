"""Every .json / .jsonl file the C19b codename sweep changed still parses (Codex r1).

A placeholder replacement inside a JSON string must preserve JSON escaping, and a
.jsonl file must carry one JSON value per non-empty line. Two sources of files:

- ``SWEPT``: the files PR #3899 changed, fixed here so the check survives the merge;
- the files changed against the PR base, when a base ref resolves (``JSON_CHECK_BASE``,
  then the PR base branch, then ``origin/main``), so a later sweep is covered too.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

SWEPT = [
    ".claude/state/corrections/session_20260131.jsonl",
    ".claude/state/corrections/session_20260208.jsonl",
    ".claude/state/corrections/session_20260223.jsonl",
    ".claude/state/corrections/session_20260224.jsonl",
    ".claude/state/corrections/session_20260424.jsonl",
    ".claude/state/corrections/session_20260501.jsonl",
    ".claude/state/corrections/session_20260512.jsonl",
    ".claude/state/corrections/session_20260518.jsonl",
    "config/agents/codex/state-snapshots/history.jsonl",
    "docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-1-codex.jsonl",
    "docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-2-codex.jsonl",
    "docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-3-codex.jsonl",
    "docs/plans/agent-swarm-audits/2026-05-10/logs/swarm-4-codex.jsonl",
]

_BASES = ["origin/fix/c19-private-config-behaviour", "fix/c19-private-config-behaviour",
          "origin/main"]


def _git(*args: str) -> subprocess.CompletedProcess:
    # Inherited repository bindings would override cwd; clear them.
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE")}
    return subprocess.run(["git", *args], cwd=REPO_ROOT, env=env,
                          capture_output=True, text=True)


def _changed_against_base() -> list[str]:
    for base in filter(None, [os.environ.get("JSON_CHECK_BASE"), *_BASES]):
        if _git("rev-parse", "--verify", "--quiet", base + "^{commit}").returncode == 0:
            out = _git("diff", "--name-only", "--diff-filter=AMR", f"{base}...HEAD",
                       "--", "*.json", "*.jsonl")
            if out.returncode == 0:
                return [p for p in out.stdout.splitlines() if p]
    return []


def _files() -> list[str]:
    return sorted(set(SWEPT) | set(_changed_against_base()))


def _parse_errors(rel: str) -> list[str]:
    text = (REPO_ROOT / rel).read_text(encoding="utf-8")
    if rel.endswith(".json"):
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            return [f"line {exc.lineno}"]
        return []
    errors = []
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"line {n}")
    return errors


@pytest.mark.parametrize("rel", _files())
def test_changed_json_file_parses(rel):
    path = REPO_ROOT / rel
    if not path.exists():
        pytest.skip("file removed from the public tree")
    errors = _parse_errors(rel)
    # Line numbers only: a failing line may carry the text the sweep was removing.
    assert not errors, f"{rel}: invalid JSON at {', '.join(errors[:10])}"


def test_swept_list_is_non_empty():
    assert len(SWEPT) == 13
    assert all((REPO_ROOT / p).exists() for p in SWEPT)
