"""
checkpoint_writer.py — Auto-writes checkpoint.yaml and emits STAGE_GATE signal (WRK-1046).

Called by exit_stage.py after each successful stage exit.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def _load_next_contract(repo_root: str, next_stage: int) -> dict:
    """Load stage contract for next_stage. Returns scalars + lists."""
    import glob as _glob
    pattern = os.path.join(
        repo_root, "scripts", "work-queue", "stages", f"stage-{next_stage:02d}-*.yaml"
    )
    matches = _glob.glob(pattern)
    if not matches:
        return {}
    result: dict = {}
    current_key: Optional[str] = None
    list_items: list[str] = []
    with open(matches[0]) as f:
        for line in f:
            if line.startswith("  - "):
                if current_key:
                    list_items.append(line.strip()[2:])
                continue
            if current_key and list_items:
                result[current_key] = list_items
                list_items = []
                current_key = None
            if ":" in line and not line.startswith(" "):
                k, _, v = line.partition(":")
                key = k.strip()
                val = v.strip().strip('"').strip("'")
                if val:
                    result[key] = val
                else:
                    current_key = key
    if current_key and list_items:
        result[current_key] = list_items
    return result


def write_checkpoint(
    wrk_id: str,
    completed_stage: int,
    repo_root: str,
    context_summary: Optional[str] = None,
) -> dict:
    """
    Write checkpoint.yaml after stage exit.

    Schema aligns with checkpoint.sh: current_stage=N+1, checkpointed_at.
    Reads entry_reads, human_gate, chained_stages from the N+1 contract.
    Returns info dict for STAGE_GATE output.
    """
    from datetime import datetime, timezone

    assets_dir = os.path.join(repo_root, ".claude", "work-queue", "assets", wrk_id)
    cp_path = os.path.join(assets_dir, "checkpoint.yaml")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if completed_stage >= 20:
        lines = [
            f"wrk_id: {wrk_id}",
            "current_stage: complete",
            f"completed_stage: {completed_stage}",
            "next_action: WRK complete — archive if not done",
            f"context_summary: {context_summary or f'Stage {completed_stage} complete. WRK finished.'}",
            f"checkpointed_at: {now}",
        ]
        with open(cp_path, "w") as f:
            f.write("\n".join(lines) + "\n")
        return {"terminal": True}

    next_stage = completed_stage + 1
    nc = _load_next_contract(repo_root, next_stage)
    next_name = nc.get("name", f"Stage {next_stage}")
    next_human_gate = nc.get("human_gate", "false").lower() == "true"

    entry_reads: list[str] = nc.get("entry_reads", [])
    if isinstance(entry_reads, str):
        entry_reads = [entry_reads]
    entry_reads = [er.replace("WRK-NNN", wrk_id) for er in entry_reads]
    cp_rel = f".claude/work-queue/assets/{wrk_id}/checkpoint.yaml"
    if cp_rel not in entry_reads:
        entry_reads = [cp_rel] + entry_reads

    chained = nc.get("chained_stages")
    if isinstance(chained, str):
        chained = [chained]

    auto_summary = (
        context_summary
        or f"Stage {completed_stage} complete. Next: stage {next_stage} ({next_name})."
    )

    lines = [
        f"wrk_id: {wrk_id}",
        f"current_stage: {next_stage}",
        f"stage_name: {next_name}",
        f"completed_stage: {completed_stage}",
        f"next_action: Execute stage {next_stage}: {next_name}",
        f"context_summary: {auto_summary}",
        "entry_reads:",
    ] + [f"  - {er}" for er in entry_reads] + [
        f"checkpointed_at: {now}",
        f"human_gate: {'true' if next_human_gate else 'false'}",
    ]
    if chained:
        chained_str = "[" + ", ".join(str(c) for c in chained) + "]"
        lines.append(f"chained_stages: {chained_str}")

    with open(cp_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    return {
        "terminal": False,
        "next_stage": next_stage,
        "next_name": next_name,
        "human_gate": next_human_gate,
        "chained": chained,
    }


_STAGE_NAMES = {
    1: "Capture", 2: "Resource Intelligence", 3: "Triage",
    4: "Plan Draft", 5: "User Review Plan Draft", 6: "Cross-Review",
    7: "User Review Plan Final", 8: "Claim/Activation", 9: "Routing",
    10: "Work Execution", 11: "Artifact Generation", 12: "TDD/Eval",
    13: "Agent Cross-Review", 14: "Verify Gate Evidence",
    15: "Future Work", 16: "Resource Intel Update",
    17: "User Review Implementation", 18: "Reclaim", 19: "Close", 20: "Archive",
}


def print_stage_gate(wrk_id: str, completed_stage: int, cp_info: dict) -> None:
    """Print STAGE_GATE block for orchestrator to read."""
    if cp_info.get("terminal"):
        print(f"\nStage {completed_stage} complete. WRK finished — proceed to archive.")
        return
    next_stage = cp_info["next_stage"]
    next_name = cp_info["next_name"]
    human_gate = cp_info["human_gate"]
    action = "await_user_approval" if human_gate else "spawn_subagent"
    completed_name = _STAGE_NAMES.get(completed_stage, f"Stage {completed_stage}")
    w = 52

    def row(label: str, value: str) -> str:
        content = f"  {label:<16}{value}"
        return "║" + content + " " * max(w - len(content), 0) + "║"

    print("")
    print("╔" + "═" * w + "╗")
    print(row("STAGE_GATE", ""))
    print(row("wrk_id:", wrk_id))
    print(row("completed:", f"{completed_stage}  ({completed_name})"))
    print(row("next_stage:", f"{next_stage}  ({next_name})"))
    print(row("human_gate:", str(human_gate).lower()))
    print(row("action:", action))
    print("╚" + "═" * w + "╝")
    print("")


def validate_checkpoint(checkpoint_path: str) -> None:
    """
    Non-blocking checkpoint.yaml schema validation.
    Warns if required fields are missing; does NOT exit on failure.
    """
    import re

    if not os.path.exists(checkpoint_path):
        return

    missing: list[str] = []

    def _read(field: str) -> Optional[str]:
        try:
            with open(checkpoint_path) as f:
                for line in f:
                    if line.strip().startswith(field + ":"):
                        val = line.strip()[len(field) + 1:].strip()
                        return val.strip('"').strip("'")
        except OSError:
            pass
        return None

    if not _read("wrk_id"):
        missing.append("wrk_id")

    stage_val = _read("stage") or _read("current_stage")
    if stage_val is None:
        missing.append("stage")
    elif stage_val != "complete":
        try:
            s = int(stage_val)
            if not 1 <= s <= 20:
                missing.append("stage (out of range)")
        except ValueError:
            missing.append("stage (not an integer)")

    if not _read("next_action"):
        missing.append("next_action")

    ctx = _read("context_summary")
    if not ctx:
        try:
            content = open(checkpoint_path).read()
            has_list = any(
                line.strip().startswith("- ")
                for line in content.splitlines()
                if line.startswith("context_summary:") or (
                    "context_summary" in content and line.strip().startswith("- ")
                )
            )
            if not has_list:
                missing.append("context_summary")
        except OSError:
            missing.append("context_summary")

    updated = _read("updated_at") or _read("checkpointed_at")
    if not updated:
        missing.append("updated_at")
    elif "T" not in updated and not re.search(r"\d{4}-\d{2}-\d{2}.+\d{2}:\d{2}", updated):
        missing.append("updated_at (date-only; must include time)")

    if missing:
        import sys
        print(
            f"\n⚠ checkpoint.yaml missing fields: {missing}\n"
            "  next_action and context_summary required for /work run auto-resume",
            file=sys.stderr,
        )


def log_stage_complete(wrk_id: str, stage: int, repo_root: str) -> None:
    """Emit stage_complete log event via log-gate-event.sh (non-blocking)."""
    import subprocess
    script = os.path.join(repo_root, "scripts", "work-queue", "log-gate-event.sh")
    if not os.path.exists(script):
        return
    try:
        subprocess.run(
            ["bash", script, wrk_id, str(stage), "stage_complete", "claude",
             f"Stage {stage} complete"],
            capture_output=True, cwd=repo_root,
        )
    except Exception:
        pass
