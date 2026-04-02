#!/usr/bin/env python3
"""Cross-repo module status matrix.

Scans a Python package's top-level sub-packages and classifies maturity:
  PRODUCTION  — >5 test files AND >3 source files AND >50% files have docstrings
  DEVELOPMENT — source files AND 1-5 test files
  SKELETON    — source files but 0 test files OR all files <20 lines
  GAP         — directory exists but empty or only __init__.py

Outputs:
  - docs/reports/module-status-matrix.md  — human-readable table
  - docs/reports/module-status-matrix.json — structured data

Usage:
    uv run scripts/analysis/module_status_matrix.py [--src-dir PATH] [--tests-dir PATH]

Related: GitHub issue #1570
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _count_test_files(tests_dir: Path, package_name: str) -> int:
    """Count test files for a package in the tests directory."""
    pkg_test_dir = tests_dir / package_name
    if not pkg_test_dir.is_dir():
        return 0
    return len([f for f in pkg_test_dir.rglob("test_*.py")])


def _has_docstring(filepath: Path) -> bool:
    """Check if a Python file has a module-level docstring."""
    try:
        content = filepath.read_text(errors="replace").strip()
        if not content:
            return False
        # Module docstring: file starts with """ or '''
        return content.startswith(('"""', "'''", 'r"""', "r'''", 'u"""', "u'''"))
    except (OSError, UnicodeDecodeError):
        return False


def _count_lines(filepath: Path) -> int:
    """Count non-empty lines in a file."""
    try:
        return sum(1 for line in filepath.read_text(errors="replace").splitlines() if line.strip())
    except (OSError, UnicodeDecodeError):
        return 0


def _extract_classes(package_dir: Path) -> list[str]:
    """Extract class names from all .py files in a package."""
    classes = []
    for pyfile in sorted(package_dir.rglob("*.py")):
        try:
            for line in pyfile.read_text(errors="replace").splitlines():
                m = re.match(r"^class\s+(\w+)", line)
                if m:
                    classes.append(m.group(1))
        except (OSError, UnicodeDecodeError):
            continue
    return classes


def _classify_maturity(
    source_files: list[Path],
    test_count: int,
) -> str:
    """Classify a package's maturity level.

    Rules:
      PRODUCTION  — >5 test files AND >3 source files AND >50% files have docstrings
      DEVELOPMENT — source files AND 1-5 test files
      SKELETON    — source files but 0 test files OR all files <20 lines
      GAP         — only __init__.py or empty
    """
    # Exclude __init__.py from "real" source files for GAP detection
    real_files = [f for f in source_files if f.name != "__init__.py"]

    if not real_files:
        return "GAP"

    # Check if all files are tiny (<20 lines)
    all_tiny = all(_count_lines(f) < 20 for f in real_files)
    if all_tiny and test_count == 0:
        return "SKELETON"

    # PRODUCTION: >5 test files AND >3 source files AND >50% docstrings
    if test_count > 5 and len(real_files) > 3:
        docstring_count = sum(1 for f in source_files if _has_docstring(f))
        docstring_pct = docstring_count / len(source_files) if source_files else 0
        if docstring_pct > 0.5:
            return "PRODUCTION"

    # DEVELOPMENT: has source AND 1-5 test files
    if 1 <= test_count <= 5:
        return "DEVELOPMENT"

    # If >5 tests but didn't meet PRODUCTION criteria, still DEVELOPMENT
    if test_count > 5:
        return "DEVELOPMENT"

    # SKELETON: 0 test files
    if test_count == 0:
        return "SKELETON"

    return "SKELETON"


