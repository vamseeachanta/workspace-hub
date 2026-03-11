#!/usr/bin/env python3
"""Quality gap discovery script (WRK-1060).

Walks all tier-1 repo directories and classifies each path against known quality
check coverage, producing a YAML gap report.

Usage:
    uv run --no-project python scripts/quality/quality_gap_report.py [--repo <name>] [--output <path>]

Output: gap report YAML to --output (default: config/quality/quality-gap-report.yaml)
        human-readable summary to stdout
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ---------------------------------------------------------------------------
# Repo map: lowercase name -> relative path from workspace root
# ---------------------------------------------------------------------------
REPO_MAP: dict[str, str] = {
    "assetutilities": "assetutilities",
    "digitalmodel": "digitalmodel",
    "worldenergydata": "worldenergydata",
    "assethold": "assethold",
    "ogmanufacturing": "OGManufacturing",
}

# ---------------------------------------------------------------------------
# Coverage map: dir pattern -> {tools, coverage, recommended_tool, effort}
# "partial_for" repos get upgraded coverage; others get base_coverage.
# ---------------------------------------------------------------------------
_COVERAGE_MAP: dict[str, dict[str, Any]] = {
    "src/": {
        "tools": ["ruff", "mypy", "pytest", "bandit"],
        "coverage": "covered",
        "recommended_tool": None,
        "effort": None,
    },
    "tests/": {
        "tools": ["ruff", "pytest"],
        "coverage": "covered",
        "recommended_tool": None,
        "effort": None,
    },
    "scripts/": {
        "tools": [],
        "coverage": "uncovered",
        "recommended_tool": "ruff",
        "effort": "low",
    },
    "examples/": {
        "tools": [],
        "coverage": "uncovered",
        "recommended_tool": "ruff",
        "effort": "low",
    },
    "notebooks/": {
        "tools": [],
        "coverage": "uncovered",
        "recommended_tool": "nbqa",
        "effort": "medium",
        # digitalmodel already has nbqa
        "partial_for": ["digitalmodel"],
    },
    "docs/": {
        "tools": [],
        "coverage": "uncovered",
        "recommended_tool": "markdownlint",
        "effort": "low",
        # digitalmodel and worldenergydata have markdown checks
        "partial_for": ["digitalmodel", "worldenergydata"],
    },
    "config/": {
        "tools": [],
        "coverage": "uncovered",
        "recommended_tool": "yamllint",
        "effort": "medium",
        # worldenergydata already has yamllint in pre-commit
        "partial_for": ["worldenergydata"],
    },
    "data/": {
        "tools": [],
        "coverage": "uncovered",
        "recommended_tool": "schema-validation",
        "effort": "high",
    },
}

# ---------------------------------------------------------------------------
# Cross-cutting gaps: missing checks not tied to a specific directory
# ---------------------------------------------------------------------------
_CROSS_CUTTING_MAP: dict[str, dict[str, Any]] = {
    "pydocstyle": {
        "description": "docstring style enforcement",
        "missing_in": ["assetutilities", "worldenergydata", "assethold", "ogmanufacturing"],
        "tool": "ruff-pydocstyle",
        "effort": "low",
    },
    "radon_complexity": {
        "description": "cyclomatic complexity gate",
        "missing_in": ["assetutilities", "worldenergydata", "assethold", "ogmanufacturing"],
        "tool": "radon",
        "effort": "low",
    },
    "vulture_dead_code": {
        "description": "dead code detection",
        "missing_in": ["assetutilities", "worldenergydata", "assethold", "ogmanufacturing"],
        "tool": "vulture",
        "effort": "low",
    },
    "commitizen": {
        "description": "conventional commit linting",
        # worldenergydata already has commitizen
        "missing_in": ["assetutilities", "digitalmodel", "assethold", "ogmanufacturing"],
        "tool": "commitizen",
        "effort": "low",
    },
    "windows_path_guard": {
        "description": "Windows path artifact detection",
        # worldenergydata already has windows path guard (WRK-364)
        "missing_in": ["assetutilities", "assethold"],
        "tool": "pre-commit-hook",
        "effort": "low",
    },
    "api_audit": {
        "description": "public API docstring coverage audit",
        "missing_in": ["assetutilities", "digitalmodel", "worldenergydata", "assethold", "ogmanufacturing"],
        "tool": "api-audit.py",
        "effort": "low",
    },
    "ratchet_gates": {
        "description": "mypy and complexity ratchet gates in pre-commit",
        "missing_in": ["assetutilities", "digitalmodel", "worldenergydata", "assethold", "ogmanufacturing"],
        "tool": "check_mypy_ratchet.py / check_complexity_ratchet.py",
        "effort": "medium",
    },
}


def classify_dir(dir_pattern: str, repo: str) -> dict[str, Any]:
    """Return coverage classification for a directory pattern in a given repo.

    Returns dict with keys: coverage, tools, recommended_tool, effort.
    """
    entry = _COVERAGE_MAP.get(dir_pattern)
    if entry is None:
        return {"coverage": "unknown", "tools": [], "recommended_tool": None, "effort": None}

    partial_for = entry.get("partial_for", [])
    if repo in partial_for:
        # Repo has some coverage for this dir
        result = dict(entry)
        result["coverage"] = "partial"
        result.pop("partial_for", None)
        return result

    result = dict(entry)
    result.pop("partial_for", None)
    return result


def _walk_repo_dirs(repo_path: Path) -> list[str]:
    """Return list of top-level directory patterns that exist in repo_path."""
    found = []
    for pattern in _COVERAGE_MAP:
        # Match by checking if top-level dir exists
        target = repo_path / pattern.rstrip("/")
        if target.is_dir():
            found.append(pattern)
    return found


def build_gap_report(
    repo_map: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Build the full gap report dict.

    Args:
        repo_map: mapping of repo name -> relative path (defaults to REPO_MAP)
        repo_root: workspace root (defaults to 2 levels up from this file)
    """
    if repo_map is None:
        repo_map = REPO_MAP
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]

    repos: dict[str, Any] = {}
    total_gaps = 0

    for repo_name, repo_rel in repo_map.items():
        repo_path = repo_root / repo_rel
        existing_dirs = _walk_repo_dirs(repo_path)

        dir_gaps: dict[str, Any] = {}
        dir_covered: dict[str, Any] = {}

        for dir_pattern in existing_dirs:
            info = classify_dir(dir_pattern, repo_name)
            if info["coverage"] in ("uncovered", "partial"):
                dir_gaps[dir_pattern] = {
                    "coverage": info["coverage"],
                    "recommended_tool": info.get("recommended_tool"),
                    "effort": info.get("effort"),
                }
                total_gaps += 1
            else:
                dir_covered[dir_pattern] = {"tools": info.get("tools", [])}

        # Cross-cutting gaps for this repo
        cross_cutting: list[str] = []
        for gap_name, gap_info in _CROSS_CUTTING_MAP.items():
            if repo_name in gap_info.get("missing_in", []):
                cross_cutting.append(gap_name)

        repos[repo_name] = {
            "dir_gaps": dir_gaps,
            "dir_covered": dir_covered,
            "cross_cutting_gaps": cross_cutting,
        }

    return {
        "schema_version": "1",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "repos": repos,
        "summary": {
            "total_gaps": total_gaps,
            "repos_scanned": len(repo_map),
        },
    }


