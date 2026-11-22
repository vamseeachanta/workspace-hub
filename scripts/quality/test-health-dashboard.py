# ABOUTME: Cross-repo test health dashboard generator — #1573.
# ABOUTME: Runs pytest on digitalmodel/tests/, parses results per package,
# ABOUTME: generates docs/dashboards/test-health-dashboard.md with pass/fail
# ABOUTME: metrics, emoji status badges, and a zero-test gap list.
"""
Test Health Dashboard Generator

Runs pytest across digitalmodel/tests/ and produces a per-package
summary dashboard at docs/dashboards/test-health-dashboard.md.

Usage:
    uv run python scripts/quality/test-health-dashboard.py
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_pytest_summary(raw: str) -> dict[str, int]:
    """Parse a pytest short summary line into counts.

    Args:
        raw: A line like '10 passed, 2 failed, 1 skipped in 3.45s'

    Returns:
        Dict with keys: passed, failed, skipped, errors — all ints.
    """
    result = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
    if not raw.strip():
        return result
    for key in result:
        label = r"errors?" if key == "errors" else key
        match = re.search(rf"(\d+)\s+{label}\b", raw)
        if match:
            result[key] = int(match.group(1))
    return result


def aggregate_by_package(lines: list[str]) -> dict[str, dict[str, int]]:
    """Aggregate pytest verbose output lines by top-level test package.

    Args:
        lines: List of pytest output lines including:
               'digitalmodel/tests/reservoir/test_x.py::test_y PASSED'
               'ERROR digitalmodel/tests/fatigue/test_x.py'

    Returns:
        Dict mapping package name -> {passed, failed, skipped, errors, total}.
    """
    packages: dict[str, dict[str, int]] = {}

    # Pattern 1: verbose result lines — test_x.py::test_y PASSED
    result_pattern = re.compile(
        r"digitalmodel/tests/([^/]+)/.*\s+(PASSED|FAILED|SKIPPED|ERROR)"
    )
    # Pattern 2: short summary ERROR lines — ERROR digitalmodel/tests/<pkg>/...
    error_pattern = re.compile(
        r"^ERROR\s+digitalmodel/tests/([^/]+)/"
    )

    for line in lines:
        m = result_pattern.search(line)
        if m:
            pkg = m.group(1)
            status = m.group(2).lower()
        else:
            m = error_pattern.search(line)
            if m:
                pkg = m.group(1)
                status = "error"
            else:
                continue

        if pkg not in packages:
            packages[pkg] = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "total": 0}
        key = "errors" if status == "error" else status
        packages[pkg][key] += 1
        packages[pkg]["total"] += 1
    return packages


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_pass_rate(passed: int, total: int) -> float:
    """Compute pass rate as a percentage.

    Args:
        passed: Number of passed tests.
        total: Total number of tests.

    Returns:
        Pass rate 0.0-100.0. Returns 0.0 if total is 0.
    """
    if total == 0:
        return 0.0
    return round((passed / total) * 100, 1)


# History policy: issue 1666, acceptance criteria 2-4 (2026).
# See docs/quality/test-health-telemetry.html for the calculation basis.
TREND_RUNS = 8
REGRESSION_POINTS = 5.0
COUNT_FIELDS = ("passed", "failed", "skipped", "errors")


def make_history_record(packages: dict, timestamp: datetime) -> dict:
    """Summarize counts; diagnostics remain included in the outcome total."""
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("History timestamps require a timezone")
    counts = {key: sum(p[key] for p in packages.values()) for key in COUNT_FIELDS}
    total = sum(counts.values())
    record = dict(timestamp=timestamp.astimezone(UTC).isoformat(),
                  total=total, **counts,
                  pass_rate=compute_pass_rate(counts["passed"], total))
    validate_history([record])
    if any(p["total"] != sum(p[key] for key in COUNT_FIELDS)
           for p in packages.values()):
        raise ValueError("Package totals disagree with outcome counts")
    if any(type(p[key]) is not int or p[key] < 0
           for p in packages.values() for key in (*COUNT_FIELDS, "total")):
        raise ValueError("Package counts require nonnegative integers")
    return record


def validate_history(records: object) -> None:
    """Reject malformed or contradictory stored evidence before replacement."""
    if not isinstance(records, list):
        raise TypeError("History must be a JSON array")
    fields = {"timestamp", "total", "pass_rate", *COUNT_FIELDS}
    for record in records:
        if not isinstance(record, dict) or set(record) != fields:
            raise ValueError("History record fields do not match the schema")
        if any(type(record[key]) is not int or record[key] < 0
               for key in (*COUNT_FIELDS, "total")):
            raise ValueError("History counts require nonnegative integers")
        if record["total"] != sum(record[key] for key in COUNT_FIELDS):
            raise ValueError("History total disagrees with outcome counts")
        stamp = record["timestamp"]
        try:
            instant = datetime.fromisoformat(stamp)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid history timestamp") from exc
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError("History timestamps require a timezone")
        rate = record["pass_rate"]
        if (type(rate) not in (int, float) or not math.isfinite(rate)
                or rate != compute_pass_rate(record["passed"], record["total"])):
            raise ValueError("History pass rate disagrees with outcome counts")


def append_history(path: Path, packages: dict, timestamp: datetime) -> list[dict]:
    """Append one observation atomically; invalid existing data is preserved.

    A single writer is required. This does not merge concurrent writers.
    """
    records = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    validate_history(records)
    records.append(make_history_record(packages, timestamp))
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent,
                                     prefix=path.name + ".", suffix=".partial",
                                     delete=False) as stream:
        json.dump(records, stream, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
        temporary_path = stream.name
    os.replace(temporary_path, path)
    return records


# ---------------------------------------------------------------------------
# Gap detection
# ---------------------------------------------------------------------------

def find_test_gaps(
    source_packages: list[str],
    tested_packages: dict[str, dict],
) -> list[str]:
    """Find source packages with zero tests.

    Args:
        source_packages: List of source package directory names.
        tested_packages: Dict of packages that have test results.

    Returns:
        List of package names with no tests.
    """
    return [pkg for pkg in source_packages if pkg not in tested_packages]


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def generate_markdown_report(
    packages: dict[str, dict[str, int]],
    timestamp: datetime,
    gaps: list[str] | None = None,
    history: list[dict] | None = None,
) -> str:
    """Generate a markdown dashboard report.

    Args:
        packages: Dict mapping package name -> {passed, failed, skipped, errors, total}.
        timestamp: When the report was generated.
        gaps: Optional list of packages with 0 tests.

    Returns:
        Markdown string with summary table, emoji badges, timestamp, gap list.
    """
    lines: list[str] = []
    lines.append("# Test Health Dashboard")
    lines.append("")
    lines.append(f"**Generated**: {timestamp.strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")

    # Overall summary
    total_tests = sum(p.get("total", 0) for p in packages.values())
    total_passed = sum(p.get("passed", 0) for p in packages.values())
    total_failed = sum(p.get("failed", 0) for p in packages.values())
    total_skipped = sum(p.get("skipped", 0) for p in packages.values())
    total_errors = sum(p.get("errors", 0) for p in packages.values())
    overall_rate = compute_pass_rate(total_passed, total_tests)
    failing_packages = [n for n, p in packages.items() if p.get("failed", 0) > 0 or p.get("errors", 0) > 0]

    lines.append("## Overall Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total outcomes | {total_tests} |")
    lines.append(f"| Passed | {total_passed} |")
    lines.append(f"| Failed | {total_failed} |")
    lines.append(f"| Skipped | {total_skipped} |")
    lines.append(f"| Errors | {total_errors} |")
    lines.append(f"| Pass rate | {overall_rate}% |")
    lines.append(f"| Packages with failures | {len(failing_packages)} |")
    lines.append("")
    lines.append("Totals include diagnostic execution errors, not only collected test cases.")
    lines.append("")

    # Per-package table
    lines.append("## Per-Package Results")
    lines.append("")
    lines.append("| Status | Package | Outcomes | Pass | Fail | Skip | Errors | Rate |")
    lines.append("|--------|---------|-------|------|------|------|--------|------|")

    for name in sorted(packages.keys()):
        p = packages[name]
        total = p.get("total", 0)
        passed = p.get("passed", 0)
        failed = p.get("failed", 0)
        skipped = p.get("skipped", 0)
        errors = p.get("errors", 0)
        rate = compute_pass_rate(passed, total)

        # Emoji badge
        if failed > 0 or errors > 0:
            badge = "\u274c"
        elif total == 0 or passed == 0:
            badge = "\u26a0\ufe0f"
        else:
            badge = "\u2705"

        lines.append(f"| {badge} | {name} | {total} | {passed} | {failed} | {skipped} | {errors} | {rate}% |")

    lines.append("")

    # Gap list
    if gaps is not None:
        lines.append("## Packages with 0 Tests (Gap List)")
        lines.append("")
        if gaps:
            for g in sorted(gaps):
                lines.append(f"- `{g}`")
        else:
            lines.append("No gaps detected in the supplied package inventory.")
        lines.append("")

    if history:
        lines.extend(["## Recent Test Health", ""])
        if len(history) > 1:
            drop = (Decimal(str(history[-2]["pass_rate"]))
                    - Decimal(str(history[-1]["pass_rate"])))
            if drop > REGRESSION_POINTS:
                lines.extend([
                    f"> WARNING: Pass rate dropped by {drop:.1f} percentage points.",
                    "",
                ])
        lines.extend(["| Timestamp | Pass rate (%) |", "|-----------|---------------|"])
        for record in history[-TREND_RUNS:]:
            lines.append(f"| {record['timestamp']} | {record['pass_rate']:.1f} |")
        lines.extend(["", "Pass rate measures reported outcomes, not source coverage.", ""])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def discover_source_packages(repo_root: Path) -> list[str]:
    """Discover source packages under digitalmodel/src/digitalmodel/."""
    src_dir = repo_root / "digitalmodel" / "src" / "digitalmodel"
    if not src_dir.is_dir():
        return []
    return [
        d.name
        for d in sorted(src_dir.iterdir())
        if d.is_dir() and not d.name.startswith("_")
    ]


def run_pytest_per_package(repo_root: Path) -> dict[str, dict[str, int]]:
    """Run pytest per test subdirectory and collect per-package results.

    Instead of running all tests at once (which hits collection error limits),
    runs pytest per top-level test subdirectory for reliable results.

    Returns:
        Dict mapping package name -> {passed, failed, skipped, errors, total}.
    """
    tests_dir = repo_root / "digitalmodel" / "tests"
    if not tests_dir.is_dir():
        raise FileNotFoundError("Required test tree is unavailable")

    packages: dict[str, dict[str, int]] = {}
    skip_dirs = {"__pycache__", "fixtures", "output", "outputs",
                 "rainflow_comparison_results", "performance"}

    for sub in sorted(tests_dir.iterdir()):
        if not sub.is_dir() or sub.name in skip_dirs or sub.name.startswith("_"):
            continue
        pkg = sub.name
        print(f"  [{pkg}] running ...", end=" ", flush=True)

        cmd = [
            sys.executable, "-m", "pytest",
            str(sub),
            "-v", "--tb=no", "-q",
            "--no-header",
        ]
        try:
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                cwd=str(repo_root),
                timeout=120,
            )
            summary_line = ""
            all_lines = (result.stdout + "\n" + result.stderr).strip().split("\n")

            # Find summary line
            for line in reversed(all_lines):
                if re.search(r"\d+\s+(passed|failed|skipped|error)", line):
                    summary_line = line
                    break

            counts = parse_pytest_summary(summary_line)
            # Check for "no tests ran"
            no_tests = any("no tests ran" in l for l in all_lines)

            entry = {
                "passed": counts["passed"],
                "failed": counts["failed"],
                "skipped": counts["skipped"],
                "errors": counts["errors"],
                "total": counts["passed"] + counts["failed"] + counts["skipped"] + counts["errors"],
            }

            # A nonzero exit without reported failure evidence is diagnostic,
            # not a successful or empty package (including pytest exit code 5).
            if result.returncode != 0 and not (entry["failed"] or entry["errors"]):
                entry["errors"] += 1
                entry["total"] += 1

            if no_tests and entry["total"] == 0:
                # Skip packages with no tests (they'll appear in gaps)
                print("no tests")
                continue

            packages[pkg] = entry
            print(f"{entry['total']} outcomes ({entry['passed']}P/{entry['failed']}F/{entry['skipped']}S/{entry['errors']}E)")

        except subprocess.TimeoutExpired:
            packages[pkg] = {"passed": 0, "failed": 0, "skipped": 0, "errors": 1, "total": 1}
            print("TIMEOUT")
        except OSError as e:
            packages[pkg] = {"passed": 0, "failed": 0, "skipped": 0, "errors": 1, "total": 1}
            print(f"ERROR: {e}")

    return packages


def main() -> None:
    """Run the test health dashboard pipeline."""
    repo_root = Path(__file__).resolve().parents[2]
    now = datetime.now(UTC)

    print("[test-health-dashboard] Running pytest per package on digitalmodel/tests/ ...")
    packages = run_pytest_per_package(repo_root)

    print("[test-health-dashboard] Aggregating results ...")

    source_packages = discover_source_packages(repo_root)
    gaps = find_test_gaps(source_packages, packages)

    print("[test-health-dashboard] Generating dashboard ...")
    history_path = repo_root / "docs" / "dashboards" / "test-health-history.json"
    history = append_history(history_path, packages, now)
    md = generate_markdown_report(packages, now, gaps=gaps, history=history)

    output_path = repo_root / "docs" / "dashboards" / "test-health-dashboard.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8", newline="\n")

    # Compute overall stats
    total_tests = sum(p.get("total", 0) for p in packages.values())
    total_passed = sum(p.get("passed", 0) for p in packages.values())

    print(f"[test-health-dashboard] Dashboard written to {output_path.relative_to(repo_root).as_posix()}")
    print(f"[test-health-dashboard] Overall: {total_tests} outcomes, {total_passed} passed ({compute_pass_rate(total_passed, total_tests)}%)")
    print(f"[test-health-dashboard] Packages tested: {len(packages)}, Gaps: {len(gaps)}")


if __name__ == "__main__":
    main()
