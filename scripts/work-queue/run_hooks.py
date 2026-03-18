"""
Generic hook runner for stage transitions.

Executes a list of hook dicts from stage YAML, respects gate type and timeout,
writes evidence to assets dir. Returns list of hard blockers.

Usage (programmatic):
    from run_hooks import run_hooks
    blockers = run_hooks(hooks, wrk_id, repo_root, phase, stage)

Usage (CLI):
    uv run --no-project python scripts/work-queue/run_hooks.py WRK-NNN 10 pre_exit
"""

import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import yaml


def run_hooks(hooks, wrk_id, repo_root, phase, stage,
              assets_dir=None, dry_run=False):
    """Execute hooks and return list of hard blockers.

    Args:
        hooks: list of hook dicts [{script, gate, timeout_s, description}]
               or None
        wrk_id: e.g. "WRK-1316"
        repo_root: workspace-hub root path
        phase: "pre_exit" or "pre_enter"
        stage: int stage number
        assets_dir: path to assets/WRK-NNN/ (for evidence writing)
        dry_run: if True, log what would run without executing

    Returns:
        list of blocker dicts (hard hooks that failed)
    """
    if not hooks:
        return []

    results = []
    blockers = []

    for hook in hooks:
        script = hook.get("script", "")
        gate = hook.get("gate", "hard")
        timeout_s = hook.get("timeout_s", 30)
        description = hook.get("description", script)

        # Substitute WRK-NNN token with actual WRK ID
        resolved_script = script.replace("WRK-NNN", wrk_id)

        if dry_run:
            results.append({
                "script": resolved_script,
                "description": description,
                "gate": gate,
                "dry_run": True,
                "passed": True,
            })
            continue

        # Execute the hook script
        start = time.monotonic()
        try:
            proc = subprocess.run(
                ["bash", resolved_script],
                capture_output=True,
                text=True,
                timeout=timeout_s,
                cwd=repo_root,
            )
            duration_s = round(time.monotonic() - start, 3)
            passed = proc.returncode == 0
            entry = {
                "script": resolved_script,
                "description": description,
                "gate": gate,
                "returncode": proc.returncode,
                "duration_s": duration_s,
                "passed": passed,
                "stdout": proc.stdout.strip()[:500] if proc.stdout else "",
                "stderr": proc.stderr.strip()[:500] if proc.stderr else "",
            }
        except subprocess.TimeoutExpired:
            duration_s = round(time.monotonic() - start, 3)
            entry = {
                "script": resolved_script,
                "description": description,
                "gate": gate,
                "returncode": -1,
                "duration_s": duration_s,
                "passed": False,
                "stderr": f"timeout after {timeout_s}s",
            }

        results.append(entry)

        if not entry["passed"] and gate == "hard":
            blockers.append(entry)

    # Write evidence if assets_dir provided
    if assets_dir and not dry_run:
        _write_evidence(results, phase, stage, wrk_id, assets_dir)

    return blockers


def _write_evidence(results, phase, stage, wrk_id, assets_dir):
    """Write hook execution evidence to YAML."""
    evidence_dir = os.path.join(assets_dir, "evidence")
    os.makedirs(evidence_dir, exist_ok=True)

    passed_count = sum(1 for r in results if r.get("passed"))
    hard_fail = sum(1 for r in results
                    if not r.get("passed") and r.get("gate") == "hard")
    soft_fail = sum(1 for r in results
                    if not r.get("passed") and r.get("gate") == "soft")

    evidence = {
        "phase": phase,
        "stage": stage,
        "wrk_id": wrk_id,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "hooks": results,
        "summary": {
            "total": len(results),
            "passed": passed_count,
            "failed_hard": hard_fail,
            "failed_soft": soft_fail,
            "blocked": hard_fail > 0,
        },
    }

    path = os.path.join(evidence_dir, f"hooks-{phase}-{stage}.yaml")
    with open(path, "w") as f:
        yaml.dump(evidence, f, default_flow_style=False, sort_keys=False)
