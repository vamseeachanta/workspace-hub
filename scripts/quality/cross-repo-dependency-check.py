#!/usr/bin/env python3
"""Cross-repo dependency verification for workspace-hub tier-1 repos.

Scans tier-1 repositories for Python imports that reference other tier-1 repos,
compares against declared dependencies in pyproject.toml, and reports violations
including undeclared dependencies, missing dependencies, and circular chains.

Usage:
    uv run scripts/quality/cross-repo-dependency-check.py
    uv run scripts/quality/cross-repo-dependency-check.py --workspace /path/to/workspace-hub
    uv run scripts/quality/cross-repo-dependency-check.py --output-dir docs/reports
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
import tomllib
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── Tier-1 repo definitions ─────────────────────────────────────────────────

TIER1_REPOS: list[str] = [
    "digitalmodel",
    "assetutilities",
    "aceengineer-strategy",
    "achantas-data",
    "assethold",
]

# Map from repo directory name → possible Python import names
# (repo name, underscored variant, and known package names from src/)
REPO_TO_IMPORT_NAMES: dict[str, list[str]] = {
    "digitalmodel": ["digitalmodel"],
    "assetutilities": ["assetutilities"],
    "aceengineer-strategy": ["aceengineer_strategy", "aceengineer-strategy"],
    "achantas-data": ["achantas_data", "achantas-data"],
    "assethold": ["assethold"],
}

# Reverse map: import name → repo name
IMPORT_NAME_TO_REPO: dict[str, str] = {}
for _repo, _names in REPO_TO_IMPORT_NAMES.items():
    for _name in _names:
        IMPORT_NAME_TO_REPO[_name] = _repo


# ── Data structures ─────────────────────────────────────────────────────────


@dataclass
class RepoInfo:
    """Information gathered about a single tier-1 repository."""

    name: str
    path: Path
    exists: bool = False
    has_pyproject: bool = False
    package_name: str = ""
    declared_deps: list[str] = field(default_factory=list)
    # tier-1 repo names that are declared as dependencies
    declared_tier1_deps: list[str] = field(default_factory=list)
    # tier-1 repo names discovered via import scanning
    imported_tier1_deps: set[str] = field(default_factory=set)
    python_file_count: int = 0
    import_details: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Violation:
    """A dependency violation."""

    kind: str  # "undeclared", "missing", "circular"
    source_repo: str
    target_repo: str = ""
    details: str = ""
    file_path: str = ""
    line_number: int = 0

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"kind": self.kind, "source_repo": self.source_repo}
        if self.target_repo:
            d["target_repo"] = self.target_repo
        if self.details:
            d["details"] = self.details
        if self.file_path:
            d["file_path"] = self.file_path
        if self.line_number:
            d["line_number"] = self.line_number
        return d


# ── Import scanning ─────────────────────────────────────────────────────────


def extract_imports_from_file(filepath: Path) -> list[dict[str, Any]]:
    """Parse a Python file with ast and extract all import module names.

    Returns a list of dicts: {"module": str, "line": int, "kind": "import"|"from"}
    """
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, ValueError):
        return []

    imports: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    {"module": alias.name, "line": node.lineno, "kind": "import"}
                )
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(
                    {"module": node.module, "line": node.lineno, "kind": "from"}
                )
    return imports


def get_top_level_module(module_name: str) -> str:
    """Extract the top-level module from a dotted import path."""
    return module_name.split(".")[0]


def scan_repo_imports(
    repo_info: RepoInfo, all_import_names: dict[str, str]
) -> None:
    """Scan all Python files in a repo and find imports of other tier-1 repos."""
    search_dirs = [repo_info.path / "src", repo_info.path]
    python_files: list[Path] = []

    for search_dir in search_dirs:
        if search_dir.is_dir():
            for py_file in search_dir.rglob("*.py"):
                # Skip hidden dirs, __pycache__, .egg-info, venv, .venv
                parts = py_file.relative_to(repo_info.path).parts
                if any(
                    p.startswith(".") or p == "__pycache__" or p.endswith(".egg-info")
                    or p in ("venv", ".venv", "node_modules", ".tox")
                    for p in parts
                ):
                    continue
                python_files.append(py_file)

    repo_info.python_file_count = len(python_files)

    for py_file in python_files:
        file_imports = extract_imports_from_file(py_file)
        for imp in file_imports:
            top_level = get_top_level_module(imp["module"])
            if top_level in all_import_names:
                target_repo = all_import_names[top_level]
                # Don't count self-imports
                if target_repo != repo_info.name:
                    repo_info.imported_tier1_deps.add(target_repo)
                    repo_info.import_details.append(
                        {
                            "file": str(py_file.relative_to(repo_info.path)),
                            "module": imp["module"],
                            "line": imp["line"],
                            "kind": imp["kind"],
                            "target_repo": target_repo,
                        }
                    )


# ── pyproject.toml parsing ──────────────────────────────────────────────────


def parse_pyproject_deps(pyproject_path: Path) -> tuple[str, list[str]]:
    """Parse pyproject.toml and return (project_name, list_of_dependency_strings).

    Returns ("", []) if file doesn't exist or can't be parsed.
    """
    if not pyproject_path.is_file():
        return "", []

    try:
        content = pyproject_path.read_text(encoding="utf-8")
        # Handle git merge conflict markers by stripping them
        clean_lines = []
        for line in content.splitlines():
            if line.startswith(("<<<<<<", "======", ">>>>>>")):
                continue
            clean_lines.append(line)
        data = tomllib.loads("\n".join(clean_lines))
    except (tomllib.TOMLDecodeError, ValueError, KeyError):
        return "", []

    project = data.get("project", {})
    name = project.get("name", "")
    deps = project.get("dependencies", [])
    return name, deps


def normalize_dep_name(dep_string: str) -> str:
    """Extract the package name from a PEP 508 dependency string.

    Examples:
        "assetutilities>=0.0.7" -> "assetutilities"
        "beautifulsoup4>=4.12.0" -> "beautifulsoup4"
        "assetutilities" -> "assetutilities"
    """
    # Strip extras like [dev]
    name = dep_string.split("[")[0]
    # Strip version specifiers
    for sep in (">=", "<=", "==", "!=", "~=", ">", "<", ";", "@"):
        name = name.split(sep)[0]
    return name.strip().lower().replace("-", "_")


def find_tier1_in_deps(
    dep_strings: list[str], all_import_names: dict[str, str]
) -> list[str]:
    """Find which tier-1 repos are declared as dependencies.

    Returns list of repo names.
    """
    found: list[str] = []
    for dep_str in dep_strings:
        dep_name = normalize_dep_name(dep_str)
        # Check against all known import/package names
        for import_name, repo_name in all_import_names.items():
            normalized_import = import_name.lower().replace("-", "_")
            if dep_name == normalized_import and repo_name not in found:
                found.append(repo_name)
    return found


# ── Cycle detection ─────────────────────────────────────────────────────────


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Find all cycles in a directed graph using DFS.

    Returns list of cycles, where each cycle is a list of node names.
    """
    cycles: list[list[str]] = []
    visited: set[str] = set()
    rec_stack: set[str] = set()
    path: list[str] = []

    def dfs(node: str) -> None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        path.pop()
        rec_stack.discard(node)

    for node in graph:
        if node not in visited:
            dfs(node)

    return cycles


