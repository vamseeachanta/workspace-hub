#!/usr/bin/env python3
"""Architecture scanner: API surface + import dependency graph.

Walks all .py files under a repo's package structure and produces:
  - Per-package metrics: modules, classes, functions, LOC
  - Public API surface (non-_ prefixed classes and functions)
  - Import dependency graph (which package imports which)
  - Structured YAML report
  - Markdown report with Mermaid dependency graph

Usage:
    uv run python scripts/analysis/architecture-scanner.py [REPO_PATH]

Defaults to digitalmodel/ if no path given.
Outputs to docs/architecture/api-surface-map.md and .yaml

Related: GitHub issue #1604
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


def _find_package_root(repo_path: Path) -> Path:
    """Find the directory containing top-level packages.

    Checks for PEP 621 src/ layout first, then falls back to repo root.
    """
    src_dir = repo_path / "src"
    if src_dir.is_dir():
        subdirs = [
            d for d in src_dir.iterdir()
            if d.is_dir()
            and not d.name.startswith((".", "_"))
            and not d.name.endswith((".egg-info", ".dist-info"))
        ]
        if len(subdirs) == 1 and (subdirs[0] / "__init__.py").exists():
            return subdirs[0]
        return src_dir
    return repo_path


def _detect_namespace_package(repo_path: Path) -> str | None:
    """Detect the top-level namespace package name (e.g. 'digitalmodel')."""
    src_dir = repo_path / "src"
    if src_dir.is_dir():
        subdirs = [
            d for d in src_dir.iterdir()
            if d.is_dir()
            and not d.name.startswith((".", "_"))
            and not d.name.endswith((".egg-info", ".dist-info"))
        ]
        if len(subdirs) == 1 and (subdirs[0] / "__init__.py").exists():
            return subdirs[0].name
    return None


def discover_packages(repo_path: Path) -> list[dict[str, Any]]:
    """Discover all top-level Python packages and compute metrics.

    Returns a list of dicts with keys:
        name, path, modules, classes, functions, loc,
        public_classes, public_functions, has_all, has_tests
    """
    repo_path = Path(repo_path).resolve()
    search_root = _find_package_root(repo_path)

    # Find test directories
    tests_root = repo_path / "tests"
    test_dirs = set()
    if tests_root.is_dir():
        for d in tests_root.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                test_dirs.add(d.name)

    packages = []
    for entry in sorted(search_root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith((".", "_")):
            continue
        if not (entry / "__init__.py").exists():
            continue

        # Gather all .py files (exclude __pycache__)
        py_files = [
            f for f in entry.rglob("*.py")
            if "__pycache__" not in str(f)
        ]

        # Count metrics
        total_classes = 0
        total_functions = 0
        total_loc = 0
        public_classes: list[str] = []
        public_functions: list[str] = []

        for pyf in py_files:
            try:
                content = pyf.read_text(errors="replace")
            except (OSError, UnicodeDecodeError):
                continue

            # Count non-blank lines
            total_loc += sum(1 for line in content.splitlines() if line.strip())

            for line in content.splitlines():
                # Top-level class
                match = re.match(r"^class\s+(\w+)", line)
                if match:
                    total_classes += 1
                    name = match.group(1)
                    if not name.startswith("_"):
                        public_classes.append(name)

                # Top-level function
                match = re.match(r"^def\s+(\w+)", line)
                if match:
                    total_functions += 1
                    name = match.group(1)
                    if not name.startswith("_"):
                        public_functions.append(name)

        # Check __all__
        init_file = entry / "__init__.py"
        has_all = False
        if init_file.exists():
            try:
                init_content = init_file.read_text(errors="replace")
                has_all = "__all__" in init_content
            except (OSError, UnicodeDecodeError):
                pass

        # Check for matching test directory
        has_tests = entry.name in test_dirs

        packages.append({
            "name": entry.name,
            "path": str(entry),
            "modules": len(py_files),
            "classes": total_classes,
            "functions": total_functions,
            "loc": total_loc,
            "public_classes": sorted(set(public_classes)),
            "public_functions": sorted(set(public_functions)),
            "has_all": has_all,
            "has_tests": has_tests,
        })

    return packages


def build_dependency_graph(
    repo_path: Path,
    packages: list[dict[str, Any]],
) -> dict[str, set[str]]:
    """Build inter-package import dependency graph.

    Scans all .py files for import statements referencing sibling packages.
    Returns dict mapping source package -> set of target packages.
    Only includes edges between known packages (no stdlib/third-party).
    """
    repo_path = Path(repo_path).resolve()
    search_root = _find_package_root(repo_path)
    namespace = _detect_namespace_package(repo_path)

    pkg_names = {p["name"] for p in packages}
    graph: dict[str, set[str]] = defaultdict(set)

    for pkg in packages:
        pkg_path = Path(pkg["path"])
        py_files = [
            f for f in pkg_path.rglob("*.py")
            if "__pycache__" not in str(f)
        ]

        for pyf in py_files:
            try:
                content = pyf.read_text(errors="replace")
            except (OSError, UnicodeDecodeError):
                continue

            for line in content.splitlines():
                line_stripped = line.strip()

                # Match: from namespace.package... import ...
                # Match: import namespace.package...
                # Match: from .package import ... (relative)
                targets = set()

                if namespace:
                    # Absolute imports: from namespace.pkg or import namespace.pkg
                    pattern = rf"(?:from|import)\s+{re.escape(namespace)}\.(\w+)"
                    for m in re.finditer(pattern, line_stripped):
                        target = m.group(1)
                        if target in pkg_names and target != pkg["name"]:
                            targets.add(target)

                # Relative imports: from .pkg import ...
                rel_pattern = r"from\s+\.(\w+)"
                for m in re.finditer(rel_pattern, line_stripped):
                    target = m.group(1)
                    if target in pkg_names and target != pkg["name"]:
                        targets.add(target)

                graph[pkg["name"]].update(targets)

    # Convert defaultdict to regular dict, remove empty entries
    return {k: v for k, v in graph.items() if v}


def generate_yaml_report(
    packages: list[dict[str, Any]],
    graph: dict[str, set[str]],
) -> str:
    """Generate a structured YAML report."""
    total_modules = sum(p["modules"] for p in packages)
    total_classes = sum(p["classes"] for p in packages)
    total_functions = sum(p["functions"] for p in packages)
    total_loc = sum(p["loc"] for p in packages)
    total_public_classes = sum(len(p["public_classes"]) for p in packages)
    total_public_functions = sum(len(p["public_functions"]) for p in packages)

    data = {
        "summary": {
            "total_packages": len(packages),
            "total_modules": total_modules,
            "total_classes": total_classes,
            "total_functions": total_functions,
            "total_loc": total_loc,
            "public_api_classes": total_public_classes,
            "public_api_functions": total_public_functions,
        },
        "packages": [
            {
                "name": p["name"],
                "modules": p["modules"],
                "classes": p["classes"],
                "functions": p["functions"],
                "loc": p["loc"],
                "public_classes": p["public_classes"],
                "public_functions": p["public_functions"],
                "has_all": p["has_all"],
                "has_tests": p["has_tests"],
            }
            for p in sorted(packages, key=lambda x: x["name"])
        ],
        "dependency_graph": {
            k: sorted(v) for k, v in sorted(graph.items())
        },
    }

    return yaml.dump(data, default_flow_style=False, sort_keys=False, width=120)


def generate_markdown(
    repo_name: str,
    packages: list[dict[str, Any]],
    graph: dict[str, set[str]],
) -> str:
    """Generate API surface map markdown report with Mermaid dependency graph."""
    lines: list[str] = []

    # Header
    lines.append(f"# API Surface Map: {repo_name}")
    lines.append("")
    lines.append("Auto-generated by `architecture-scanner.py`.")
    lines.append("")

    # Summary
    total_modules = sum(p["modules"] for p in packages)
    total_classes = sum(p["classes"] for p in packages)
    total_functions = sum(p["functions"] for p in packages)
    total_loc = sum(p["loc"] for p in packages)
    total_pub_classes = sum(len(p["public_classes"]) for p in packages)
    total_pub_functions = sum(len(p["public_functions"]) for p in packages)
    tested = sum(1 for p in packages if p["has_tests"])

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Packages**: {len(packages)}")
    lines.append(f"- **Total modules**: {total_modules}")
    lines.append(f"- **Total classes**: {total_classes} ({total_pub_classes} public)")
    lines.append(f"- **Total functions**: {total_functions} ({total_pub_functions} public)")
    lines.append(f"- **Total LOC** (non-blank): {total_loc:,}")
    lines.append(f"- **Packages with tests**: {tested}/{len(packages)}")
    lines.append("")

    # Package listing table
    lines.append("## Package Listing")
    lines.append("")
    lines.append(
        "| Package | Modules | Classes | Functions | LOC | "
        "Public API | Has `__all__` | Tests |"
    )
    lines.append(
        "|---------|--------:|--------:|----------:|----:|"
        "----------:|:-------------:|:-----:|"
    )
    for pkg in sorted(packages, key=lambda p: p["name"]):
        pub_count = len(pkg["public_classes"]) + len(pkg["public_functions"])
        all_mark = "✓" if pkg["has_all"] else "✗"
        test_mark = "✓" if pkg["has_tests"] else "✗"
        lines.append(
            f"| {pkg['name']} | {pkg['modules']} | {pkg['classes']} | "
            f"{pkg['functions']} | {pkg['loc']:,} | {pub_count} | "
            f"{all_mark} | {test_mark} |"
        )
    lines.append("")

    # Top 10 largest by LOC
    lines.append("## Top 10 Largest Packages (by LOC)")
    lines.append("")
    sorted_by_loc = sorted(packages, key=lambda p: p["loc"], reverse=True)[:10]
    for i, pkg in enumerate(sorted_by_loc, 1):
        lines.append(
            f"{i}. **{pkg['name']}** — {pkg['loc']:,} LOC, "
            f"{pkg['modules']} modules, {pkg['classes']} classes, "
            f"{pkg['functions']} functions"
        )
    lines.append("")

    # Public API surface detail
    lines.append("## Public API Surface")
    lines.append("")
    for pkg in sorted(packages, key=lambda p: p["name"]):
        if not pkg["public_classes"] and not pkg["public_functions"]:
            continue
        lines.append(f"### {pkg['name']}")
        lines.append("")
        if pkg["public_classes"]:
            lines.append(f"**Classes**: {', '.join(pkg['public_classes'])}")
        if pkg["public_functions"]:
            lines.append(f"**Functions**: {', '.join(pkg['public_functions'])}")
        lines.append("")

    # Dependency graph — Mermaid
    lines.append("## Import Dependency Graph")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")

    # Add all packages as nodes
    for pkg in sorted(packages, key=lambda p: p["name"]):
        safe_name = pkg["name"].replace("-", "_")
        label = f"{pkg['name']}"
        lines.append(f"    {safe_name}[\"{label}\"]")
        if pkg["has_tests"]:
            lines.append(f"    style {safe_name} fill:#4CAF50,color:#fff")

    # Add dependency edges
    for source, targets in sorted(graph.items()):
        safe_source = source.replace("-", "_")
        for target in sorted(targets):
            safe_target = target.replace("-", "_")
            lines.append(f"    {safe_source} --> {safe_target}")

    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def build_reverse_index(
    packages: list[dict[str, Any]],
) -> dict[str, list[str]]:
    """Build a reverse index: symbol_name → list of package names exporting it.

    Combines public_classes and public_functions.  Deduplicates so each
    package appears at most once per symbol.
    """
    index: dict[str, list[str]] = defaultdict(list)
    for pkg in packages:
        seen_symbols: set[str] = set()
        for symbol in pkg.get("public_classes", []) + pkg.get("public_functions", []):
            if symbol not in seen_symbols:
                seen_symbols.add(symbol)
                index[symbol].append(pkg["name"])
    return dict(index)


def detect_collisions(
    packages: list[dict[str, Any]],
) -> dict[str, list[str]]:
    """Detect cross-package API name collisions.

    Returns a dict of symbol_name → list of packages that export it,
    filtered to only symbols exported by 2+ packages.
    """
    index = build_reverse_index(packages)
    return {
        symbol: pkgs
        for symbol, pkgs in index.items()
        if len(pkgs) >= 2
    }


def generate_collision_report(
    packages: list[dict[str, Any]],
    top_n: int = 20,
) -> str:
    """Generate a markdown section reporting cross-package API name collisions.

    Returns a markdown string with collision details.
    """
    collisions = detect_collisions(packages)
    lines: list[str] = []

    lines.append("## Cross-Package API Name Collisions")
    lines.append("")

    if not collisions:
        lines.append("No cross-package API name collisions detected.")
        lines.append("")
        return "\n".join(lines)

    total_collisions = len(collisions)
    lines.append(
        f"**{total_collisions} symbols** are exported by 2+ packages."
    )
    lines.append("")

    # Sort by number of packages (descending), then alphabetically
    sorted_collisions = sorted(
        collisions.items(),
        key=lambda x: (-len(x[1]), x[0]),
    )

    # Top-N table
    display = sorted_collisions[:top_n]
    lines.append(f"### Top {min(top_n, len(display))} Most Common Collisions")
    lines.append("")
    lines.append("| Symbol | Packages | Count |")
    lines.append("|--------|----------|------:|")
    for symbol, pkgs in display:
        pkg_list = ", ".join(sorted(pkgs))
        lines.append(f"| `{symbol}` | {pkg_list} | {len(pkgs)} |")
    lines.append("")

    if len(sorted_collisions) > top_n:
        lines.append(
            f"*... and {len(sorted_collisions) - top_n} more colliding symbols.*"
        )
        lines.append("")

    return "\n".join(lines)


def scan_repo(
    repo_path: Path,
    output_dir: Path | None = None,
    detect_collisions_flag: bool = False,
) -> str:
    """Full pipeline: discover packages, build graph, generate reports."""
    repo_path = Path(repo_path).resolve()
    repo_name = repo_path.name

    packages = discover_packages(repo_path)
    graph = build_dependency_graph(repo_path, packages)

    md = generate_markdown(repo_name, packages, graph)
    yaml_str = generate_yaml_report(packages, graph)

    # Collision detection
    collision_md = ""
    if detect_collisions_flag:
        collision_md = generate_collision_report(packages)
        md = md.rstrip("\n") + "\n\n" + collision_md

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        md_file = output_dir / "api-surface-map.md"
        md_file.write_text(md)
        print(f"Written: {md_file}")

        yaml_file = output_dir / "api-surface-map.yaml"
        yaml_file.write_text(yaml_str)
        print(f"Written: {yaml_file}")

    # Print summary
    print(f"\nScan complete: {len(packages)} packages")
    total_loc = sum(p["loc"] for p in packages)
    total_pub = sum(
        len(p["public_classes"]) + len(p["public_functions"]) for p in packages
    )
    dep_edges = sum(len(v) for v in graph.values())
    print(f"Total LOC: {total_loc:,}")
    print(f"Public API surface: {total_pub} symbols")
    print(f"Dependency edges: {dep_edges}")

    if detect_collisions_flag:
        collisions = detect_collisions(packages)
        print(f"API name collisions: {len(collisions)} symbols in 2+ packages")
        sorted_collisions = sorted(
            collisions.items(),
            key=lambda x: (-len(x[1]), x[0]),
        )
        for symbol, pkgs in sorted_collisions[:20]:
            print(f"  {symbol}: {', '.join(sorted(pkgs))}")

    return md


def main():
    parser = argparse.ArgumentParser(
        description="Architecture scanner: API surface + import dependency graph"
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default="digitalmodel/",
        help="Path to the repository to scan (default: digitalmodel/)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="Output directory for reports (default: docs/architecture)",
    )
    parser.add_argument(
        "--detect-collisions",
        action="store_true",
        default=False,
        help="Detect and report cross-package API name collisions",
    )
    args = parser.parse_args()

    repo = Path(args.repo_path)
    if not repo.is_dir():
        print(f"Error: {repo} is not a directory", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else Path("docs/architecture")
    scan_repo(repo, output_dir, detect_collisions_flag=args.detect_collisions)


if __name__ == "__main__":
    main()
