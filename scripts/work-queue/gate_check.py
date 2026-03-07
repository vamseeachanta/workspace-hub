"""
gate_check.py — Supplemental PreToolUse gate enforcer (P1, WRK-1028)

Canonical gate authority: verify-gate-evidence.py + stage5-gate-config.yaml
This script adds a convenience block at Write tool calls only.

Bash bypass limitation: agents using Bash (echo/sed/cat) bypass this hook.
Primary enforcement remains verify-gate-evidence.py.

Gates:
  5→6  : block evidence writes until evidence/user-review-plan-draft.yaml decision=approved
  7→8  : block activation writes until evidence/plan-final-review.yaml has all 3 required fields
  17→18: block done/WRK-NNN.md writes until evidence/user-review-close.yaml decision=approved

Usage as PreToolUse hook (stdin = JSON tool-use event):
  uv run --no-project python scripts/work-queue/gate_check.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional


# ── gate predicates ─────────────────────────────────────────────────────────

def _read_field(yaml_path: str, field: str) -> Optional[str]:
    """Read a simple 'field: value' line from a YAML file without a YAML parser."""
    try:
        with open(yaml_path) as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith(field + ":"):
                    val = stripped[len(field) + 1:].strip()
                    return val.strip('"').strip("'")
    except OSError:
        pass
    return None


def _gate5_ok(wrk_id: str, assets_root: str) -> bool:
    """True if user-review-plan-draft.yaml has decision: approved."""
    gate_file = os.path.join(assets_root, wrk_id, "evidence", "user-review-plan-draft.yaml")
    return _read_field(gate_file, "decision") == "approved"


def _gate7_ok(wrk_id: str, assets_root: str) -> bool:
    """True if plan-final-review.yaml has confirmed_by + confirmed_at + decision: passed."""
    gate_file = os.path.join(assets_root, wrk_id, "evidence", "plan-final-review.yaml")
    return (
        _read_field(gate_file, "confirmed_by") is not None
        and _read_field(gate_file, "confirmed_at") is not None
        and _read_field(gate_file, "decision") == "passed"
    )


def _gate17_ok(wrk_id: str, assets_root: str) -> bool:
    """True if user-review-close.yaml has decision: approved."""
    gate_file = os.path.join(assets_root, wrk_id, "evidence", "user-review-close.yaml")
    return _read_field(gate_file, "decision") == "approved"


# ── path classifiers ─────────────────────────────────────────────────────────

def _is_gate5_target(file_path: str, wrk_id: str, assets_root: str) -> bool:
    """Gate 5 blocks writes to cross-review.yaml or execute artifacts."""
    evidence_dir = os.path.join(assets_root, wrk_id, "evidence")
    gated = {"cross-review.yaml", "execute.yaml"}
    return (
        os.path.dirname(os.path.abspath(file_path)) == os.path.abspath(evidence_dir)
        and os.path.basename(file_path) in gated
    )


def _is_gate7_target(file_path: str, wrk_id: str, assets_root: str) -> bool:
    """Gate 7 blocks writes to claim-evidence.yaml or activation.yaml."""
    evidence_dir = os.path.join(assets_root, wrk_id, "evidence")
    gated = {"claim-evidence.yaml", "activation.yaml"}
    return (
        os.path.dirname(os.path.abspath(file_path)) == os.path.abspath(evidence_dir)
        and os.path.basename(file_path) in gated
    )


def _is_gate17_target(file_path: str, wrk_id: str, queue_root: str) -> bool:
    """Gate 17 blocks writes to done/WRK-NNN.md."""
    done_dir = os.path.join(queue_root, ".claude", "work-queue", "done")
    abs_path = os.path.abspath(file_path)
    return (
        os.path.dirname(abs_path) == os.path.abspath(done_dir)
        and os.path.basename(abs_path) == f"{wrk_id}.md"
    )


# ── public API ───────────────────────────────────────────────────────────────

def check_gate(
    tool_name: str,
    file_path: str,
    wrk_id: Optional[str],
    assets_root: str,
    queue_root: Optional[str] = None,
) -> dict:
    """
    Return {blocked: bool, reason: str}.

    Parameters
    ----------
    tool_name   : Claude tool being called (only 'Write' is ever blocked)
    file_path   : absolute or relative path being written
    wrk_id      : active WRK ID (e.g. "WRK-1028"), or None if not in a WRK session
    assets_root : path to .claude/work-queue/assets/ directory
    queue_root  : repo root (for done/ path resolution); defaults to assets_root/../..
    """
    # Only Write tool can be blocked
    if tool_name != "Write":
        return {"blocked": False, "reason": ""}

    # No active WRK — never block
    if not wrk_id:
        return {"blocked": False, "reason": ""}

    # Normalise queue_root
    if queue_root is None:
        queue_root = str(Path(assets_root).parent.parent.parent)

    # Gate 5→6
    if _is_gate5_target(file_path, wrk_id, assets_root):
        if not _gate5_ok(wrk_id, assets_root):
            return {
                "blocked": True,
                "reason": (
                    f"Gate 5→6 BLOCKED: {wrk_id}/evidence/user-review-plan-draft.yaml "
                    "must have 'decision: approved' before writing cross-review artifacts. "
                    "Complete Stage 5 human review first."
                ),
            }

    # Gate 7→8
    if _is_gate7_target(file_path, wrk_id, assets_root):
        if not _gate7_ok(wrk_id, assets_root):
            return {
                "blocked": True,
                "reason": (
                    f"Gate 7→8 BLOCKED: {wrk_id}/evidence/plan-final-review.yaml "
                    "must have confirmed_by, confirmed_at, and 'decision: passed' "
                    "(verify-gate-evidence.py G-07). Complete Stage 7 final review first."
                ),
            }

    # Gate 17→18
    if _is_gate17_target(file_path, wrk_id, queue_root):
        if not _gate17_ok(wrk_id, assets_root):
            return {
                "blocked": True,
                "reason": (
                    f"Gate 17→18 BLOCKED: {wrk_id}/evidence/user-review-close.yaml "
                    "must have 'decision: approved' before writing done/{wrk_id}.md. "
                    "Complete Stage 17 implementation review first."
                ),
            }

    return {"blocked": False, "reason": ""}


# ── hook entrypoint (stdin = Claude PreToolUse JSON) ─────────────────────────

def _hook_main() -> None:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # unparseable input → allow

    tool_name = event.get("tool_name", "")
    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path") or tool_input.get("path", "")

    if not file_path:
        sys.exit(0)

    # Read active WRK from state file
    repo_root = os.environ.get(
        "WORKSPACE_HUB",
        str(Path(__file__).parent.parent.parent),
    )
    active_wrk_file = os.path.join(repo_root, ".claude", "state", "active-wrk")
    wrk_id = None
    try:
        wrk_id = Path(active_wrk_file).read_text().strip() or None
    except OSError:
        pass

    assets_root = os.path.join(repo_root, ".claude", "work-queue", "assets")
    result = check_gate(
        tool_name=tool_name,
        file_path=file_path,
        wrk_id=wrk_id,
        assets_root=assets_root,
        queue_root=repo_root,
    )

    if result["blocked"]:
        # Claude hook protocol: print reason and exit non-zero to block
        print(result["reason"], file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    _hook_main()