# ── Output generation ───────────────────────────────────────────────────────


def generate_mermaid(repos: dict[str, RepoInfo]) -> str:
    """Generate a Mermaid flowchart of the dependency graph."""
    lines = ["graph LR"]

    # Add nodes
    for name, info in sorted(repos.items()):
        if info.exists:
            label = f'{name.replace("-", "_")}["{name}"]'
            lines.append(f"    {label}")

    # Add edges from imports (solid = declared, dashed = undeclared)
    for name, info in sorted(repos.items()):
        if not info.exists:
            continue
        src = name.replace("-", "_")
        for dep in sorted(info.imported_tier1_deps):
            tgt = dep.replace("-", "_")
            if dep in info.declared_tier1_deps:
                lines.append(f"    {src} --> {tgt}")
            else:
                lines.append(f'    {src} -.->|"undeclared"| {tgt}')

        # Declared but not imported
        for dep in sorted(info.declared_tier1_deps):
            if dep not in info.imported_tier1_deps:
                tgt = dep.replace("-", "_")
                lines.append(f'    {src} -.->|"declared only"| {tgt}')

    return "\n".join(lines) + "\n"


def generate_report(
    repos: dict[str, RepoInfo],
    violations: list[Violation],
    cycles: list[list[str]],
) -> dict[str, Any]:
    """Generate the full JSON report."""
    repo_summaries = {}
    for name, info in sorted(repos.items()):
        if not info.exists:
            repo_summaries[name] = {"status": "missing"}
            continue
        repo_summaries[name] = {
            "status": "scanned",
            "has_pyproject": info.has_pyproject,
            "package_name": info.package_name,
            "python_file_count": info.python_file_count,
            "declared_tier1_deps": sorted(info.declared_tier1_deps),
            "imported_tier1_deps": sorted(info.imported_tier1_deps),
            "import_details": info.import_details,
        }

    # Build the import graph for the report
    import_graph: dict[str, list[str]] = {}
    for name, info in repos.items():
        if info.exists:
            import_graph[name] = sorted(info.imported_tier1_deps)

    return {
        "schema_version": "1.0",
        "tier1_repos": TIER1_REPOS,
        "repos": repo_summaries,
        "import_graph": import_graph,
        "violations": [v.to_dict() for v in violations],
        "cycles": cycles,
        "stats": {
            "repos_scanned": sum(1 for r in repos.values() if r.exists),
            "repos_missing": sum(1 for r in repos.values() if not r.exists),
            "total_violations": len(violations),
            "undeclared_count": sum(1 for v in violations if v.kind == "undeclared"),
            "missing_count": sum(1 for v in violations if v.kind == "missing"),
            "circular_count": sum(1 for v in violations if v.kind == "circular"),
            "total_cross_repo_imports": sum(
                len(r.import_details) for r in repos.values() if r.exists
            ),
        },
    }


