#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Skill Evaluator for workspace-hub.

Validates all SKILL.md files for structure, quality, and consistency.

Usage:
    uv run .claude/skills/development/skill-eval/scripts/eval-skills.py
    uv run .claude/skills/development/skill-eval/scripts/eval-skills.py --format json
    uv run .claude/skills/development/skill-eval/scripts/eval-skills.py --skill testing-tdd-london
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SKILLS_ROOT = Path(".claude/skills")

REQUIRED_FRONTMATTER = ["name", "description", "version", "category"]
REQUIRED_SECTIONS = [
    "Quick Start",
    "When to Use",
    "Core Concepts",
    "Usage Examples",
    "Best Practices",
    "Error Handling",
    "Version History",
]
SECTIONS_WITH_CODE = ["Quick Start", "Usage Examples"]

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
TODO_RE = re.compile(r"\bTODO\b|\bFIXME\b", re.IGNORECASE)

DESC_MIN_WORDS = 10
DESC_MAX_WORDS = 200

SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Issue:
    severity: str  # critical | warning | info
    check: str
    message: str
    fix: str = ""


@dataclass
class SkillResult:
    path: str
    name: str | None
    category_dir: str
    passed: bool = True
    issues: list[Issue] = field(default_factory=list)


@dataclass
class EvalReport:
    timestamp: str = ""
    total: int = 0
    passed: int = 0
    failed_critical: int = 0
    failed_warning: int = 0
    results: list[SkillResult] = field(default_factory=list)
    issues_by_severity: dict[str, int] = field(default_factory=lambda: {"critical": 0, "warning": 0, "info": 0})
    top_issues: list[dict] = field(default_factory=list)
    by_category: dict[str, dict] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Extract YAML frontmatter from SKILL.md content."""
    stripped = content.lstrip()
    if not stripped.startswith("---"):
        return None, content

    end = stripped.find("---", 3)
    if end == -1:
        return None, content

    raw = stripped[3:end].strip()
    try:
        meta = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None, content

    if not isinstance(meta, dict):
        return None, content

    body = stripped[end + 3:]
    return meta, body


def extract_heading_name(content: str) -> str | None:
    """Fallback: extract skill name from first # heading."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None


def extract_h2_sections(body: str) -> list[str]:
    """Return list of H2 heading texts found in body."""
    sections = []
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("## "):
            sections.append(line[3:].strip())
    return sections


def section_body(body: str, section_name: str) -> str | None:
    """Return the text content under a specific H2 section."""
    lines = body.splitlines()
    capture = False
    result: list[str] = []
    pattern = section_name.lower()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip().lower()
            if heading == pattern:
                capture = True
                continue
            elif capture:
                break
        if capture:
            result.append(line)
    return "\n".join(result) if result else None


def has_code_block(text: str) -> bool:
    return "```" in text


def category_from_path(path: Path, root: Path) -> str:
    """Extract top-level category directory from skill path."""
    try:
        rel = path.relative_to(root)
        parts = rel.parts
        # parts[0] is category dir, e.g. "development", "coordination"
        return parts[0] if parts else "unknown"
    except ValueError:
        return "unknown"


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_file_readable(path: Path, content: str) -> list[Issue]:
    if not content.strip():
        return [Issue("critical", "file_empty", f"SKILL.md is empty", "Add skill content")]
    return []


def check_frontmatter(content: str) -> tuple[list[Issue], dict | None, str]:
    """Check frontmatter exists and is valid YAML. Returns issues, meta, body."""
    issues: list[Issue] = []
    stripped = content.lstrip()

    if not stripped.startswith("---"):
        return [Issue(
            "critical", "frontmatter_missing",
            "No YAML frontmatter found",
            "Add --- delimited YAML frontmatter with name, description, version, category"
        )], None, content

    end = stripped.find("---", 3)
    if end == -1:
        return [Issue(
            "critical", "frontmatter_unclosed",
            "YAML frontmatter not properly closed",
            "Add closing --- after frontmatter block"
        )], None, content

    raw = stripped[3:end].strip()
    try:
        meta = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        return [Issue(
            "critical", "yaml_invalid",
            f"YAML parse error: {e}",
            "Fix YAML syntax in frontmatter"
        )], None, content

    if not isinstance(meta, dict):
        return [Issue(
            "critical", "yaml_not_dict",
            "Frontmatter did not parse as a mapping",
            "Ensure frontmatter contains key: value pairs"
        )], None, content

    body = stripped[end + 3:]
    return issues, meta, body


