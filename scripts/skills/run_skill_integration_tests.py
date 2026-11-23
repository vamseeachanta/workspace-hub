#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""run_skill_integration_tests.py — Integration test runner for skills (Python).

Reads test specs from .planning/skills/integration-tests/*.yaml and validates
that skills produce expected behavior patterns.

Modes:
  --dry-run   Validate specs and skill existence only (no claude CLI needed)
  (default)   Live mode — invokes claude -p with skill content + test prompt

Usage:
  uv run --no-project python scripts/skills/run_skill_integration_tests.py --dry-run
  uv run --no-project python scripts/skills/run_skill_integration_tests.py
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ── Data classes ──────────────────────────────────────────────────────────


@dataclass
class TestCase:
    test_id: str
    description: str
    prompt: str
    expected_patterns: list[str] = field(default_factory=list)
    unexpected_patterns: list[str] = field(default_factory=list)
    timeout: int = 60


@dataclass
class TestSpec:
    version: int
    skill_name: str
    skill_path: str
    tests: list[TestCase] = field(default_factory=list)


@dataclass
class TestResult:
    test_id: str
    status: str  # PASS, FAIL, SKIP
    description: str
    errors: list[str] = field(default_factory=list)


# ── YAML Loading ──────────────────────────────────────────────────────────


def load_yaml(path: Path) -> dict:
    """Load a YAML file, using PyYAML if available, else a minimal fallback."""
    try:
        import yaml

        with path.open(encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except ImportError:
        return _parse_yaml_fallback(path.read_text(encoding="utf-8"))


def _parse_yaml_fallback(text: str) -> dict:
    """Minimal YAML parser for our test spec schema — no external deps."""
    result: dict = {}
    lines = text.splitlines()
    i = 0
    tests: list[dict] = []
    current_test: dict | None = None
    current_list_key: str | None = None

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.lstrip()

        # Top-level keys
        if not line.startswith(" ") and ":" in line:
            key, _, val = line.partition(":")
            val = val.strip().strip("'\"")
            if key == "tests":
                result["tests"] = tests
                current_list_key = None
            elif key in ("version", "skill_name", "skill_path"):
                result[key] = val
                current_list_key = None
            i += 1
            continue

        # Test entry: "  - test_id: value"
        if stripped.startswith("- test_id:"):
            current_test = {}
            tests.append(current_test)
            _, _, val = stripped.partition(":")
            current_test["test_id"] = val.strip().strip("'\"")
            current_list_key = None
            i += 1
            continue

        # Test-level fields
        if current_test is not None and stripped and not stripped.startswith("-"):
            if ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip().strip("'\"")
                if key in ("expected_patterns", "unexpected_patterns"):
                    current_test[key] = []
                    current_list_key = key
                elif key == "prompt" and (val == ">" or val == "|" or val == ""):
                    # Multi-line scalar — collect continuation lines
                    current_test["prompt"] = ""
                    current_list_key = None
                    i += 1
                    indent = len(lines[i]) - len(lines[i].lstrip()) if i < len(lines) else 0
                    parts = []
                    while i < len(lines):
                        cline = lines[i]
                        cindent = len(cline) - len(cline.lstrip())
                        if cindent >= indent and cline.strip():
                            parts.append(cline.strip())
                            i += 1
                        else:
                            break
                    current_test["prompt"] = " ".join(parts)
                    continue
                else:
                    current_test[key] = val
                    current_list_key = None
                i += 1
                continue

        # List items
        if current_list_key and current_test is not None and stripped.startswith("- "):
            val = stripped[2:].strip().strip("'\"")
            current_test[current_list_key].append(val)
            i += 1
            continue

        i += 1

    if "tests" not in result:
        result["tests"] = tests
    return result


# ── Spec parsing ──────────────────────────────────────────────────────────


def parse_spec(path: Path) -> TestSpec:
    """Parse a YAML spec file into a TestSpec object."""
    data = load_yaml(path)
    tests = []
    for t in data.get("tests", []):
        tests.append(
            TestCase(
                test_id=t.get("test_id", "unknown"),
                description=t.get("description", ""),
                prompt=t.get("prompt", ""),
                expected_patterns=t.get("expected_patterns", []),
                unexpected_patterns=t.get("unexpected_patterns", []),
                timeout=int(t.get("timeout", 60)),
            )
        )
    return TestSpec(
        version=int(data.get("version", 1)),
        skill_name=data.get("skill_name", ""),
        skill_path=data.get("skill_path", ""),
        tests=tests,
    )


# ── Test execution ─────────────────────────────────────────────────────


def validate_spec(spec: TestSpec, repo_root: Path) -> list[TestResult]:
    """Dry-run validation: check spec structure and skill existence."""
    results = []
    skill_file = repo_root / spec.skill_path

    for test in spec.tests:
        errors: list[str] = []

        # Check skill file exists
        if not skill_file.is_file():
            errors.append(f"Skill file not found: {spec.skill_path}")

        # Check required fields
        if not test.test_id:
            errors.append("Missing test_id")
        if not test.prompt:
            errors.append("Missing prompt")
        if not test.expected_patterns:
            errors.append("No expected_patterns defined")

        if errors:
            results.append(
                TestResult(
                    test_id=test.test_id,
                    status="FAIL" if "not found" in str(errors) else "SKIP",
                    description=test.description,
                    errors=errors,
                )
            )
        else:
            results.append(
                TestResult(
                    test_id=test.test_id,
                    status="PASS",
                    description=f"{test.description} (dry-run: spec valid, skill exists)",
                )
            )
    return results


def run_live_test(
    spec: TestSpec, test: TestCase, repo_root: Path
) -> TestResult:
    """Run a single test case using claude CLI."""
    skill_file = repo_root / spec.skill_path
    errors: list[str] = []

    # Verify skill exists
    if not skill_file.is_file():
        return TestResult(
            test_id=test.test_id,
            status="FAIL",
            description=test.description,
            errors=[f"Skill file not found: {spec.skill_path}"],
        )

    # Check claude CLI availability
    if not shutil.which("claude"):
        return TestResult(
            test_id=test.test_id,
            status="SKIP",
            description=test.description,
            errors=["claude CLI not found in PATH"],
        )

    # Read skill content
    skill_content = skill_file.read_text(encoding="utf-8")

    # Build full prompt
    full_prompt = (
        f"Here is a skill definition:\n\n"
        f"---SKILL START---\n{skill_content}\n---SKILL END---\n\n"
        f"Based on this skill, respond to the following:\n{test.prompt}"
    )

    # Invoke claude CLI
    try:
        result = subprocess.run(
            ["claude", "-p", full_prompt, "--print"],
            capture_output=True,
            text=True,
            timeout=test.timeout,
            cwd=str(repo_root),
        )
        if result.returncode != 0:
            return TestResult(
                test_id=test.test_id,
                status="FAIL",
                description=test.description,
                errors=[f"claude CLI exited with code {result.returncode}: {result.stderr[:200]}"],
            )
        output = result.stdout
    except subprocess.TimeoutExpired:
        return TestResult(
            test_id=test.test_id,
            status="FAIL",
            description=test.description,
            errors=[f"Timed out after {test.timeout}s"],
        )
    except Exception as e:
        return TestResult(
            test_id=test.test_id,
            status="FAIL",
            description=test.description,
            errors=[f"Exception: {e}"],
        )

    # Check expected patterns
    for pattern in test.expected_patterns:
        if not re.search(pattern, output, re.IGNORECASE):
            errors.append(f"Expected pattern not found: '{pattern}'")

    # Check unexpected patterns
    for pattern in test.unexpected_patterns:
        if re.search(pattern, output, re.IGNORECASE):
            errors.append(f"Unexpected pattern found: '{pattern}'")

    if errors:
        return TestResult(
            test_id=test.test_id,
            status="FAIL",
            description=test.description,
            errors=errors,
        )
    return TestResult(
        test_id=test.test_id,
        status="PASS",
        description=test.description,
    )


# ── Main ───────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Skill integration test runner"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate specs without invoking claude CLI",
    )
    parser.add_argument(
        "--specs-dir",
        default=".planning/skills/integration-tests",
        help="Directory containing test spec YAML files",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show additional output details",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root directory (auto-detected if not set)",
    )
    args = parser.parse_args()

    # Determine repo root
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        # Walk up from script location
        repo_root = Path(__file__).resolve().parent.parent.parent

    specs_dir = repo_root / args.specs_dir

    print("=" * 50)
    print(" Skill Integration Test Runner (Python)")
    print("=" * 50)
    print(f"Specs dir:  {specs_dir}")
    print(f"Mode:       {'dry-run' if args.dry_run else 'live'}")
    print(f"Repo root:  {repo_root}")
    print()

    # Find spec files
    spec_files = sorted(specs_dir.glob("*.yaml")) + sorted(specs_dir.glob("*.yml"))
    if not spec_files:
        print(f"ERROR: No spec files found in {specs_dir}")
        return 1

    print(f"Found {len(spec_files)} spec file(s)")
    print()

    # Counters
    total = 0
    passed = 0
    failed = 0
    skipped = 0
    all_errors: list[str] = []

    for spec_file in spec_files:
        print(f"── {spec_file.name} ──")
        spec = parse_spec(spec_file)
        print(f"  Skill: {spec.skill_name} ({spec.skill_path})")
        print(f"  Tests: {len(spec.tests)}")

        if args.dry_run:
            results = validate_spec(spec, repo_root)
        else:
            results = [run_live_test(spec, t, repo_root) for t in spec.tests]

        for r in results:
            total += 1
            if r.status == "PASS":
                passed += 1
                print(f"  PASS [{r.test_id}] {r.description}")
            elif r.status == "SKIP":
                skipped += 1
                print(f"  SKIP [{r.test_id}] {r.description}")
                for e in r.errors:
                    print(f"       {e}")
            else:
                failed += 1
                print(f"  FAIL [{r.test_id}] {r.description}")
                for e in r.errors:
                    print(f"       {e}")
                    all_errors.append(f"{r.test_id}: {e}")
        print()

    # Summary
    print("=" * 50)
    print(" Summary")
    print("=" * 50)
    print(f"  Total:  {total}")
    print(f"  Pass:   {passed}")
    print(f"  Fail:   {failed}")
    print(f"  Skip:   {skipped}")
    print()

    if all_errors:
        print("Errors:")
        for err in all_errors:
            print(f"  - {err}")
        print()

    if failed > 0:
        print("RESULT: FAILED")
        return 1
    else:
        print("RESULT: PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