def print_summary(
    repos: dict[str, RepoInfo],
    violations: list[Violation],
    cycles: list[list[str]],
) -> None:
    """Print a human-readable summary to stdout."""
    print("=" * 70)
    print("CROSS-REPO DEPENDENCY CHECK")
    print("=" * 70)
    print()

    # Repo status
    print("Tier-1 Repos:")
    for name, info in sorted(repos.items()):
        if not info.exists:
            print(f"  {name:30s}  MISSING (skipped)")
        elif not info.has_pyproject:
            print(f"  {name:30s}  No pyproject.toml (skipped deps)")
        else:
            print(
                f"  {name:30s}  OK  ({info.python_file_count} .py files, "
                f"{len(info.imported_tier1_deps)} cross-repo imports)"
            )
    print()

    # Import graph
    print("Import Graph (repo -> depends on):")
    any_edges = False
    for name, info in sorted(repos.items()):
        if info.exists and info.imported_tier1_deps:
            deps = ", ".join(sorted(info.imported_tier1_deps))
            print(f"  {name} -> {deps}")
            any_edges = True
    if not any_edges:
        print("  (no cross-repo imports detected)")
    print()

    # Violations
    if violations:
        print(f"VIOLATIONS ({len(violations)}):")
        for v in violations:
            if v.kind == "undeclared":
                print(
                    f"  [UNDECLARED] {v.source_repo} imports {v.target_repo} "
                    f"but does not declare it in pyproject.toml"
                )
                if v.file_path:
                    print(f"               at {v.file_path}:{v.line_number}")
            elif v.kind == "missing":
                print(
                    f"  [MISSING]    {v.source_repo} declares {v.target_repo} "
                    f"in pyproject.toml but never imports it"
                )
            elif v.kind == "circular":
                print(f"  [CIRCULAR]   {v.details}")
        print()
    else:
        print("No violations found.")
        print()

    # Cycles
    if cycles:
        print(f"Circular Dependencies ({len(cycles)}):")
        for cycle in cycles:
            print(f"  {' -> '.join(cycle)}")
        print()

    # Summary line
    total = len(violations)
    if total == 0:
        print("RESULT: PASS - No dependency violations detected")
    else:
        print(f"RESULT: FAIL - {total} violation(s) found")


# ── Main orchestration ──────────────────────────────────────────────────────