def check_required_fields(meta: dict) -> list[Issue]:
    issues = []
    for f in REQUIRED_FRONTMATTER:
        if f not in meta or not meta[f]:
            sev = "critical" if f in ("name", "description") else "warning"
            issues.append(Issue(
                sev, f"{f}_missing",
                f"Required field '{f}' missing from frontmatter",
                f"Add '{f}: <value>' to YAML frontmatter"
            ))
    return issues


def check_semver(meta: dict) -> list[Issue]:
    version = meta.get("version")
    if version and not SEMVER_RE.match(str(version)):
        return [Issue(
            "warning", "version_not_semver",
            f"Version '{version}' does not follow X.Y.Z semver",
            "Use semantic versioning format: X.Y.Z"
        )]
    return []


def check_category_matches_dir(meta: dict, category_dir: str) -> list[Issue]:
    cat = meta.get("category", "")
    if not cat:
        return []
    cat_lower = str(cat).lower().replace("-", "").replace("_", "")
    dir_lower = category_dir.lower().replace("-", "").replace("_", "")
    # Allow partial matches (e.g., "workspace-hub" matches "workspace" dir)
    if cat_lower != dir_lower and not cat_lower.startswith(dir_lower) and not dir_lower.startswith(cat_lower):
        return [Issue(
            "warning", "category_dir_mismatch",
            f"Frontmatter category '{cat}' does not match directory '{category_dir}'",
            f"Update category to match directory or move skill to correct directory"
        )]
    return []


def check_required_sections(body: str) -> list[Issue]:
    issues = []
    found = [s.lower() for s in extract_h2_sections(body)]
    for section in REQUIRED_SECTIONS:
        if section.lower() not in found:
            issues.append(Issue(
                "warning", "section_missing",
                f"Required section '## {section}' not found",
                f"Add '## {section}' section"
            ))
    return issues


def check_sections_have_code(body: str) -> list[Issue]:
    issues = []
    for sec_name in SECTIONS_WITH_CODE:
        sec_body = section_body(body, sec_name)
        if sec_body is not None and not has_code_block(sec_body):
            issues.append(Issue(
                "warning", f"{sec_name.lower().replace(' ', '_')}_no_code",
                f"'{sec_name}' section has no code blocks",
                f"Add code examples with ``` blocks to '{sec_name}'"
            ))
    return issues


def check_description_quality(meta: dict) -> list[Issue]:
    desc = meta.get("description", "")
    if not desc:
        return []
    words = str(desc).split()
    if len(words) < DESC_MIN_WORDS:
        return [Issue(
            "warning", "description_too_short",
            f"Description has {len(words)} words (min {DESC_MIN_WORDS})",
            f"Expand description to at least {DESC_MIN_WORDS} words"
        )]
    if len(words) > DESC_MAX_WORDS:
        return [Issue(
            "info", "description_too_long",
            f"Description has {len(words)} words (max {DESC_MAX_WORDS})",
            f"Trim description to under {DESC_MAX_WORDS} words"
        )]
    return []


def check_todo_fixme(content: str) -> list[Issue]:
    matches = TODO_RE.findall(content)
    if matches:
        return [Issue(
            "warning", "todo_fixme_present",
            f"Found {len(matches)} TODO/FIXME markers",
            "Resolve or remove TODO/FIXME items"
        )]
    return []


def check_related_skills(meta: dict, name_index: dict[str, Path]) -> list[Issue]:
    related = meta.get("related_skills", [])
    if not related or not isinstance(related, list):
        return []
    issues = []
    for ref in related:
        ref_str = str(ref).strip()
        if ref_str not in name_index:
            issues.append(Issue(
                "warning", "related_skill_unresolved",
                f"related_skills reference '{ref_str}' not found",
                f"Fix reference or remove from related_skills list"
            ))
    return issues


