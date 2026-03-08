#!/usr/bin/env python3
"""
validate-stage-gate-policy.py — L3 schema validator for stage-gate-policy.yaml.

Usage:
    uv run --no-project python validate-stage-gate-policy.py [path/to/policy.yaml]

Exit codes:
    0 = valid
    1 = validation failed
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not available", file=sys.stderr)
    sys.exit(1)

REQUIRED_STAGES = set(range(1, 21))  # stages 1-20
VALID_GATE_TYPES = {"hard", "auto"}
EXPECTED_HARD_GATES = {1, 5, 7, 17}


def validate(policy_path: Path) -> list[str]:
    """Return list of error strings; empty = valid."""
    if not policy_path.exists():
        return [f"policy file not found: {policy_path}"]
    try:
        data = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return [f"YAML parse error: {exc}"]
    if not isinstance(data, dict):
        return ["policy root is not a mapping"]

    stages = data.get("stages")
    if not stages or not isinstance(stages, dict):
        return ["'stages' key missing or not a mapping"]

    errors: list[str] = []
    found_stages: set[int] = set()
    hard_gate_stages: set[int] = set()

    for key, stage_def in stages.items():
        try:
            stage_num = int(key)
        except (ValueError, TypeError):
            errors.append(f"non-integer stage key: {key!r}")
            continue
        found_stages.add(stage_num)
        if not isinstance(stage_def, dict):
            errors.append(f"stage {stage_num}: definition must be a mapping")
            continue
        gate_type = stage_def.get("gate_type")
        if gate_type not in VALID_GATE_TYPES:
            errors.append(
                f"stage {stage_num}: gate_type={gate_type!r} "
                f"(must be one of {sorted(VALID_GATE_TYPES)})"
            )
        if gate_type == "hard":
            hard_gate_stages.add(stage_num)

    missing = REQUIRED_STAGES - found_stages
    if missing:
        errors.append(f"missing stages: {sorted(missing)}")

    if hard_gate_stages != EXPECTED_HARD_GATES:
        errors.append(
            f"hard gates = {sorted(hard_gate_stages)}, "
            f"expected {sorted(EXPECTED_HARD_GATES)}"
        )

    return errors


def main() -> None:
    policy_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if policy_arg is None:
        # Default: validate the canonical policy file
        repo_root = Path(__file__).resolve().parents[2]
        policy_path = Path(__file__).resolve().parent / "stage-gate-policy.yaml"
    else:
        policy_path = Path(policy_arg)

    errors = validate(policy_path)
    if errors:
        for err in errors:
            print(f"✖ {err}", file=sys.stderr)
        print(f"\nValidation FAILED ({len(errors)} error(s)): {policy_path}",
              file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✔ stage-gate-policy.yaml valid: {policy_path}")


if __name__ == "__main__":
    main()