def _dump_yaml(data: dict[str, Any]) -> str:
    if not _HAS_YAML:
        raise ImportError("PyYAML is required: uv add pyyaml")
    return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)


def _print_summary(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print(f"\n{'='*60}")
    print(f"Quality Gap Report — {report['generated_at'][:10]}")
    print(f"{'='*60}")
    print(f"Repos scanned: {summary['repos_scanned']}")
    print(f"Total dir gaps: {summary['total_gaps']}")
    print()

    for repo_name, repo_data in report["repos"].items():
        gaps = repo_data.get("dir_gaps", {})
        cc_gaps = repo_data.get("cross_cutting_gaps", [])
        print(f"  {repo_name}:")
        if gaps:
            for dir_pat, gap in gaps.items():
                cov = gap["coverage"]
                tool = gap.get("recommended_tool") or "—"
                effort = gap.get("effort") or "—"
                print(f"    [GAP/{cov}] {dir_pat:<15} → {tool} (effort: {effort})")
        else:
            print("    [OK] all tracked dirs covered")
        if cc_gaps:
            print(f"    cross-cutting: {', '.join(cc_gaps)}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quality gap discovery across tier-1 repos (WRK-1060)"
    )
    parser.add_argument("--repo", help="Run only this repo (lowercase name)")
    parser.add_argument(
        "--output",
        default="config/quality/quality-gap-report.yaml",
        help="Output YAML path (default: config/quality/quality-gap-report.yaml)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]

    repo_map = REPO_MAP
    if args.repo:
        if args.repo not in REPO_MAP:
            print(f"ERROR: Unknown repo '{args.repo}'. Valid: {list(REPO_MAP)}", file=sys.stderr)
            sys.exit(1)
        repo_map = {args.repo: REPO_MAP[args.repo]}

    report = build_gap_report(repo_map=repo_map, repo_root=repo_root)

    out_path = repo_root / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_dump_yaml(report), encoding="utf-8")
    print(f"✔ Gap report written to {args.output}")

    _print_summary(report)


if __name__ == "__main__":
    main()