def check_v2_template(content: str) -> list[Issue]:
    if not content.lstrip().startswith("---"):
        return [Issue(
            "info", "legacy_format",
            "Uses legacy format (no YAML frontmatter); consider migrating to v2 template",
            "Convert to v2 template with --- delimited YAML frontmatter"
        )]
    return []


def check_optional_sections(body: str) -> list[Issue]:
    issues = []
    found = [s.lower() for s in extract_h2_sections(body)]
    optional = {"Metrics": "metrics", "Metrics & Success Criteria": "metrics"}
    for section, label in optional.items():
        if section.lower() not in found:
            issues.append(Issue(
                "info", f"{label}_section_missing",
                f"Optional section '## {section}' not found",
                f"Consider adding '## {section}' section"
            ))
            break  # only report once for metrics variants
    return issues


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def discover_skills(root: Path) -> list[Path]:
    """Find all SKILL.md files under skills root."""
    return sorted(root.rglob("SKILL.md"))


def build_name_index(skills: list[Path], root: Path) -> dict[str, Path]:
    """Build mapping from skill name -> path for cross-reference checks."""
    index: dict[str, Path] = {}
    for path in skills:
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        meta, _ = parse_frontmatter(content)
        if meta and "name" in meta:
            index[str(meta["name"])] = path
        else:
            name = extract_heading_name(content)
            if name:
                # Slugify heading for index
                slug = name.lower().replace(" ", "-")
                slug = re.sub(r"[^a-z0-9\-]", "", slug)
                index[slug] = path
    return index


def evaluate_skill(path: Path, root: Path, name_index: dict[str, Path]) -> SkillResult:
    """Run all checks on a single SKILL.md file."""
    rel_path = str(path.relative_to(root.parent.parent.parent) if root.parent.parent.parent.exists() else path)
    cat_dir = category_from_path(path, root)

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return SkillResult(
            path=rel_path, name=None, category_dir=cat_dir, passed=False,
            issues=[Issue("critical", "file_unreadable", str(e))]
        )

    all_issues: list[Issue] = []

    # File readable
    all_issues.extend(check_file_readable(path, content))
    if any(i.severity == "critical" for i in all_issues):
        return SkillResult(path=rel_path, name=None, category_dir=cat_dir, passed=False, issues=all_issues)

    # v2 template check (info)
    all_issues.extend(check_v2_template(content))

    # Frontmatter
    fm_issues, meta, body = check_frontmatter(content)
    all_issues.extend(fm_issues)

    skill_name = None
    if meta:
        skill_name = meta.get("name")
        all_issues.extend(check_required_fields(meta))
        all_issues.extend(check_semver(meta))
        all_issues.extend(check_category_matches_dir(meta, cat_dir))
        all_issues.extend(check_description_quality(meta))
        all_issues.extend(check_related_skills(meta, name_index))
    else:
        skill_name = extract_heading_name(content)
        body = content

    # Content checks
    all_issues.extend(check_required_sections(body))
    all_issues.extend(check_sections_have_code(body))
    all_issues.extend(check_todo_fixme(content))
    all_issues.extend(check_optional_sections(body))

    has_critical = any(i.severity == "critical" for i in all_issues)
    return SkillResult(
        path=rel_path,
        name=skill_name if skill_name else None,
        category_dir=cat_dir,
        passed=not has_critical,
        issues=all_issues,
    )


