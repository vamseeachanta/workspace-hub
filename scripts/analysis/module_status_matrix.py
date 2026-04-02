#!/usr/bin/env python3
"""Cross-repo module status matrix.

Scans digitalmodel/src/digitalmodel/ top-level packages and classifies each
by maturity: PRODUCTION, DEVELOPMENT, SKELETON, or GAP.

Outputs:
  - docs/reports/module-status-matrix.md  -- human-readable table
  - docs/reports/module-status-matrix.json -- structured data

Usage:
    uv run scripts/analysis/module_status_matrix.py [REPO_PATH]

Defaults to digitalmodel/ if no path given.

Related: GitHub issue #1570
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _count_test_files(repo_path: Path, package_name: str) -> int:
    """Count test files for a given package name."""
    tests_root = repo_path / "tests" / package_name
    if not tests_root.is_dir():
        return 0
    return len(list(tests_root.rglob("test_*.py"))) + len(
        list(tests_root.rglob("*_test.py"))
    )


def _has_docstring(filepath: Path) -> bool:
    """Check if a Python file has a module-level docstring."""
    try:
        content = filepath.read_text(errors="replace").strip()
    except (OSError, UnicodeDecodeError):
        return False
    if not content:
        return False
    return bool(re.match(r'^(\'\'\'|"""|\'|")', content))


def _count_lines(filepath: Path) -> int:
    """Count non-blank lines in a file."""
    try:
        content = filepath.read_text(errors="replace")
    except (OSError, UnicodeDecodeError):
        return 0
    return sum(1 for line in content.splitlines() if line.strip())


def _extract_classes(filepath: Path) -> list[str]:
    """Extract top-level class names from a Python file."""
    classes = []
    try:
        content = filepath.read_text(errors="replace")
    except (OSError, UnicodeDecodeError):
        return classes
    for line in content.splitlines():
        match = re.match(r"^class\s+(\w+)", line)
        if match:
            classes.append(match.group(1))
    return classes


def _classify_maturity(
    file_count: int,
    test_count: int,
    docstring_pct: int,
    all_files_tiny: bool,
    only_init: bool,
) -> str:
    """Classify package maturity based on metrics.

    Rules (evaluated top-down):
      GAP:         directory exists but empty or only __init__.py
      PRODUCTION:  >5 test files AND >3 source files AND docstrings >50%
      DEVELOPMENT: has source files AND some tests (1-5 test files)
      SKELETON:    has source files but 0 test files OR all files <20 lines
    """
    if only_init:
        return "GAP"

    if test_count > 5 and file_count > 3 and docstring_pct > 50:
        return "PRODUCTION"

    if test_count >= 1 and not all_files_tiny:
        return "DEVELOPMENT"

    return "SKELETON"


