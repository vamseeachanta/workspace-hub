#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Single-pass SKILL.md auditor — replaces audit-skill-violations.sh + skill-coverage-audit.sh.

Usage:
    uv run --no-project python scripts/skills/audit-skills.py --mode violations
    uv run --no-project python scripts/skills/audit-skills.py --mode coverage
    uv run --no-project python scripts/skills/audit-skills.py --mode all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure sibling module is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_skill_lib import (  # noqa: E402
    format_all_yaml,
    format_coverage_yaml,
    format_violations_yaml,
    run_coverage_audit,
    run_violations_audit,
)


def cli_run(args: list[str]) -> tuple[int, str]:
    """Run with given args, return (exit_code, stdout_output)."""
    parser = argparse.ArgumentParser(description="Single-pass SKILL.md auditor")
    parser.add_argument("--mode", choices=["violations", "coverage", "all"],
                        default="all", help="Which checks to run")
    parser.add_argument("--skill-dir", default=None,
                        help="Skills directory (default: .claude/skills)")
    parsed = parser.parse_args(args)

    if parsed.skill_dir:
        skill_dir = Path(parsed.skill_dir)
    else:
        repo_root = Path(__file__).resolve().parent.parent.parent
        skill_dir = repo_root / ".claude" / "skills"

    if not skill_dir.is_dir():
        return 2, f"Error: skill dir not found: {skill_dir}\n"

    if parsed.mode == "violations":
        results = run_violations_audit(skill_dir)
        return (1 if results else 0), format_violations_yaml(results)

    if parsed.mode == "coverage":
        results = run_coverage_audit(skill_dir)
        return (1 if results else 0), format_coverage_yaml(results)

    violations = run_violations_audit(skill_dir)
    gaps = run_coverage_audit(skill_dir)
    code = 1 if (violations or gaps) else 0
    return code, format_all_yaml(violations, gaps)


def main() -> int:
    exit_code, output = cli_run(sys.argv[1:])
    if output:
        print(output, end="")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