def build_report(results: list[SkillResult]) -> EvalReport:
    """Aggregate results into a report."""
    report = EvalReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        total=len(results),
    )

    check_counts: dict[str, int] = {}

    for r in results:
        has_critical = False
        has_warning = False
        for issue in r.issues:
            report.issues_by_severity[issue.severity] = report.issues_by_severity.get(issue.severity, 0) + 1
            check_counts[issue.check] = check_counts.get(issue.check, 0) + 1
            if issue.severity == "critical":
                has_critical = True
            elif issue.severity == "warning":
                has_warning = True

        if has_critical:
            report.failed_critical += 1
        elif has_warning:
            report.failed_warning += 1
        else:
            report.passed += 1

        # By category
        cat = r.category_dir
        if cat not in report.by_category:
            report.by_category[cat] = {"total": 0, "passed": 0, "failed": 0}
        report.by_category[cat]["total"] += 1
        if not has_critical:
            report.by_category[cat]["passed"] += 1
        else:
            report.by_category[cat]["failed"] += 1

    report.results = results

    # Top issues
    sorted_checks = sorted(check_counts.items(), key=lambda x: -x[1])
    for check_name, count in sorted_checks[:10]:
        # Find severity for this check from first occurrence
        sev = "info"
        for r in results:
            for i in r.issues:
                if i.check == check_name:
                    sev = i.severity
                    break
            if sev != "info":
                break
        report.top_issues.append({"check": check_name, "count": count, "severity": sev})

    return report


# ---------------------------------------------------------------------------
# Report formatters
# ---------------------------------------------------------------------------

def format_human(report: EvalReport, severity_filter: str, summary_only: bool) -> str:
    """Format report as human-readable text."""
    lines: list[str] = []
    lines.append("=" * 64)
    lines.append("  SKILL EVALUATION REPORT")
    lines.append(f"  Generated: {report.timestamp}")
    lines.append("=" * 64)
    lines.append("")
    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Total skills evaluated:  {report.total}")
    lines.append(f"  Passed (no critical):    {report.passed}  ({report.passed / report.total * 100:.1f}%)" if report.total else "  Passed: 0")
    lines.append(f"  Warnings only:           {report.failed_warning}  ({report.failed_warning / report.total * 100:.1f}%)" if report.total else "  Warnings only: 0")
    lines.append(f"  Critical failures:       {report.failed_critical}  ({report.failed_critical / report.total * 100:.1f}%)" if report.total else "  Critical: 0")
    lines.append("")
    lines.append("  Issues by severity:")
    for sev in ("critical", "warning", "info"):
        lines.append(f"    {sev.upper():10s} {report.issues_by_severity.get(sev, 0)}")
    lines.append("")

    # By category
    lines.append("  By category:")
    for cat in sorted(report.by_category):
        c = report.by_category[cat]
        lines.append(f"    {cat:25s} {c['total']:3d} skills | {c['passed']:3d} pass | {c['failed']:3d} fail")
    lines.append("")

    # Top issues
    if report.top_issues:
        lines.append("TOP ISSUES")
        lines.append("-" * 40)
        for i, ti in enumerate(report.top_issues, 1):
            lines.append(f"  {i:2d}. {ti['check']:35s} {ti['count']:3d} skills  [{ti['severity'].upper()}]")
        lines.append("")

    if summary_only:
        lines.append("=" * 64)
        return "\n".join(lines)

    min_sev = SEVERITY_ORDER.get(severity_filter, 2)

    # Critical failures
    criticals = [r for r in report.results if any(i.severity == "critical" for i in r.issues)]
    if criticals and min_sev <= SEVERITY_ORDER["critical"]:
        lines.append("CRITICAL FAILURES")
        lines.append("-" * 40)
        for r in criticals:
            label = r.name or r.path
            lines.append(f"[CRITICAL] {label}")
            for issue in r.issues:
                if issue.severity == "critical":
                    lines.append(f"  - {issue.check}: {issue.message}")
                    if issue.fix:
                        lines.append(f"    Fix: {issue.fix}")
            lines.append("")

    # Warnings
    warnings = [r for r in report.results if any(i.severity == "warning" for i in r.issues) and not any(i.severity == "critical" for i in r.issues)]
    if warnings and min_sev <= SEVERITY_ORDER["warning"]:
        lines.append(f"WARNINGS ({len(warnings)} skills)")
        lines.append("-" * 40)
        for r in warnings[:30]:  # cap display at 30
            label = r.name or r.path
            lines.append(f"[WARNING] {label}")
            for issue in r.issues:
                if SEVERITY_ORDER.get(issue.severity, 2) <= min_sev:
                    lines.append(f"  - {issue.check}: {issue.message}")
            lines.append("")
        if len(warnings) > 30:
            lines.append(f"  ... and {len(warnings) - 30} more (use --format json for full list)")
            lines.append("")

    lines.append("=" * 64)
    has_critical = report.failed_critical > 0
    lines.append(f"Exit code: {'1 (critical failures found)' if has_critical else '0 (all checks passed)'}")
    lines.append("=" * 64)

    return "\n".join(lines)