def scan_packages(src_dir: Path, tests_dir: Path) -> list[dict[str, Any]]:
    """Scan top-level packages and classify maturity.

    Args:
        src_dir: Path to the source packages directory (e.g., digitalmodel/src/digitalmodel/)
        tests_dir: Path to the tests directory (e.g., digitalmodel/tests/)

    Returns:
        List of dicts with: package, status, file_count, test_count, key_classes
    """
    src_dir = Path(src_dir)
    tests_dir = Path(tests_dir)

    results = []
    for entry in sorted(src_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith((".", "_")):
            continue
        if not (entry / "__init__.py").exists():
            continue

        # Source files
        source_files = list(entry.rglob("*.py"))
        file_count = len(source_files)

        # Test files
        test_count = _count_test_files(tests_dir, entry.name)

        # Key classes
        key_classes = _extract_classes(entry)

        # Classify
        status = _classify_maturity(source_files, test_count)

        results.append({
            "package": entry.name,
            "status": status,
            "file_count": file_count,
            "test_count": test_count,
            "key_classes": key_classes,
        })

    return results


def _status_emoji(status: str) -> str:
    """Return an emoji for the status."""
    return {
        "PRODUCTION": "🟢",
        "DEVELOPMENT": "🟡",
        "SKELETON": "🟠",
        "GAP": "🔴",
    }.get(status, "⚪")


def generate_markdown(packages: list[dict[str, Any]]) -> str:
    """Generate the module status matrix markdown report."""
    lines: list[str] = []

    lines.append("# Module Status Matrix")
    lines.append("")
    lines.append("Auto-generated by `module-status-matrix.py`.")
    lines.append("")

    # Summary
    counts = Counter(p["status"] for p in packages)
    total = len(packages)
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total packages**: {total}")
    lines.append(f"- 🟢 **PRODUCTION**: {counts.get('PRODUCTION', 0)}")
    lines.append(f"- 🟡 **DEVELOPMENT**: {counts.get('DEVELOPMENT', 0)}")
    lines.append(f"- 🟠 **SKELETON**: {counts.get('SKELETON', 0)}")
    lines.append(f"- 🔴 **GAP**: {counts.get('GAP', 0)}")
    lines.append("")

    # Table
    lines.append("## Package Matrix")
    lines.append("")
    lines.append("| Package | Status | Files | Tests | Key Classes |")
    lines.append("|---------|--------|------:|------:|-------------|")
    for pkg in sorted(packages, key=lambda p: p["package"]):
        emoji = _status_emoji(pkg["status"])
        classes_str = ", ".join(pkg["key_classes"][:5])
        if len(pkg["key_classes"]) > 5:
            classes_str += f" (+{len(pkg['key_classes']) - 5} more)"
        lines.append(
            f"| {pkg['package']} | {emoji} {pkg['status']} | "
            f"{pkg['file_count']} | {pkg['test_count']} | {classes_str} |"
        )
    lines.append("")

    # Top 5 gaps (largest packages with SKELETON or GAP status)
    gaps = [p for p in packages if p["status"] in ("SKELETON", "GAP")]
    gaps.sort(key=lambda p: p["file_count"], reverse=True)
    top_gaps = gaps[:5]

    if top_gaps:
        lines.append("## Top 5 Gaps (largest SKELETON/GAP packages)")
        lines.append("")
        for i, g in enumerate(top_gaps, 1):
            lines.append(
                f"{i}. **{g['package']}** — {_status_emoji(g['status'])} {g['status']}, "
                f"{g['file_count']} files, {g['test_count']} tests"
            )
        lines.append("")

    return "\n".join(lines)


def generate_json(packages: list[dict[str, Any]]) -> str:
    """Generate structured JSON output."""
    counts = Counter(p["status"] for p in packages)
    data = {
        "summary": {
            "total": len(packages),
            "PRODUCTION": counts.get("PRODUCTION", 0),
            "DEVELOPMENT": counts.get("DEVELOPMENT", 0),
            "SKELETON": counts.get("SKELETON", 0),
            "GAP": counts.get("GAP", 0),
        },
        "packages": sorted(packages, key=lambda p: p["package"]),
    }
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Cross-repo module status matrix")
    parser.add_argument("--src-dir", default="digitalmodel/src/digitalmodel",
                        help="Path to source packages directory")
    parser.add_argument("--tests-dir", default="digitalmodel/tests",
                        help="Path to tests directory")
    parser.add_argument("--output-dir", default="docs/reports",
                        help="Output directory for reports")
    args = parser.parse_args()

    src_dir = Path(args.src_dir)
    tests_dir = Path(args.tests_dir)
    output_dir = Path(args.output_dir)

    if not src_dir.is_dir():
        print(f"Error: {src_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    packages = scan_packages(src_dir, tests_dir)

    # Generate outputs
    output_dir.mkdir(parents=True, exist_ok=True)

    md = generate_markdown(packages)
    md_file = output_dir / "module-status-matrix.md"
    md_file.write_text(md)
    print(f"Written: {md_file}")

    json_str = generate_json(packages)
    json_file = output_dir / "module-status-matrix.json"
    json_file.write_text(json_str)
    print(f"Written: {json_file}")

    # Print summary
    counts = Counter(p["status"] for p in packages)
    print(f"\n  Summary: {counts.get('PRODUCTION', 0)} production, "
          f"{counts.get('DEVELOPMENT', 0)} development, "
          f"{counts.get('SKELETON', 0)} skeleton, "
          f"{counts.get('GAP', 0)} gap")


if __name__ == "__main__":
    main()