def scan_packages(repo_path: Path) -> list[dict[str, Any]]:
    """Scan top-level packages under src/digitalmodel/ and classify maturity.

    Returns a list of dicts with keys:
        name, status, file_count, test_count, key_classes, docstring_pct
    """
    repo_path = Path(repo_path).resolve()

    # Find the package root
    src_dir = repo_path / "src"
    if src_dir.is_dir():
        subdirs = [
            d for d in src_dir.iterdir()
            if d.is_dir()
            and not d.name.startswith((".", "_"))
            and not d.name.endswith((".egg-info", ".dist-info"))
        ]
        if len(subdirs) == 1 and (subdirs[0] / "__init__.py").exists():
            search_root = subdirs[0]
        else:
            search_root = src_dir
    else:
        search_root = repo_path

    packages = []
    for entry in sorted(search_root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith((".", "_")):
            continue
        if not (entry / "__init__.py").exists():
            continue

        py_files = [
            f for f in entry.rglob("*.py")
            if "__pycache__" not in str(f)
        ]
        file_count = len(py_files)

        test_count = _count_test_files(repo_path, entry.name)

        if py_files:
            with_docstring = sum(1 for f in py_files if _has_docstring(f))
            docstring_pct = round(100 * with_docstring / len(py_files))
        else:
            docstring_pct = 0

        non_init_files = [f for f in py_files if f.name != "__init__.py"]
        only_init = len(non_init_files) == 0

        all_files_tiny = all(
            _count_lines(f) < 20 for f in py_files
        ) if py_files else True

        all_classes = []
        for f in py_files:
            all_classes.extend(_extract_classes(f))

        status = _classify_maturity(
            file_count, test_count, docstring_pct, all_files_tiny, only_init,
        )

        packages.append({
            "name": entry.name,
            "status": status,
            "file_count": file_count,
            "test_count": test_count,
            "key_classes": sorted(set(all_classes)),
            "docstring_pct": docstring_pct,
        })

    return packages


def _status_emoji(status: str) -> str:
    """Return emoji for status."""
    return {
        "PRODUCTION": "\U0001f7e2",
        "DEVELOPMENT": "\U0001f7e1",
        "SKELETON": "\U0001f7e0",
        "GAP": "\U0001f534",
    }.get(status, "\u26aa")


def generate_markdown(packages: list[dict[str, Any]]) -> str:
    """Generate the module status matrix markdown report."""
    lines: list[str] = []

    lines.append("# Module Status Matrix")
    lines.append("")
    lines.append("Auto-generated by `module_status_matrix.py`.")
    lines.append("")

    counts = Counter(p["status"] for p in packages)
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total packages**: {len(packages)}")
    for status in ["PRODUCTION", "DEVELOPMENT", "SKELETON", "GAP"]:
        emoji = _status_emoji(status)
        lines.append(f"- {emoji} **{counts.get(status, 0)} {status}**")
    lines.append("")

    lines.append("## Package Status Table")
    lines.append("")
    lines.append(
        "| Package | Status | Files | Tests | Docstring % | Key Classes |"
    )
    lines.append(
        "|---------|--------|------:|------:|------------:|-------------|"
    )
    for pkg in sorted(packages, key=lambda p: p["name"]):
        emoji = _status_emoji(pkg["status"])
        classes_str = ", ".join(pkg["key_classes"][:5])
        if len(pkg["key_classes"]) > 5:
            classes_str += f" (+{len(pkg['key_classes']) - 5} more)"
        lines.append(
            f"| {pkg['name']} | {emoji} {pkg['status']} | "
            f"{pkg['file_count']} | {pkg['test_count']} | "
            f"{pkg['docstring_pct']}% | {classes_str} |"
        )
    lines.append("")

    gaps = [
        p for p in packages if p["status"] in ("SKELETON", "GAP")
    ]
    gaps_sorted = sorted(gaps, key=lambda p: p["file_count"], reverse=True)[:5]

    if gaps_sorted:
        lines.append("## Top 5 Gaps (largest SKELETON/GAP packages)")
        lines.append("")
        for i, pkg in enumerate(gaps_sorted, 1):
            emoji = _status_emoji(pkg["status"])
            lines.append(
                f"{i}. {emoji} **{pkg['name']}** -- "
                f"{pkg['file_count']} files, {pkg['test_count']} tests, "
                f"{pkg['status']}"
            )
        lines.append("")

    return "\n".join(lines)


def generate_json_output(packages: list[dict[str, Any]]) -> str:
    """Generate structured JSON output."""
    counts = Counter(p["status"] for p in packages)
    data = {
        "packages": sorted(packages, key=lambda p: p["name"]),
        "summary": {
            "total": len(packages),
            "PRODUCTION": counts.get("PRODUCTION", 0),
            "DEVELOPMENT": counts.get("DEVELOPMENT", 0),
            "SKELETON": counts.get("SKELETON", 0),
            "GAP": counts.get("GAP", 0),
        },
    }
    return json.dumps(data, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser(
        description="Cross-repo module status matrix"
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
        help="Output directory for reports",
    )
    args = parser.parse_args()

    repo = Path(args.repo_path)
    if not repo.is_dir():
        print(f"Error: {repo} is not a directory", file=sys.stderr)
        sys.exit(1)

    packages = scan_packages(repo)
    output_dir = Path(args.output_dir) if args.output_dir else Path("docs/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    md = generate_markdown(packages)
    md_file = output_dir / "module-status-matrix.md"
    md_file.write_text(md)
    print(f"Written: {md_file}")

    json_str = generate_json_output(packages)
    json_file = output_dir / "module-status-matrix.json"
    json_file.write_text(json_str)
    print(f"Written: {json_file}")

    counts = Counter(p["status"] for p in packages)
    print(f"\nSummary: {len(packages)} packages -- "
          f"{counts.get('PRODUCTION', 0)} production, "
          f"{counts.get('DEVELOPMENT', 0)} development, "
          f"{counts.get('SKELETON', 0)} skeleton, "
          f"{counts.get('GAP', 0)} gap")


if __name__ == "__main__":
    main()