def format_json(report: EvalReport, severity_filter: str) -> str:
    """Format report as JSON."""
    min_sev = SEVERITY_ORDER.get(severity_filter, 2)

    results_data = []
    for r in report.results:
        filtered_issues = [
            {"severity": i.severity, "check": i.check, "message": i.message, "fix": i.fix}
            for i in r.issues
            if SEVERITY_ORDER.get(i.severity, 2) <= min_sev
        ]
        if filtered_issues or min_sev >= 2:
            has_critical = any(i.severity == "critical" for i in r.issues)
            results_data.append({
                "path": r.path,
                "name": r.name,
                "category": r.category_dir,
                "status": "fail" if has_critical else "pass",
                "issues": filtered_issues,
            })

    data = {
        "timestamp": report.timestamp,
        "summary": {
            "total_skills": report.total,
            "passed": report.passed,
            "failed_critical": report.failed_critical,
            "failed_warning_only": report.failed_warning,
            "issues": report.issues_by_severity,
        },
        "by_category": report.by_category,
        "top_issues": report.top_issues,
        "results": results_data,
    }
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Duplicate name detection
# ---------------------------------------------------------------------------

def check_duplicate_names(results: list[SkillResult]) -> list[SkillResult]:
    """Add warnings for duplicate skill names across results."""
    seen: dict[str, list[str]] = {}
    for r in results:
        if r.name:
            seen.setdefault(r.name, []).append(r.path)
    for name, paths in seen.items():
        if len(paths) > 1:
            for r in results:
                if r.name == name:
                    r.issues.append(Issue(
                        "warning", "duplicate_name",
                        f"Skill name '{name}' shared by {len(paths)} files: {', '.join(paths)}",
                        "Ensure each skill has a unique name"
                    ))
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate workspace-hub SKILL.md files")
    parser.add_argument("--skill", help="Evaluate a single skill by name")
    parser.add_argument("--category", help="Filter by top-level category directory")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    parser.add_argument("--severity", choices=["critical", "warning", "info"], default="info", help="Minimum severity to report")
    parser.add_argument("--summary-only", action="store_true", help="Show summary only")
    parser.add_argument("--output", help="Write report to file")
    parser.add_argument("--root", default=".", help="Workspace root directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    skills_dir = root / SKILLS_ROOT

    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}", file=sys.stderr)
        return 2

    # Discover
    all_paths = discover_skills(skills_dir)
    print(f"Discovered {len(all_paths)} SKILL.md files", file=sys.stderr)

    # Build name index for cross-reference checks
    name_index = build_name_index(all_paths, skills_dir)
    print(f"Built name index with {len(name_index)} entries", file=sys.stderr)

    # Filter
    if args.category:
        all_paths = [p for p in all_paths if category_from_path(p, skills_dir) == args.category]
        print(f"Filtered to {len(all_paths)} skills in category '{args.category}'", file=sys.stderr)

    if args.skill:
        target = args.skill.lower()
        matched = [p for p in all_paths if target in str(p).lower()]
        if not matched:
            print(f"Error: No skill matching '{args.skill}' found", file=sys.stderr)
            return 2
        all_paths = matched
        print(f"Evaluating {len(all_paths)} matching skill(s)", file=sys.stderr)

    # Evaluate
    results: list[SkillResult] = []
    for path in all_paths:
        result = evaluate_skill(path, skills_dir, name_index)
        results.append(result)

    # Duplicate name check (cross-skill)
    results = check_duplicate_names(results)

    # Build report
    report = build_report(results)

    # Format output
    if args.format == "json":
        output = format_json(report, args.severity)
    else:
        output = format_human(report, args.severity, args.summary_only)

    # Output
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(output)

    return 1 if report.failed_critical > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
