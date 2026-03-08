"""
exit_stage.py — Stage exit validator (P2, WRK-1028)

Validates that all exit artifacts exist and any human gate condition is met,
then updates lifecycle HTML and stage-state.yaml.

Usage:
  uv run --no-project python scripts/work-queue/exit_stage.py WRK-NNN N
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional


def _read_field(yaml_path: str, field: str) -> Optional[str]:
    """Read a simple 'field: value' line from YAML without a parser."""
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


def check_human_gate(
    gate_file: str,
    stage_dir: str,
    gate_field: str = "decision",
    gate_value: str = "approved",
) -> bool:
    """Return True if gate condition is met."""
    full_path = os.path.join(stage_dir, gate_file)
    val = _read_field(full_path, gate_field)
    return val == gate_value


def _deterministic_stage_check(stage: int, stage_dir: str, repo_root: str) -> None:
    """D-item deterministic gate enforcement — delegates to stage_exit_checks."""
    # Ensure scripts/work-queue is importable
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    if _script_dir not in sys.path:
        sys.path.insert(0, _script_dir)

    try:
        from stage_dispatch import run_d_item_checks  # type: ignore[import]
    except ImportError as exc:
        print(f"WARN: D-item checks unavailable ({exc})", file=sys.stderr)
        return

    run_d_item_checks(stage, Path(stage_dir), repo_root)


def _heavy_stage_check(stage: int, stage_dir: str, repo_root: str) -> None:
    """
    P4 heavy-stage enforcement.

    Stage 10 (Work Execution): execute.yaml must exist (verified by artifact check).
                               Emits warning if no test count signal found.
    Stage 12 (TDD / Eval):    ac-test-matrix.md must have ≥3 PASS entries, zero FAIL.
    """
    if stage == 10:
        execute_yaml = os.path.join(stage_dir, "evidence", "execute.yaml")
        if os.path.exists(execute_yaml):
            test_count = _read_field(execute_yaml, "test_count")
            test_files_present = False
            with open(execute_yaml) as f:
                for line in f:
                    if "test_files" in line or "test_count" in line:
                        test_files_present = True
                        break
            if not test_files_present:
                print(
                    "STAGE 10 WARNING: execute.yaml has no test_count or test_files field. "
                    "TDD is mandatory — ensure tests were written before implementation.",
                    file=sys.stderr,
                )
        return

    if stage == 12:
        matrix_path = os.path.join(stage_dir, "ac-test-matrix.md")
        if not os.path.exists(matrix_path):
            # Will be caught by artifact check — skip here
            return
        pass_count = 0
        fail_count = 0
        with open(matrix_path) as f:
            for line in f:
                # Only count table rows (lines with | pipe characters)
                if "|" not in line:
                    continue
                upper = line.upper()
                if "| PASS" in upper or "PASS |" in upper or "✓" in line:
                    pass_count += 1
                if "| FAIL" in upper or "FAIL |" in upper or "✗" in line:
                    fail_count += 1
        if fail_count > 0:
            print(
                f"STAGE 12 BLOCKED: ac-test-matrix.md has {fail_count} FAIL entries. "
                "All ACs must pass before Stage 12 exit.",
                file=sys.stderr,
            )
            sys.exit(1)
        if pass_count < 3:
            print(
                f"STAGE 12 BLOCKED: ac-test-matrix.md has only {pass_count} PASS entries "
                "(minimum 3 required). Expand test coverage.",
                file=sys.stderr,
            )
            sys.exit(1)


def validate_exit(
    exit_artifacts: list[str],
    stage_dir: str,
    human_gate: bool = False,
    gate_field: str = "decision",
    gate_value: str = "approved",
    gate_file: Optional[str] = None,
    stage: Optional[int] = None,
    repo_root: Optional[str] = None,
) -> bool:
    """
    Validate stage exit conditions.

    Raises SystemExit(1) if:
      - any exit artifact is missing
      - human_gate=True and gate condition not met

    Returns True on success.
    """
    # Normalize artifact paths: strip "assets/WRK-NNN/" or "assets/<wrk_id>/" prefix
    # since stage_dir already points to assets/<wrk_id>; also substitute WRK-NNN token.
    _wrk_id = os.path.basename(stage_dir)

    def _normalize(path: str) -> str:
        p = path.replace("WRK-NNN", _wrk_id)
        for prefix in (f"assets/WRK-NNN/", f"assets/{_wrk_id}/"):
            if p.startswith(prefix):
                return p[len(prefix):]
        # Handle done/ paths (Stage 19 exit artifact is done/WRK-NNN.md)
        return p

    # Check all exit artifacts exist
    missing = []
    for artifact in exit_artifacts:
        rel = _normalize(artifact)
        if rel.startswith(("done/", "pending/", "working/", "archive/")):
            # queue-relative paths — not inside assets/WRK-NNN/
            queue_root = str(Path(stage_dir).parent.parent)
            # archive/ may have YYYY-MM subdir — search recursively
            if rel.startswith("archive/"):
                import glob as _glob
                fname = os.path.basename(rel)
                matches = _glob.glob(os.path.join(queue_root, "archive", "**", fname),
                                     recursive=True)
                full_path = matches[0] if matches else os.path.join(queue_root, rel)
            else:
                full_path = os.path.join(queue_root, rel)
        else:
            full_path = os.path.join(stage_dir, rel)
        if not os.path.exists(full_path):
            missing.append(artifact)

    if missing:
        for m in missing:
            print(f"EXIT BLOCKED: missing artifact: {m}", file=sys.stderr)
        sys.exit(1)

    # D-item deterministic gate enforcement (WRK-1044)
    if stage is not None and repo_root is not None:
        _deterministic_stage_check(stage, stage_dir, repo_root)

    # P4: heavy-stage enforcement for stages 10 and 12
    if stage is not None and repo_root is not None:
        _heavy_stage_check(stage, stage_dir, repo_root)

    # Check human gate condition
    if human_gate and gate_file:
        gate_rel = _normalize(gate_file)
        if not check_human_gate(gate_rel, stage_dir, gate_field, gate_value):
            full_path = os.path.join(stage_dir, gate_rel)
            actual = _read_field(full_path, gate_field) or "(field absent)"
            print(
                f"GATE BLOCKED: {gate_file} must have '{gate_field}: {gate_value}' "
                f"(found: '{gate_field}: {actual}')",
                file=sys.stderr,
            )
            sys.exit(1)

    return True


# ── Checkpoint schema validation (delegated to checkpoint_writer.py) ──────────

def _validate_checkpoint(checkpoint_path: str) -> None:
    """Non-blocking checkpoint.yaml schema validation. Delegated to checkpoint_writer."""
    _write_cp, _print_gate, _log_complete = _load_checkpoint_writer()
    # Import validate function separately
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    if _script_dir not in sys.path:
        sys.path.insert(0, _script_dir)
    from checkpoint_writer import validate_checkpoint  # type: ignore[import]
    validate_checkpoint(checkpoint_path)


# ── checkpoint writer (delegated to checkpoint_writer.py) ─────────────────────

def _load_checkpoint_writer():
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    if _script_dir not in sys.path:
        sys.path.insert(0, _script_dir)
    from checkpoint_writer import write_checkpoint, print_stage_gate, log_stage_complete  # type: ignore[import]
    return write_checkpoint, print_stage_gate, log_stage_complete


# ── lifecycle HTML helper ─────────────────────────────────────────────────────

def _regenerate_lifecycle_html(wrk_id: str, repo_root: str) -> None:
    """Regenerate lifecycle HTML after stage exit so state is always current."""
    import subprocess
    script = os.path.join(repo_root, "scripts", "work-queue", "generate-html-review.py")
    if not os.path.exists(script):
        return
    result = subprocess.run(
        ["uv", "run", "--no-project", "python", script, wrk_id, "--lifecycle"],
        capture_output=True, text=True, cwd=repo_root,
    )
    if result.returncode == 0:
        print(f"✔ Lifecycle HTML updated ({wrk_id})")
    else:
        print(f"⚠ Lifecycle HTML update failed: {result.stderr.strip()[:120]}", file=sys.stderr)


# ── CLI entrypoint ────────────────────────────────────────────────────────────

def _main() -> None:
    if len(sys.argv) < 3:
        print("Usage: exit_stage.py WRK-NNN N [--context-summary TEXT]", file=sys.stderr)
        sys.exit(1)

    wrk_id = sys.argv[1]
    stage = int(sys.argv[2])

    # Parse optional --context-summary arg
    context_summary: Optional[str] = None
    args = sys.argv[3:]
    i = 0
    while i < len(args):
        if args[i] == "--context-summary" and i + 1 < len(args):
            context_summary = args[i + 1]
            i += 2
        else:
            i += 1

    repo_root = os.environ.get(
        "WORKSPACE_HUB",
        str(Path(__file__).parent.parent.parent),
    )

    import glob as _glob
    contract_glob = os.path.join(
        repo_root, "scripts", "work-queue", "stages", f"stage-{stage:02d}-*.yaml"
    )
    matches = _glob.glob(contract_glob)
    if not matches:
        print(f"No contract found for stage {stage}", file=sys.stderr)
        sys.exit(1)

    # Minimal YAML field extraction
    contract: dict = {}
    with open(matches[0]) as f:
        for line in f:
            if ":" in line and not line.startswith(" "):
                k, _, v = line.partition(":")
                contract[k.strip()] = v.strip().strip('"').strip("'")

    assets_root = os.path.join(repo_root, ".claude", "work-queue", "assets")
    stage_dir = os.path.join(assets_root, wrk_id)

    # Parse exit_artifacts (simple list from YAML block)
    exit_artifacts = []
    in_list = False
    with open(matches[0]) as f:
        for line in f:
            if line.startswith("exit_artifacts:"):
                in_list = True
                continue
            if in_list:
                stripped = line.strip()
                if stripped.startswith("- "):
                    exit_artifacts.append(stripped[2:].strip())
                elif stripped and not stripped.startswith("#"):
                    in_list = False

    human_gate = contract.get("human_gate", "false").lower() == "true"
    gate_file = contract.get("gate_file", "")
    gate_field = contract.get("gate_field", "decision")
    gate_value = contract.get("gate_value", "approved")

    validate_exit(
        exit_artifacts=exit_artifacts,
        stage_dir=stage_dir,
        human_gate=human_gate,
        gate_field=gate_field,
        gate_value=gate_value,
        gate_file=gate_file or None,
        stage=stage,
        repo_root=repo_root,
    )

    print(f"Stage {stage} exit validated. All artifacts present.")
    if human_gate:
        print(f"GATE PASSED — Stage {stage + 1} unlocked.")

    # Regenerate lifecycle HTML to reflect this stage as done
    _regenerate_lifecycle_html(wrk_id, repo_root)

    # Write rich checkpoint and emit STAGE_GATE signal
    _write_cp, _print_gate, _log_complete = _load_checkpoint_writer()
    cp_info = _write_cp(wrk_id, stage, repo_root, context_summary)
    _print_gate(wrk_id, stage, cp_info)

    # Emit stage_complete log event (non-blocking)
    _log_complete(wrk_id, stage, repo_root)

    # Validate written checkpoint (non-blocking)
    checkpoint_path = os.path.join(assets_root, wrk_id, "checkpoint.yaml")
    _validate_checkpoint(checkpoint_path)


if __name__ == "__main__":
    _main()
