"""generate_transition_table.py — Explicit FSM transition table from stage contracts.

ABOUTME: Reads the 20 stage-NN-*.yaml contracts and produces a machine-readable
transition table mapping {from_stage → to_stage} with guards, human gates, and
rollback targets. Enforces no-skip transitions.

WRK-1187 Enhancement 2.
"""

from __future__ import annotations

import glob
import os
from typing import Any


def _read_yaml_fields(path: str) -> dict[str, Any]:
    """Minimal YAML field extraction (no dependency on pyyaml)."""
    fields: dict[str, Any] = {}
    with open(path) as f:
        for line in f:
            if ":" in line and not line.startswith(" ") and not line.startswith("#"):
                k, _, v = line.partition(":")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if v.lower() == "true":
                    fields[k] = True
                elif v.lower() == "false":
                    fields[k] = False
                elif v.isdigit():
                    fields[k] = int(v)
                else:
                    fields[k] = v
    return fields


def load_stage_contracts(stages_dir: str) -> list[dict[str, Any]]:
    """Load all stage contract YAML files, sorted by order.

    Returns:
        List of dicts with at least {order, name, human_gate} keys.
    """
    pattern = os.path.join(stages_dir, "stage-*-*.yaml")
    contracts = []
    for path in sorted(glob.glob(pattern)):
        fields = _read_yaml_fields(path)
        if "order" not in fields:
            continue
        # Ensure human_gate is boolean
        if "human_gate" not in fields:
            fields["human_gate"] = False
        contracts.append(fields)
    contracts.sort(key=lambda c: c["order"])
    return contracts


def build_transition_table(
    contracts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build explicit transition table from ordered stage contracts.

    Each transition specifies:
    - from_stage, to_stage: sequential (N → N+1)
    - human_gate: True if from_stage has a human gate
    - guard: description of gate condition
    - rollback_to: stage to revert to on failure (previous plan stage)

    Returns:
        List of transition dicts, one per adjacent stage pair.
    """
    transitions: list[dict[str, Any]] = []

    # Find the last human-gate stage for rollback targeting
    last_plan_stage = 1  # default rollback target

    for i in range(len(contracts) - 1):
        src = contracts[i]
        dst = contracts[i + 1]

        from_stage = src["order"]
        to_stage = dst["order"]
        is_human = bool(src.get("human_gate", False))

        # Build guard description
        guards = []
        if is_human:
            gate_file = src.get("gate_file", "")
            guards.append(f"human_gate: {gate_file}")
        if src.get("blocking_condition"):
            guards.append(str(src["blocking_condition"]))
        if src.get("pre_checks"):
            guards.append(f"pre_checks: {src['pre_checks']}")

        transition = {
            "from_stage": from_stage,
            "to_stage": to_stage,
            "from_name": src.get("name", ""),
            "to_name": dst.get("name", ""),
            "human_gate": is_human,
            "guard": "; ".join(guards) if guards else "exit_artifacts exist",
            "rollback_to": last_plan_stage,
        }
        transitions.append(transition)

        # Update rollback target after human gate stages
        if is_human:
            last_plan_stage = from_stage

    return transitions


def validate_transition(
    table: list[dict[str, Any]],
    from_stage: int,
    to_stage: int,
) -> bool:
    """Check if a from_stage → to_stage transition is legal.

    Only sequential transitions (N → N+1) are allowed.
    """
    for t in table:
        if t["from_stage"] == from_stage and t["to_stage"] == to_stage:
            return True
    return False


def generate_yaml(stages_dir: str) -> str:
    """Generate YAML representation of the transition table."""
    contracts = load_stage_contracts(stages_dir)
    table = build_transition_table(contracts)

    lines = ["# Auto-generated transition table — do not edit manually",
             "# Source: scripts/work-queue/stages/stage-NN-*.yaml",
             "# WRK-1187 Enhancement 2",
             "",
             "transitions:"]
    for t in table:
        lines.append(f"  - from: {t['from_stage']}")
        lines.append(f"    to: {t['to_stage']}")
        lines.append(f"    from_name: \"{t['from_name']}\"")
        lines.append(f"    to_name: \"{t['to_name']}\"")
        lines.append(f"    human_gate: {str(t['human_gate']).lower()}")
        lines.append(f"    guard: \"{t['guard']}\"")
        lines.append(f"    rollback_to: {t['rollback_to']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import sys
    stages = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "stages"
    )
    if len(sys.argv) > 1:
        stages = sys.argv[1]
    print(generate_yaml(stages))
