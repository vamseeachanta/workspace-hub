#!/usr/bin/env python3
"""Per-repo code architecture scanner.

Discovers Python packages in a repository, counts classes/functions,
detects test coverage, and generates an architecture markdown report
with a Mermaid diagram.

Usage:
    uv run scripts/analysis/repo_architecture_scanner.py [REPO_PATH]

Defaults to digitalmodel/ if no path given.
Outputs to docs/architecture/{repo-name}-architecture.md

Related: GitHub issue #1569
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any


def discover_packages(repo_path: Path) -> list[dict[str, Any]]:
    """Discover all top-level Python packages in a repo.

    Looks for packages under src/ first (PEP 621 layout).
    Falls back to repo root if no src/ directory exists.

    Returns a list of dicts with keys:
        name, path, py_files, classes, functions, has_all, has_tests
    """
    repo_path = Path(repo_path)

    # Determine where packages live
    src_dir = repo_path / "src"
    if src_dir.is_dir():
        # In src layout, look one level deeper if there's a single namespace package
        subdirs = [d for d in src_dir.iterdir()
                   if d.is_dir()
                   and not d.name.startswith((".", "_"))
                   and not d.name.endswith((".egg-info", ".dist-info"))]
        if len(subdirs) == 1 and (subdirs[0] / "__init__.py").exists():
            # Single namespace package — scan its children as the top-level packages
            search_root = subdirs[0]
        else:
            search_root = src_dir
    else:
        search_root = repo_path

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

        # Count .py files
        py_files = list(entry.rglob("*.py"))
        py_file_count = len(py_files)

        # Count top-level classes and functions (lines starting with 'class ' or 'def ')
        class_count = 0
        func_count = 0
        for pyf in py_files:
            try:
                content = pyf.read_text(errors="replace")
            except (OSError, UnicodeDecodeError):
                continue
            for line in content.splitlines():
                if re.match(r"^class\s", line):
                    class_count += 1
                if re.match(r"^def\s", line):
                    func_count += 1

        # Check if __init__.py exports __all__
        init_file = entry / "__init__.py"
        has_all = False
        if init_file.exists():
            try:
                init_content = init_file.read_text(errors="replace")
                has_all = "__all__" in init_content
            except (OSError, UnicodeDecodeError):
                pass

        # Check for matching tests directory
        has_tests = entry.name in test_dirs

        packages.append({
            "name": entry.name,
            "path": str(entry),
            "py_files": py_file_count,
            "classes": class_count,
            "functions": func_count,
            "has_all": has_all,
            "has_tests": has_tests,
        })

    return packages


def find_entry_points(repo_path: Path) -> list[str]:
    """Find entry points: __main__.py files, scripts/*.py, CLI commands."""
    repo_path = Path(repo_path)
    entry_points = []

    # Directories to skip
    skip_dirs = {".venv", "venv", "node_modules", ".git", "__pycache__", ".tox", ".nox"}

    def _skip_venv(path: Path) -> bool:
        return any(part in skip_dirs for part in path.parts)

    # Find all __main__.py (excluding virtualenvs)
    for main_file in repo_path.rglob("__main__.py"):
        if not _skip_venv(main_file):
            try:
                entry_points.append(str(main_file.relative_to(repo_path)))
            except ValueError:
                entry_points.append(str(main_file))

    # Find scripts/*.py (top-level only, skip deep legacy trees)
    scripts_dir = repo_path / "scripts"
    if scripts_dir.is_dir():
        for script in sorted(scripts_dir.glob("*.py")):
            if not _skip_venv(script):
                try:
                    entry_points.append(str(script.relative_to(repo_path)))
                except ValueError:
                    entry_points.append(str(script))

    # Check pyproject.toml for [project.scripts]
    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(errors="replace")
            if "[project.scripts]" in content:
                entry_points.append(f"{pyproject} [project.scripts]")
        except (OSError, UnicodeDecodeError):
            pass

    return sorted(set(entry_points))


def generate_markdown(
    repo_name: str,
    packages: list[dict[str, Any]],
    entry_points: list[str],
    cli_commands: list[str],
) -> str:
    """Generate architecture markdown report.

    Includes:
      - Package listing table
      - Top 10 largest packages by file count
      - Entry points
      - Mermaid diagram of package structure
    """
    lines: list[str] = []

    # Header
    lines.append(f"# Architecture Report: {repo_name}")
    lines.append("")
    lines.append(f"Auto-generated by `repo-architecture-scanner.py`.")
    lines.append("")

    # Summary
    total_files = sum(p["py_files"] for p in packages)
    total_classes = sum(p["classes"] for p in packages)
    total_functions = sum(p["functions"] for p in packages)
    tested = sum(1 for p in packages if p["has_tests"])
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Packages**: {len(packages)}")
    lines.append(f"- **Total .py files**: {total_files}")
    lines.append(f"- **Total classes**: {total_classes}")
    lines.append(f"- **Total functions**: {total_functions}")
    lines.append(f"- **Packages with tests**: {tested}/{len(packages)}")
    lines.append("")

    # Package listing table
    lines.append("## Package Listing")
    lines.append("")
    lines.append("| Package | Files | Classes | Functions | Has `__all__` | Has Tests |")
    lines.append("|---------|------:|--------:|----------:|:-------------:|:---------:|")
    for pkg in sorted(packages, key=lambda p: p["name"]):
        all_mark = "✓" if pkg["has_all"] else "✗"
        test_mark = "✓" if pkg["has_tests"] else "✗"
        lines.append(
            f"| {pkg['name']} | {pkg['py_files']} | {pkg['classes']} | "
            f"{pkg['functions']} | {all_mark} | {test_mark} |"
        )
    lines.append("")

    # Top 10 largest packages
    lines.append("## Top 10 Largest Packages (by file count)")
    lines.append("")
    sorted_by_files = sorted(packages, key=lambda p: p["py_files"], reverse=True)[:10]
    for i, pkg in enumerate(sorted_by_files, 1):
        lines.append(f"{i}. **{pkg['name']}** — {pkg['py_files']} files, "
                     f"{pkg['classes']} classes, {pkg['functions']} functions")
    lines.append("")

    # Entry points
    lines.append("## Entry Points")
    lines.append("")
    if entry_points:
        for ep in entry_points:
            lines.append(f"- `{ep}`")
    else:
        lines.append("_No entry points discovered._")
    if cli_commands:
        lines.append("")
        lines.append("### CLI Commands")
        for cmd in cli_commands:
            lines.append(f"- `{cmd}`")
    lines.append("")

    # Mermaid diagram
    lines.append("## Package Structure")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph TD")
    lines.append(f"    ROOT[{repo_name}]")
    for pkg in sorted(packages, key=lambda p: p["name"]):
        safe_name = pkg["name"].replace("-", "_")
        label = f"{pkg['name']}<br/>{pkg['py_files']} files"
        lines.append(f"    ROOT --> {safe_name}[\"{label}\"]")
        if pkg["has_tests"]:
            lines.append(f"    style {safe_name} fill:#4CAF50,color:#fff")
        elif pkg["py_files"] <= 1:
            lines.append(f"    style {safe_name} fill:#FF9800,color:#fff")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def scan_repo(repo_path: Path, output_dir: Path | None = None) -> str:
    """Full pipeline: discover packages, find entry points, generate report."""
    repo_path = Path(repo_path).resolve()
    repo_name = repo_path.name

    packages = discover_packages(repo_path)
    entry_points = find_entry_points(repo_path)

    # Extract CLI commands from pyproject.toml if present
    cli_commands: list[str] = []
    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(errors="replace")
            in_scripts = False
            for line in content.splitlines():
                if line.strip() == "[project.scripts]":
                    in_scripts = True
                    continue
                if in_scripts:
                    if line.strip().startswith("["):
                        break
                    if "=" in line:
                        cmd_name = line.split("=")[0].strip()
                        if cmd_name:
                            cli_commands.append(cmd_name)
        except (OSError, UnicodeDecodeError):
            pass

    md = generate_markdown(repo_name, packages, entry_points, cli_commands)

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        out_file = output_dir / f"{repo_name}-architecture.md"
        out_file.write_text(md)
        print(f"Written: {out_file}")

    return md


def main():
    parser = argparse.ArgumentParser(description="Per-repo code architecture scanner")
    parser.add_argument("repo_path", nargs="?", default="digitalmodel/",
                        help="Path to the repository to scan (default: digitalmodel/)")
    parser.add_argument("-o", "--output-dir", default=None,
                        help="Output directory for the markdown report")
    args = parser.parse_args()

    repo = Path(args.repo_path)
    if not repo.is_dir():
        print(f"Error: {repo} is not a directory", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else Path("docs/architecture")
    scan_repo(repo, output_dir)


if __name__ == "__main__":
    main()