def analyze_workspace(workspace: Path) -> tuple[
    dict[str, RepoInfo], list[Violation], list[list[str]]
]:
    """Run the full analysis on a workspace directory.

    Returns (repos, violations, cycles).
    """
    repos: dict[str, RepoInfo] = {}

    # Phase 1: Discover repos and parse pyproject.toml
    for repo_name in TIER1_REPOS:
        repo_path = workspace / repo_name
        info = RepoInfo(name=repo_name, path=repo_path)

        if not repo_path.is_dir():
            print(f"WARNING: Repo '{repo_name}' not found at {repo_path}, skipping.",
                  file=sys.stderr)
            repos[repo_name] = info
            continue

        info.exists = True
        pyproject_path = repo_path / "pyproject.toml"

        if pyproject_path.is_file():
            info.has_pyproject = True
            pkg_name, dep_strings = parse_pyproject_deps(pyproject_path)
            info.package_name = pkg_name
            info.declared_deps = dep_strings
            info.declared_tier1_deps = find_tier1_in_deps(
                dep_strings, IMPORT_NAME_TO_REPO
            )

        repos[repo_name] = info

    # Phase 2: Scan imports
    for info in repos.values():
        if info.exists:
            scan_repo_imports(info, IMPORT_NAME_TO_REPO)

    # Phase 3: Detect violations
    violations: list[Violation] = []

    for name, info in repos.items():
        if not info.exists:
            continue

        # Undeclared: imported but not in pyproject.toml
        for dep in sorted(info.imported_tier1_deps):
            if dep not in info.declared_tier1_deps:
                # Find first import for details
                first_import = next(
                    (d for d in info.import_details if d["target_repo"] == dep),
                    None,
                )
                violations.append(
                    Violation(
                        kind="undeclared",
                        source_repo=name,
                        target_repo=dep,
                        details=(
                            f"{name} imports {dep} but does not list it "
                            f"in pyproject.toml dependencies"
                        ),
                        file_path=first_import["file"] if first_import else "",
                        line_number=first_import["line"] if first_import else 0,
                    )
                )

        # Missing: declared but not imported
        if info.has_pyproject:
            for dep in sorted(info.declared_tier1_deps):
                if dep not in info.imported_tier1_deps:
                    violations.append(
                        Violation(
                            kind="missing",
                            source_repo=name,
                            target_repo=dep,
                            details=(
                                f"{name} declares {dep} in pyproject.toml "
                                f"but never imports it"
                            ),
                        )
                    )

    # Phase 4: Detect cycles
    import_graph: dict[str, set[str]] = {}
    for name, info in repos.items():
        if info.exists:
            import_graph[name] = info.imported_tier1_deps.copy()

    cycles = find_cycles(import_graph)

    for cycle in cycles:
        violations.append(
            Violation(
                kind="circular",
                source_repo=cycle[0],
                details=" -> ".join(cycle),
            )
        )

    return repos, violations, cycles


def main(argv: list[str] | None = None) -> int:
    """Entry point with argparse."""
    parser = argparse.ArgumentParser(
        description="Cross-repo dependency verification for workspace-hub tier-1 repos.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="Path to workspace-hub root (default: auto-detect from script location)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for reports (default: <workspace>/docs/reports)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output only JSON report to stdout (no summary)",
    )
    args = parser.parse_args(argv)

    workspace = args.workspace.resolve()
    output_dir = (args.output_dir or workspace / "docs" / "reports").resolve()

    if not workspace.is_dir():
        print(f"ERROR: Workspace directory not found: {workspace}", file=sys.stderr)
        return 1

    # Run analysis
    repos, violations, cycles = analyze_workspace(workspace)

    # Generate outputs
    output_dir.mkdir(parents=True, exist_ok=True)

    # Mermaid diagram
    mermaid_path = output_dir / "dependency-graph.mermaid"
    mermaid_content = generate_mermaid(repos)
    mermaid_path.write_text(mermaid_content, encoding="utf-8")

    # JSON report
    report = generate_report(repos, violations, cycles)
    report_path = output_dir / "dependency-report.json"
    report_path.write_text(
        json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8"
    )

    if args.json_only:
        print(json.dumps(report, indent=2, default=str))
    else:
        print_summary(repos, violations, cycles)
        print(f"\nReports written to:")
        print(f"  {mermaid_path}")
        print(f"  {report_path}")

    # Return non-zero if violations found
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
