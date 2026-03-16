#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Skill ecosystem quality evaluation orchestrator.

Chains audit-skills.py (violations + coverage) and eval-skills.py into
a single YAML summary. Pure Python — no shell injection surface.

Usage: uv run --no-project python scripts/skills/skill_eval_ecosystem.py [--output FILE]
"""
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml


@dataclass
class EvalResult:
    total_skills: int = 0
    passed: int = 0
    warnings: int = 0
    critical: int = 0
    violations_count: int = 0
    coverage_gap_count: int = 0

    @property
    def pass_rate(self) -> str:
        if self.total_skills == 0:
            return "0.0%"
        return f"{self.passed / self.total_skills * 100:.1f}%"

    @property
    def exit_code(self) -> int:
        return 1 if self.critical > 0 else 0

    def to_yaml(self) -> str:
        data = {
            "total_skills": self.total_skills,
            "violations": {"count": self.violations_count},
            "coverage_gaps": {"count": self.coverage_gap_count},
            "eval_summary": {
                "passed": self.passed,
                "warnings": self.warnings,
                "critical": self.critical,
                "pass_rate": self.pass_rate,
            },
            "generated_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        }
        return yaml.dump(data, default_flow_style=False, sort_keys=False)


def _run_script(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run a script, propagating failures explicitly."""
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        timeout=120,
    )
    return result


def run_ecosystem_eval(repo_root: Path) -> EvalResult:
    """Run all three audit passes and return combined result."""
    audit_script = repo_root / "scripts" / "skills" / "audit-skills.py"
    eval_script = (
        repo_root
        / ".claude"
        / "skills"
        / "development"
        / "skill-eval"
        / "scripts"
        / "eval-skills.py"
    )

    result = EvalResult()

    # Violations audit
    if audit_script.exists():
        proc = _run_script(
            [
                "uv", "run", "--no-project", "python",
                str(audit_script), "--mode", "violations",
            ],
            repo_root,
        )
        if proc.returncode in (0, 1):
            result.violations_count = proc.stdout.count("  - file:")
        else:
            print(
                f"WARNING: audit-skills.py violations failed "
                f"(exit {proc.returncode}): {proc.stderr[:200]}",
                file=sys.stderr,
            )
    else:
        print(f"ERROR: {audit_script} not found", file=sys.stderr)
        sys.exit(2)

    # Coverage audit
    proc = _run_script(
        [
            "uv", "run", "--no-project", "python",
            str(audit_script), "--mode", "coverage",
        ],
        repo_root,
    )
    if proc.returncode in (0, 1):
        result.coverage_gap_count = proc.stdout.count("  - path:")
    else:
        print(
            f"WARNING: audit-skills.py coverage failed "
            f"(exit {proc.returncode}): {proc.stderr[:200]}",
            file=sys.stderr,
        )

    # Eval pass
    if eval_script.exists():
        proc = _run_script(
            [
                "uv", "run", "--no-project", "python",
                str(eval_script), "--format", "json",
                "--severity", "warning",
            ],
            repo_root,
        )
        if proc.returncode in (0, 1) and proc.stdout.strip():
            try:
                data = json.loads(proc.stdout)
                summary = data.get("summary", data)
                result.total_skills = summary.get("total_skills", 0)
                result.passed = summary.get("passed", 0)
                issues = summary.get("issues", {})
                result.warnings = issues.get("warning", 0)
                result.critical = issues.get("critical", 0)
            except json.JSONDecodeError as e:
                print(
                    f"WARNING: eval-skills.py JSON parse error: {e}",
                    file=sys.stderr,
                )
        else:
            print(
                f"WARNING: eval-skills.py failed "
                f"(exit {proc.returncode}): {proc.stderr[:200]}",
                file=sys.stderr,
            )
    else:
        print(f"ERROR: {eval_script} not found", file=sys.stderr)
        sys.exit(2)

    return result


def main():
    output_path = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            output_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--help":
            print("Usage: skill_eval_ecosystem.py [--output FILE]")
            print(
                "Runs audit-skills.py + eval-skills.py, "
                "outputs combined YAML summary."
            )
            sys.exit(0)
        else:
            print(f"Unknown option: {args[i]}", file=sys.stderr)
            sys.exit(2)

    repo_root = Path(".")
    result = run_ecosystem_eval(repo_root)
    yaml_output = result.to_yaml()

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(yaml_output)
        print(f"Summary written to {output_path}", file=sys.stderr)
    else:
        print(yaml_output, end="")

    sys.exit(result.exit_code)


if __name__ == "__main__":
    main()
