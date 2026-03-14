"""
start_stage.py — Stage entry orchestrator (P2, WRK-1028)

Reads a stage YAML contract and either:
  task_agent    → writes stage-N-prompt.md (human/orchestrator dispatches via work.sh)
  human_interactive → emits checklist to stdout; checks for checkpoint
  chained_agent → writes combined prompt for all chained stages

Usage:
  uv run --no-project python scripts/work-queue/start_stage.py WRK-NNN N
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # optional — falls back to simple parsing
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


# ── Stage micro-skill loader ─────────────────────────────────────────────────

def _load_stage_micro_skill(stage: int, repo_root: str) -> str:
    """Load per-stage micro-skill file content.

    Returns file content on success, a warning string if not found, raises
    RuntimeError if multiple files match (prevents nondeterministic loading).
    """
    import glob as _glob
    pattern = os.path.join(
        repo_root, ".claude", "skills", "workspace-hub", "stages",
        f"stage-{stage:02d}-*.md",
    )
    matches = sorted(_glob.glob(pattern))
    if len(matches) == 0:
        return f"[stage micro-skill not found: stage-{stage:02d}-*.md]"
    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple stage micro-skill files matched for stage {stage}: {matches}"
        )
    return Path(matches[0]).read_text(encoding="utf-8")


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
    repo_root: Optional[str] = None,
) -> str:
    """
    Build and write stage-N-prompt.md. Returns the output file path.
    Works for both task_agent and chained_agent invocations.
    """
    if assets_root is None:
        assets_root = output_dir
    if repo_root is None:
        repo_root = os.environ.get("WORKSPACE_HUB", str(Path(__file__).parent.parent.parent))

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

    # Inject stage micro-skill so dispatched agents have rules in scope
    micro_skill = _load_stage_micro_skill(stage, repo_root)
    lines += ["", "## Stage Micro-Skill (rules for this stage)", "```", micro_skill, "```"]

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


# ── checkpoint resume block ───────────────────────────────────────────────────

def _read_checkpoint(assets_dir: str, wrk_id: str) -> dict:
    """Read checkpoint.yaml from assets_dir/checkpoint.yaml. Returns {} if absent."""
    cp_path = os.path.join(assets_dir, "checkpoint.yaml")
    if not os.path.exists(cp_path):
        return {}
    data: dict = {}
    try:
        with open(cp_path) as f:
            content = f.read()
        # Simple scalar parsing
        for line in content.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            if ":" in line and not line.startswith(" "):
                k, _, v = line.partition(":")
                v = v.strip().strip('"').strip("'")
                if v:
                    data[k.strip()] = v
        # Parse entry_reads list
        entry_reads: list[str] = []
        in_list = False
        for line in content.splitlines():
            if line.startswith("entry_reads:"):
                in_list = True
                continue
            if in_list:
                stripped = line.strip()
                if stripped.startswith("- "):
                    entry_reads.append(stripped[2:].strip())
                elif stripped and not line.startswith(" "):
                    in_list = False
        if entry_reads:
            data["entry_reads"] = entry_reads
    except OSError:
        pass
    return data


def _print_checkpoint_resume(wrk_id: str, stage: int, output_dir: str) -> None:
    """
    Print resume block if checkpoint.yaml exists and stage matches.
    Informational only — never blocks if checkpoint is absent.
    """
    cp = _read_checkpoint(output_dir, wrk_id)
    if not cp:
        return

    cp_stage_raw = cp.get("stage") or cp.get("current_stage", "")
    try:
        cp_stage = int(cp_stage_raw)
    except (ValueError, TypeError):
        cp_stage = None

    if cp_stage is None or cp_stage != stage:
        return  # Checkpoint is for a different stage; skip

    stage_name = cp.get("stage_name", f"Stage {stage}")
    next_action = cp.get("next_action", "(not set)")
    context_raw = cp.get("context_summary", "(not set)")
    context_str = str(context_raw)[:200]
    entry_reads = cp.get("entry_reads", [])
    if isinstance(entry_reads, str):
        entry_reads = [entry_reads]

    border = "\u2550" * 55
    print(f"\n{border}")
    print(f"  {wrk_id}  Resume \u00b7 Stage {stage} \u2014 {stage_name}")
    print(f"  Last action: {next_action}")
    print(f"  Context: {context_str}")
    if entry_reads:
        print(f"  Entry reads:")
        for er in entry_reads:
            print(f"    \u2022 {er}")
    print(f"{border}\n")


# ── route_stage ───────────────────────────────────────────────────────────────

def route_stage(
    contract: dict,
    wrk_id: str,
    stage: int,
    output_dir: str,
    assets_root: Optional[str] = None,
    repo_root: Optional[str] = None,
) -> None:
    """
    Route stage based on invocation type. Prints to stdout.
    """
    from checkpoint_writer import print_stage_banner  # same package dir
    if repo_root is None:
        repo_root = os.environ.get("WORKSPACE_HUB", str(Path(__file__).parent.parent.parent))

    stage_name = contract.get("name", f"Stage {stage}")
    print_stage_banner(stage, stage_name, "START")

    # Print stage micro-skill for human operator (unconditional — all invocation types)
    micro_skill = _load_stage_micro_skill(stage, repo_root)
    print(f"\n--- Stage {stage} Micro-Skill ---\n{micro_skill}\n---\n")

    invocation = contract.get("invocation", "task_agent")

    if invocation == "task_agent":
        _print_checkpoint_resume(wrk_id, stage, output_dir)
        out = build_prompt(contract, wrk_id, stage, output_dir, assets_root, repo_root=repo_root)
        print(f"Prompt package ready: {out}")
        print("Run: scripts/agents/work.sh with the prompt package above.")

    elif invocation == "human_interactive":
        # Auto-load checkpoint if present and stage matches
        _print_checkpoint_resume(wrk_id, stage, output_dir)
        print("Checklist:")
        for i, artifact in enumerate(contract.get("exit_artifacts", []), 1):
            print(f"  {i}. Produce: {artifact}")
        if contract.get("human_gate"):
            print(f"\n  GATE: Verify blocking_condition before advancing:")
            print(f"    {contract.get('blocking_condition', 'check gate artifact')}")

    elif invocation == "chained_agent":
        _print_checkpoint_resume(wrk_id, stage, output_dir)
        chained = contract.get("chained_stages", [stage])
        extra_contracts = []
        for cs in chained:
            if cs == stage:
                continue
            cs_glob = os.path.join(
                repo_root, "scripts", "work-queue", "stages", f"stage-{cs:02d}-*.yaml"
            )
            import glob as _glob2
            cs_matches = sorted(_glob2.glob(cs_glob))
            if cs_matches:
                extra_contracts.append(_load_yaml(cs_matches[0]))
        out = build_prompt(
            contract, wrk_id, stage, output_dir, assets_root,
            extra_contracts=extra_contracts or None, repo_root=repo_root,
        )
        print(f"Chained prompt package ready: {out}")
        print(f"Covers stages: {chained}")
        print("Single Task agent handles all chained stages; exits after all complete.")

    else:
        print(f"Unknown invocation type: {invocation}", file=sys.stderr)
        sys.exit(1)


# ── lifecycle HTML helper ─────────────────────────────────────────────────────

def _regenerate_lifecycle_html(wrk_id: str, repo_root: str) -> None:
    """Regenerate lifecycle + plan HTML as a standard stage-start action."""
    script = os.path.join(repo_root, "scripts", "work-queue", "generate-html-review.py")
    if not os.path.exists(script):
        return
    for mode in ("--lifecycle", "--plan"):
        label = "Lifecycle" if mode == "--lifecycle" else "Plan"
        result = subprocess.run(
            ["uv", "run", "--no-project", "python", script, wrk_id, mode],
            capture_output=True, text=True, cwd=repo_root,
        )
        if result.returncode == 0:
            print(f"✔ {label} HTML updated ({wrk_id})")
        else:
            print(f"⚠ {label} HTML update failed: {result.stderr.strip()[:120]}", file=sys.stderr)


# ── auto-open HTML for human-gate stages ─────────────────────────────────────

_HUMAN_GATE_STAGE_MAP = {
    5: "plan_draft",
    7: "plan_final",
    17: "close_review",
}


def _auto_open_html_for_human_gates(wrk_id: str, stage: int, repo_root: str) -> None:
    """Open lifecycle + plan HTML in browser at human-gate stages (5, 7, 17).

    Skips if the stage is not a human gate, if evidence shows the stage was
    already opened, or if the HTML files do not exist.
    """
    gate_label = _HUMAN_GATE_STAGE_MAP.get(stage)
    if gate_label is None:
        return

    assets_dir = os.path.join(
        repo_root, ".claude", "work-queue", "assets", wrk_id,
    )
    evidence_path = os.path.join(assets_dir, "evidence", "user-review-browser-open.yaml")

    # Double-open prevention: skip if this stage already has an event
    if os.path.exists(evidence_path):
        try:
            raw = Path(evidence_path).read_text(encoding="utf-8")
            if f"stage: {gate_label}" in raw:
                return
        except OSError:
            pass

    browser_script = os.path.join(
        repo_root, "scripts", "work-queue", "log-user-review-browser-open.sh",
    )
    if not os.path.exists(browser_script):
        print(f"⚠ Browser-open script not found: {browser_script}", file=sys.stderr)
        return

    html_files = [
        os.path.join(assets_dir, f"{wrk_id}-lifecycle.html"),
        os.path.join(assets_dir, f"{wrk_id}-plan.html"),
    ]

    for html_path in html_files:
        if not os.path.exists(html_path):
            print(f"⚠ HTML not found, skipping browser open: {html_path}", file=sys.stderr)
            continue
        subprocess.run(
            ["bash", browser_script, wrk_id, "--stage", gate_label, "--html", html_path],
            capture_output=True, text=True, cwd=repo_root,
        )


# ── Stage 1 guard helpers ─────────────────────────────────────────────────────

def _maybe_purge_stale_lock(lock_path: Path) -> None:
    """Auto-purge session-lock.yaml when PID is dead and age > 2h."""
    import datetime
    if not lock_path.exists():
        return
    try:
        if _HAS_YAML:
            import yaml as _yaml
            data = _yaml.safe_load(lock_path.read_text()) or {}
        else:
            data = _load_yaml(str(lock_path))
    except Exception:
        return
    pid = data.get("session_pid")
    locked_at_str = data.get("locked_at", "")
    try:
        locked_at = datetime.datetime.fromisoformat(str(locked_at_str).rstrip("Z"))
        age = (datetime.datetime.utcnow() - locked_at).total_seconds()
    except Exception:
        return
    if age <= 7200:
        return
    try:
        os.kill(int(pid), 0)
        return  # process still alive (same user)
    except PermissionError:
        return  # process alive, different owner — do not purge
    except (ProcessLookupError, TypeError, ValueError):
        pass  # process dead or invalid PID
    lock_path.unlink(missing_ok=True)
    print(
        f"  Auto-purged stale session-lock for PID {pid} (age {age / 3600:.1f}h).",
        file=sys.stderr,
    )


def _stage1_working_guard(wrk_id: str, queue_dir: str) -> None:
    """Exit 1 if wrk_id is not in working/ — prevents orphaned locks on pending items."""
    working_path = Path(queue_dir) / "working" / f"{wrk_id}.md"
    if not working_path.exists():
        print(
            f"✖ {wrk_id} is not in working/ — claim it before starting stage 1:\n"
            f"  bash scripts/work-queue/claim-item.sh {wrk_id}",
            file=sys.stderr,
        )
        sys.exit(1)


# ── stage-evidence updater ────────────────────────────────────────────────────

def _update_stage_ev(wrk_id: str, stage: int, status: str, repo_root: str) -> None:
    """Call update-stage-evidence.py to mark a stage status (in_progress/done)."""
    script = os.path.join(repo_root, "scripts", "work-queue", "update-stage-evidence.py")
    if not os.path.exists(script):
        return
    subprocess.run(
        ["uv", "run", "--no-project", "python", script, wrk_id,
         "--order", str(stage), "--status", status],
        capture_output=True, text=True, cwd=repo_root,
    )


# ── Stage 1 pending-or-working guard ─────────────────────────────────────────

def _stage1_pending_or_working_guard(wrk_id: str, queue_dir: str) -> None:
    """Exit 1 if wrk_id is in neither pending/ nor working/."""
    working = Path(queue_dir) / "working" / f"{wrk_id}.md"
    pending = Path(queue_dir) / "pending" / f"{wrk_id}.md"
    if not working.exists() and not pending.exists():
        print(
            f"\u2716 {wrk_id} not found in pending/ or working/",
            file=sys.stderr,
        )
        sys.exit(1)


# ── Stage progression guard ──────────────────────────────────────────────────

def _stage_progression_guard(wrk_id: str, stage: int, repo_root: str) -> None:
    """Verify previous stage evidence exists before allowing entry."""
    if stage <= 1:
        return
    prev_stage = stage - 1
    assets_dir = Path(repo_root) / ".claude" / "work-queue" / "assets" / wrk_id
    ev_path = assets_dir / "evidence" / "stage-evidence.yaml"
    if not ev_path.exists():
        return
    if _HAS_YAML:
        data = yaml.safe_load(ev_path.read_text(encoding="utf-8")) or {}
    else:
        data = _load_yaml(str(ev_path))
    for entry in data.get("stages", []):
        order = entry.get("order", entry.get("stage"))
        try:
            order = int(order)
        except (TypeError, ValueError):
            continue
        if order == prev_stage:
            status = str(entry.get("status", "")).lower()
            if status not in ("done", "n/a"):
                print(
                    f"\u26a0 Stage {prev_stage} is '{status}' \u2014 "
                    f"complete it before stage {stage}",
                    file=sys.stderr,
                )
                sys.exit(1)
            return
    # Previous stage not in evidence — allow (backcompat)


# ── CLI entrypoint ────────────────────────────────────────────────────────────

def _main() -> None:
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
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
    matches = sorted(_glob.glob(contract_glob))
    if not matches:
        print(f"No contract found: {contract_glob}", file=sys.stderr)
        sys.exit(1)

    contract = _load_yaml(matches[0])
    assets_root = os.path.join(repo_root, ".claude", "work-queue", "assets")
    output_dir = os.path.join(assets_root, wrk_id)

    # Detect already-archived items (stale checkpoint left behind)
    queue_dir = os.path.join(repo_root, ".claude", "work-queue")
    in_active = any(
        os.path.exists(os.path.join(queue_dir, d, f"{wrk_id}.md"))
        for d in ("pending", "working", "blocked", "done")
    )
    if not in_active:
        import glob as _ag
        archived = _ag.glob(os.path.join(queue_dir, "archive", "*", f"{wrk_id}.md"))
        if archived:
            print(
                f"✔ {wrk_id} is already archived — nothing to resume.",
                file=sys.stderr,
            )
            # Clean up stale checkpoint if present
            stale_cp = os.path.join(output_dir, "checkpoint.yaml")
            if os.path.exists(stale_cp):
                os.remove(stale_cp)
                print(f"  Removed stale checkpoint for {wrk_id}.", file=sys.stderr)
            sys.exit(0)

    # Stage guard: stage 1 accepts pending/ or working/; stages >=9 require working/
    if stage == 1:
        _maybe_purge_stale_lock(Path(output_dir) / "evidence" / "session-lock.yaml")
        _stage1_pending_or_working_guard(wrk_id, queue_dir)
    elif stage >= 9:
        _stage1_working_guard(wrk_id, queue_dir)

    # Stage progression guard: previous stage must be done before entry
    _stage_progression_guard(wrk_id, stage, repo_root)

    # Stage 1: write session-lock.yaml + active-wrk pre-validation
    if stage == 1:
        import datetime
        import socket
        workspace_root_path = Path(repo_root)
        ev_dir = Path(output_dir) / "evidence"
        ev_dir.mkdir(parents=True, exist_ok=True)

        # P4: warn if another WRK is still active
        active_wrk_path = workspace_root_path / ".claude" / "state" / "active-wrk"
        if active_wrk_path.exists():
            current = active_wrk_path.read_text().strip()
            if current and current != wrk_id:
                working_dir = workspace_root_path / ".claude" / "work-queue" / "working"
                if (working_dir / f"{current}.md").exists():
                    print(
                        f"⚠ Warning: active-wrk={current} is still in working/. "
                        f"Starting {wrk_id} anyway — verify no collision.",
                        flush=True,
                    )

        lock_path = ev_dir / "session-lock.yaml"
        lock_path.write_text(
            f"wrk_id: {wrk_id}\n"
            f"session_pid: {os.getpid()}\n"
            f"hostname: {socket.gethostname()}\n"
            f"locked_at: \"{datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}\"\n"
            f"status: in_progress\n"
        )

    route_stage(contract, wrk_id, stage, output_dir, assets_root, repo_root=repo_root)

    # Mark current stage as in_progress in stage-evidence
    _update_stage_ev(wrk_id, stage, "in_progress", repo_root)

    # Auto-regenerate lifecycle HTML so user always sees current state
    _regenerate_lifecycle_html(wrk_id, repo_root)

    # Auto-open HTML in browser at human-gate stages
    _auto_open_html_for_human_gates(wrk_id, stage, repo_root)


if __name__ == "__main__":
    _main()
