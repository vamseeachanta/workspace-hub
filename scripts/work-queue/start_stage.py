"""
start_stage.py — Stage entry orchestrator (P2, WRK-1028)

Reads a stage YAML contract and either:
  task_agent    → writes stage-N-prompt.md (human/orchestrator dispatches via work.sh)
  human_session → emits checklist to stdout; checks for checkpoint
  chained_agent → writes combined prompt for all chained stages

Usage:
  uv run --no-project python scripts/work-queue/start_stage.py WRK-NNN N
"""

from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # optional — falls back to simple parsing
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


# ── YAML loader (no-dep fallback) ────────────────────────────────────────────

def _load_yaml(path: str) -> dict:
    if _HAS_YAML:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    # Minimal field parser for simple scalar+list YAML
    result: dict = {}
    with open(path) as f:
        content = f.read()
    for line in content.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            val = val.strip().strip('"').strip("'")
            result[key.strip()] = val
    return result


# ── section-selector ─────────────────────────────────────────────────────────

def _extract_sections(html_path: str, selector: str) -> str:
    """
    Extract stage sections from lifecycle HTML using selector like 's4-s6'.
    Returns extracted text, or full file content if extraction fails.
    """
    try:
        import re
        parts = selector.split("-")
        if len(parts) != 2:
            return Path(html_path).read_text()
        start_id = parts[0]  # e.g. 's4'
        end_id = parts[1]    # e.g. 's6'
        content = Path(html_path).read_text()
        pattern = rf'(<section[^>]+id="{start_id}".*?</section>.*?<section[^>]+id="{end_id}".*?</section>)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1)
    except Exception:
        pass
    return Path(html_path).read_text()


def _resolve_entry_read(entry: str, wrk_id: str, assets_root: str) -> str:
    """Resolve an entry_reads path, applying section-selector if present."""
    selector = None
    path = entry

    # Check for section-selector suffix, e.g. WRK-NNN-lifecycle.html#s4-s6
    if "#" in entry:
        path, selector = entry.split("#", 1)

    # Resolve relative to assets root
    if not os.path.isabs(path):
        resolved = os.path.join(assets_root, wrk_id, path)
        if not os.path.exists(resolved):
            resolved = path  # fall through to original path
        path = resolved

    try:
        if selector:
            return _extract_sections(path, selector)
        return Path(path).read_text()
    except OSError:
        return f"[entry_reads: {entry} — file not found]"


# ── prompt builder ────────────────────────────────────────────────────────────

def build_prompt(
    contract: dict,
    wrk_id: str,
    stage: int,
    output_dir: str,
    assets_root: Optional[str] = None,
    extra_contracts: Optional[list[dict]] = None,
) -> str:
    """
    Build and write stage-N-prompt.md. Returns the output file path.
    Works for both task_agent and chained_agent invocations.
    """
    if assets_root is None:
        assets_root = output_dir

    lines = [
        f"# Stage {stage} Prompt Package — {wrk_id}",
        f"## Stage: {contract.get('name', f'Stage {stage}')}",
        f"**Invocation:** {contract.get('invocation', 'task_agent')}",
        f"**Weight:** {contract.get('weight', 'medium')}",
        f"**Context budget:** {contract.get('context_budget_kb', 8)} KB",
        "",
        "## Exit artifacts (must exist before calling exit-stage.sh)",
    ]
    for artifact in contract.get("exit_artifacts", []):
        lines.append(f"  - `{artifact}`")

    lines += ["", "## Entry reads"]
    for entry in contract.get("entry_reads", []):
        content = _resolve_entry_read(entry, wrk_id, assets_root)
        lines.append(f"\n### {entry}\n```\n{content[:2000]}\n```")

    # For chained_agent, include all chained stage contracts
    if extra_contracts:
        lines += ["", "## Chained stages (complete in sequence)"]
        for i, ec in enumerate(extra_contracts, 1):
            lines += [
                f"\n### Chained stage {i}: {ec.get('name', '')}",
                f"Exit artifacts: {ec.get('exit_artifacts', [])}",
            ]

    if contract.get("blocking_condition"):
        lines += ["", f"**Blocking condition:** {contract['blocking_condition']}"]

    prompt = "\n".join(lines)
    out_path = os.path.join(output_dir, f"stage-{stage}-prompt.md")
    Path(out_path).write_text(prompt)
    return out_path


# ── route_stage ───────────────────────────────────────────────────────────────

def route_stage(
    contract: dict,
    wrk_id: str,
    stage: int,
    output_dir: str,
    assets_root: Optional[str] = None,
) -> None:
    """
    Route stage based on invocation type. Prints to stdout.
    """
    invocation = contract.get("invocation", "task_agent")

    if invocation == "task_agent":
        out = build_prompt(contract, wrk_id, stage, output_dir, assets_root)
        print(f"Prompt package ready: {out}")
        print("Run: scripts/agents/work.sh with the prompt package above.")

    elif invocation == "human_session":
        print(f"\n=== Stage {stage}: {contract.get('name')} ===")
        print("Checklist:")
        for i, artifact in enumerate(contract.get("exit_artifacts", []), 1):
            print(f"  {i}. Produce: {artifact}")
        if contract.get("human_gate"):
            print(f"\n  GATE: Verify blocking_condition before advancing:")
            print(f"    {contract.get('blocking_condition', 'check gate artifact')}")
        # Check for existing checkpoint
        checkpoint = os.path.join(
            output_dir, "..", "checkpoint.yaml"
        )
        if os.path.exists(checkpoint):
            print(f"\n  Checkpoint found. Run /wrk-resume {wrk_id} to reload context.")

    elif invocation == "chained_agent":
        chained = contract.get("chained_stages", [stage])
        out = build_prompt(contract, wrk_id, stage, output_dir, assets_root)
        print(f"Chained prompt package ready: {out}")
        print(f"Covers stages: {chained}")
        print("Single Task agent handles all chained stages; exits after all complete.")

    else:
        print(f"Unknown invocation type: {invocation}", file=sys.stderr)
        sys.exit(1)


# ── CLI entrypoint ────────────────────────────────────────────────────────────

def _main() -> None:
    if len(sys.argv) < 3:
        print("Usage: start_stage.py WRK-NNN N", file=sys.stderr)
        sys.exit(1)

    wrk_id = sys.argv[1]
    stage = int(sys.argv[2])

    repo_root = os.environ.get(
        "WORKSPACE_HUB",
        str(Path(__file__).parent.parent.parent),
    )
    contract_glob = os.path.join(
        repo_root, "scripts", "work-queue", "stages", f"stage-{stage:02d}-*.yaml"
    )
    import glob as _glob
    matches = _glob.glob(contract_glob)
    if not matches:
        print(f"No contract found: {contract_glob}", file=sys.stderr)
        sys.exit(1)

    contract = _load_yaml(matches[0])
    assets_root = os.path.join(repo_root, ".claude", "work-queue", "assets")
    output_dir = os.path.join(assets_root, wrk_id)

    route_stage(contract, wrk_id, stage, output_dir, assets_root)


if __name__ == "__main__":
    _main()
