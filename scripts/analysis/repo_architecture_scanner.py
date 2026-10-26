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
import ast
import re
import sys
from pathlib import Path
from typing import Any


def _python_files(root: Path):
    """Yield sorted source paths without following links or nested checkouts."""
    if root.is_symlink():
        return
    for path in sorted(root.iterdir()):
        if path.is_symlink():
            continue
        if path.is_dir():
            if path.name != ".git" and not (path / ".git").exists():
                yield from _python_files(path)
        elif path.suffix == ".py":
            yield path


def _export_references(node: ast.AST):
    """Find module-scope uses/bindings of __all__, without executing code."""
    if isinstance(node, ast.Name) and node.id == "__all__":
        yield node
    elif isinstance(node, ast.alias) and (node.asname or node.name) == "__all__":
        yield node
    scoped = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    if scoped and node.name == "__all__":
        yield node
    if scoped and any(
        (isinstance(child, ast.Name) and child.id == "__all__"
         and isinstance(child.ctx, ast.Load))
        or (isinstance(child, ast.Global) and "__all__" in child.names)
        for child in ast.walk(node)
    ):
        # Deferred reads or global updates may mutate module exports. Without
        # evaluating calls, even a possibly shadowed read is unresolved.
        yield node
    for field, value in ast.iter_fields(node):
        # Function and class bodies have their own namespace. Decorators,
        # defaults, annotations and bases can still reference module exports.
        if scoped and field == "body":
            continue
        children = value if isinstance(value, list) else [value]
        for child in children:
            if isinstance(child, ast.AST):
                yield from _export_references(child)


def _public_api(content: str, path: str) -> dict[str, Any]:
    """Describe static exports; unknown exports are distinct from an empty API.

    Literal lists/tuples implement the __all__ name-selection rule documented at
    https://docs.python.org/3/reference/simple_stmts.html#the-import-statement
    The fallback intentionally lists only module-level function/class definitions,
    not all runtime bindings. Dynamic expressions and mutations are not evaluated.
    """
    result = {"path": path, "exports": None, "status": "unresolved", "reason": None}
    try:
        tree = ast.parse(content)
    except (SyntaxError, ValueError):
        result["reason"] = "syntax error"
        return result

    literal_targets = set()
    exports = None
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            targets = statement.targets
        elif isinstance(statement, ast.AnnAssign):
            targets = [statement.target]
        else:
            continue
        # A shared assignment could expose an alias which mutates the sequence.
        target, *other_targets = targets
        if other_targets or not isinstance(target, ast.Name) or target.id != "__all__":
            continue
        value = statement.value
        if isinstance(value, (ast.List, ast.Tuple)) and all(
            isinstance(item, ast.Constant) and isinstance(item.value, str)
            for item in value.elts
        ):
            literal_targets.add(target)
            exports = sorted({item.value for item in value.elts})

    if any(reference not in literal_targets for reference in _export_references(tree)):
        result["reason"] = "dynamic __all__"
        return result
    if exports is not None:
        result.update(exports=exports, status="literal")
    else:
        definitions = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        result.update(
            exports=sorted({node.name for node in tree.body
                            if isinstance(node, definitions) and not node.name.startswith("_")}),
            status="default",
        )
    return result


def discover_packages(repo_path: Path) -> list[dict[str, Any]]:
    """Discover all top-level Python packages in a repo.

    Looks for packages under src/ first (PEP 621 layout).
    Falls back to repo root if no src/ directory exists.

    Returns a list of dicts with keys:
        name, path, py_files, classes, functions, has_all, has_tests, api
    api contains per-module relative paths, sorted exports, status and reason.
    """
    repo_path = Path(repo_path)

    # Determine where packages live
    src_dir = repo_path / "src"
    if src_dir.is_symlink() or (src_dir / ".git").exists():
        return []
    if src_dir.is_dir():
        # In src layout, look one level deeper if there's a single namespace package
        subdirs = [d for d in src_dir.iterdir()
                   if d.is_dir()
                   and not d.is_symlink()
                   and not (d / ".git").exists()
                   and not d.name.startswith((".", "_"))
                   and not d.name.endswith((".egg-info", ".dist-info"))]
        if (len(subdirs) == 1 and (subdirs[0] / "__init__.py").exists()
                and not (subdirs[0] / "__init__.py").is_symlink()):
            # Single namespace package — scan its children as the top-level packages
            search_root = subdirs[0]
        else:
            search_root = src_dir
    else:
        search_root = repo_path

    # Find test directories
    tests_root = repo_path / "tests"
    test_dirs = set()
    if (tests_root.is_dir() and not tests_root.is_symlink()
            and not (tests_root / ".git").exists()):
        for d in tests_root.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                test_dirs.add(d.name)

    packages = []
    for entry in sorted(search_root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.is_symlink() or (entry / ".git").exists():
            continue
        if entry.name.startswith((".", "_")):
            continue
        if not (entry / "__init__.py").exists() or (entry / "__init__.py").is_symlink():
            continue

        # Count .py files
        py_files = list(_python_files(entry))
        py_file_count = len(py_files)

        # Count top-level classes and functions (lines starting with 'class ' or 'def ')
        class_count = 0
        func_count = 0
        api = []
        for pyf in py_files:
            relative_path = pyf.relative_to(repo_path).as_posix()
            try:
                content = pyf.read_text(errors="replace")
            except (OSError, UnicodeDecodeError):
                api.append({"path": relative_path, "exports": None,
                            "status": "unresolved", "reason": "unreadable source"})
                continue
            api.append(_public_api(content, relative_path))
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
            "api": sorted(api, key=lambda module: module["path"]),
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
    for main_file in _python_files(repo_path):
        if main_file.name != "__main__.py":
            continue
        if not _skip_venv(main_file):
            try:
                entry_points.append(str(main_file.relative_to(repo_path)))
            except ValueError:
                entry_points.append(str(main_file))

    # Find scripts/*.py (top-level only, skip deep legacy trees)
    scripts_dir = repo_path / "scripts"
    if (scripts_dir.is_dir() and not scripts_dir.is_symlink()
            and not (scripts_dir / ".git").exists()):
        for script in sorted(scripts_dir.glob("*.py")):
            if not script.is_symlink() and not _skip_venv(script):
                try:
                    entry_points.append(str(script.relative_to(repo_path)))
                except ValueError:
                    entry_points.append(str(script))

    # Check pyproject.toml for [project.scripts]
    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists() and not pyproject.is_symlink():
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

    lines.append("## Public API")
    lines.append("")
    lines.append("Static names per module: literal `__all__` takes precedence; otherwise "
                 "only public top-level functions and classes are listed. "
                 "Dynamic exports are unresolved; scanned code is never imported.")
    lines.append("")
    for pkg in sorted(packages, key=lambda p: p["name"]):
        for module in sorted(pkg.get("api", []), key=lambda item: item["path"]):
            if module["status"] == "unresolved":
                detail = f"unresolved: {module['reason']}"
            else:
                detail = ", ".join(f"`{name}`" for name in module["exports"]) or "No exports"
                detail += f" ({module['status']})"
            lines.append(f"- `{module['path']}`: {detail}")
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
    if pyproject.exists() and not pyproject.is_symlink():
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
