#!/usr/bin/env python3
"""
Session Governor — hard-stop checkpoint verification utility.

Loads governance-checkpoints.yaml and verifies which required gates
have been satisfied in the current session. Reports PASS/FAIL/WARN
per gate plus an overall session verdict.

Usage:
    uv run scripts/workflow/session_governor.py                          # check all gates
    uv run scripts/workflow/session_governor.py --passed plan-approval   # mark gates as passed
    uv run scripts/workflow/session_governor.py --list                   # list all checkpoints
"""

from __future__ import annotations

import argparse
import enum
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "scripts" / "workflow" / "governance-checkpoints.yaml"


# ── Data model ──────────────────────────────────────────────────────────


class GateStatus(enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"


@dataclass
class Checkpoint:
    id: str
    name: str
    stage: str
    type: str  # "hard-stop" or "auto-gate"
    description: str
    enforced: bool
    threshold: int | None = None


@dataclass
class CheckpointConfig:
    version: int
    checkpoints: list[Checkpoint] = field(default_factory=list)


@dataclass
class GateResult:
    checkpoint_id: str
    name: str
    status: GateStatus
    enforced: bool
    message: str


# ── Loading ─────────────────────────────────────────────────────────────


def load_checkpoints(data: dict) -> CheckpointConfig:
    """Parse a YAML-loaded dict into a CheckpointConfig."""
    checkpoints = []
    for cp_data in data.get("checkpoints", []):
        checkpoints.append(Checkpoint(
            id=cp_data["id"],
            name=cp_data["name"],
            stage=cp_data["stage"],
            type=cp_data["type"],
            description=cp_data["description"],
            enforced=cp_data.get("enforced", True),
            threshold=cp_data.get("threshold"),
        ))
    return CheckpointConfig(
        version=data.get("version", 1),
        checkpoints=checkpoints,
    )


def load_config_from_file(path: Path | None = None) -> CheckpointConfig:
    """Load checkpoint config from a YAML file."""
    path = path or DEFAULT_CONFIG
    with open(path) as f:
        data = yaml.safe_load(f)
    return load_checkpoints(data)


# ── Verification ────────────────────────────────────────────────────────


def verify_gates(
    config: CheckpointConfig,
    passed_gates: set[str],
) -> list[GateResult]:
    """Check each checkpoint against the set of passed gate IDs.

    Returns a GateResult per checkpoint:
      - PASS if the gate ID is in passed_gates
      - FAIL if enforced and missing
      - WARN if not enforced and missing
    """
    results: list[GateResult] = []
    for cp in config.checkpoints:
        if cp.id in passed_gates:
            status = GateStatus.PASS
            msg = "Gate satisfied."
        elif cp.enforced:
            status = GateStatus.FAIL
            msg = f"REQUIRED gate '{cp.name}' not satisfied — session blocked."
        else:
            status = GateStatus.WARN
            msg = f"Advisory gate '{cp.name}' not satisfied — non-blocking."

        results.append(GateResult(
            checkpoint_id=cp.id,
            name=cp.name,
            status=status,
            enforced=cp.enforced,
            message=msg,
        ))
    return results


def format_report(results: list[GateResult]) -> str:
    """Format gate results as a human-readable report."""
    lines: list[str] = []
    lines.append("# Session Governance Report")
    lines.append("")

    if not results:
        lines.append("No checkpoints configured.")
        return "\n".join(lines)

    lines.append("| Gate | Type | Status | Message |")
    lines.append("|------|------|--------|---------|")
    for r in results:
        status_icon = {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN"}[r.status.value]
        gate_type = "hard-stop" if r.enforced else "advisory"
        lines.append(f"| {r.name} | {gate_type} | {status_icon} | {r.message} |")

    lines.append("")
    fail_count = sum(1 for r in results if r.status == GateStatus.FAIL)
    warn_count = sum(1 for r in results if r.status == GateStatus.WARN)
    pass_count = sum(1 for r in results if r.status == GateStatus.PASS)

    if fail_count:
        lines.append(f"**VERDICT: BLOCKED** — {fail_count} enforced gate(s) not satisfied.")
    elif warn_count:
        lines.append(f"**VERDICT: PASS with warnings** — {warn_count} advisory gate(s) skipped.")
    else:
        lines.append(f"**VERDICT: PASS** — all {pass_count} gate(s) satisfied.")

    return "\n".join(lines)


def list_checkpoints(config: CheckpointConfig) -> str:
    """List all configured checkpoints."""
    lines = ["# Configured Checkpoints", ""]
    lines.append("| ID | Name | Stage | Type | Enforced |")
    lines.append("|----|------|-------|------|----------|")
    for cp in config.checkpoints:
        lines.append(
            f"| {cp.id} | {cp.name} | {cp.stage} | {cp.type} | {cp.enforced} |"
        )
    return "\n".join(lines)


# ── CLI ─────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Session governance checkpoint verifier")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to governance-checkpoints.yaml",
    )
    parser.add_argument(
        "--passed",
        nargs="*",
        default=[],
        help="Gate IDs that have been satisfied in this session",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_gates",
        help="List all configured checkpoints",
    )
    args = parser.parse_args()

    config = load_config_from_file(args.config)

    if args.list_gates:
        print(list_checkpoints(config))
        return 0

    results = verify_gates(config, set(args.passed))
    print(format_report(results))

    fail_count = sum(1 for r in results if r.status == GateStatus.FAIL)
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
