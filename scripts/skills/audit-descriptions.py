#!/usr/bin/env python3
"""
Audit SKILL.md description fields for CSO compliance.

Classifies each description into:
  good          — contains trigger conditions
  too-short     — under 30 characters
  too-long      — over 500 characters
  workflow-summary — numbered steps or "then" chains
  first-person  — starts with "I can", "I will", "This skill helps"
  vague         — only generic terms without specifics

Outputs:
  - Summary table to stdout
  - JSONL violations to scripts/skills/description-violations.jsonl
"""

import json
import os
import re
import sys
from pathlib import Path


def find_skill_files(root: Path):
    """Find all SKILL.md files under .claude/skills/, excluding _archive/."""
    for dirpath, dirnames, filenames in os.walk(root / ".claude" / "skills"):
        # Prune _archive directories
        dirnames[:] = [d for d in dirnames if d != "_archive"]
        if "SKILL.md" in filenames:
            yield Path(dirpath) / "SKILL.md"


def extract_description(filepath: Path) -> str | None:
    """Extract description: field from YAML frontmatter without PyYAML."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None

    desc_parts = []
    in_frontmatter = True
    capturing = False
    is_multiline_block = False  # for > or | style

    for line in lines[1:]:
        if line.strip() == "---":
            break

        if line.startswith("description:"):
            val = line[len("description:"):].strip()
            # Remove surrounding quotes
            if val and val[0] in ('"', "'"):
                quote = val[0]
                val = val[1:]
                if val.endswith(quote):
                    val = val[:-1]
            if val in ("", ">", "|", ">-", "|-"):
                is_multiline_block = True
                capturing = True
                continue
            desc_parts.append(val)
            capturing = True
            is_multiline_block = False
            continue

        if capturing:
            if is_multiline_block and (line.startswith("  ") or line.startswith("\t")):
                desc_parts.append(line.strip())
            elif not is_multiline_block and (line.startswith("  ") or line.startswith("\t")):
                # Continuation of a folded value
                desc_parts.append(line.strip())
            else:
                break

    if not desc_parts:
        return None
    return " ".join(desc_parts).strip()


def classify(desc: str) -> list[str]:
    """Return list of violation categories for a description."""
    violations = []

    if len(desc) < 30:
        violations.append("too-short")

    if len(desc) > 500:
        violations.append("too-long")

    # First-person check
    lower = desc.lower().strip()
    first_person_starts = [
        "i can", "i will", "i help", "i assist",
        "this skill helps", "this skill will", "this skill can",
        "this skill assists", "this skill manages",
        "this tool helps", "this tool will",
    ]
    for fp in first_person_starts:
        if lower.startswith(fp):
            violations.append("first-person")
            break

    # Workflow-summary check: numbered steps, "first...then...finally"
    workflow_patterns = [
        r"\b(?:step\s*)?1[\.\):].*(?:step\s*)?2[\.\):]",  # numbered steps
        r"\bfirst\b.*\bthen\b.*\bfinally\b",
        r"\bfirst\b.*\bthen\b.*\bthen\b",
        r"(?:^|\s)1\.\s.*2\.\s",
    ]
    for pat in workflow_patterns:
        if re.search(pat, lower, re.DOTALL):
            violations.append("workflow-summary")
            break

    # Vague check: only generic terms without specifics
    vague_terms = ["helps with", "assists with", "manages", "handles", "provides support"]
    trigger_indicators = [
        "use when", "when", "if the", "invoke", "trigger",
        ".yaml", ".yml", ".json", ".csv", ".xlsx", ".py", ".sh", ".dat",
        "error", "fail", "openfoam", "orcaflex", "excel",
    ]
    has_vague = any(v in lower for v in vague_terms)
    has_specific = any(t in lower for t in trigger_indicators)
    if has_vague and not has_specific:
        violations.append("vague")

    return violations


def is_good(desc: str) -> bool:
    """Check if description already has good trigger conditions."""
    lower = desc.lower()
    good_indicators = [
        "use when", "when the user", "when you", "invoke when",
        "trigger when", "activate when",
    ]
    return any(g in lower for g in good_indicators) and len(desc) >= 30 and len(desc) <= 500


def main():
    repo_root = Path(os.environ.get("REPO_ROOT", Path(__file__).resolve().parents[2]))
    output_jsonl = repo_root / "scripts" / "skills" / "description-violations.jsonl"

    skills = sorted(find_skill_files(repo_root))

    results = {"good": [], "too-short": [], "too-long": [],
               "workflow-summary": [], "first-person": [], "vague": [],
               "no-description": [], "no-violations": []}
    all_records = []

    for path in skills:
        rel = str(path.relative_to(repo_root))
        desc = extract_description(path)

        record = {"file": rel, "description": desc, "violations": []}

        if desc is None:
            record["violations"] = ["no-description"]
            results["no-description"].append(rel)
        else:
            violations = classify(desc)
            if not violations:
                if is_good(desc):
                    results["good"].append(rel)
                    record["violations"] = []
                else:
                    results["no-violations"].append(rel)
                    record["violations"] = []
            else:
                record["violations"] = violations
                for v in violations:
                    results[v].append(rel)

        all_records.append(record)

    # Write JSONL (violations only)
    with open(output_jsonl, "w") as f:
        for rec in all_records:
            if rec["violations"]:
                f.write(json.dumps(rec) + "\n")

    # Summary report
    total = len(skills)
    good_count = len(results["good"])
    no_viol = len(results["no-violations"])
    print(f"\n{'='*60}")
    print(f"  SKILL.md Description Audit — {total} skills scanned")
    print(f"{'='*60}\n")

    cats = [
        ("good (has trigger conditions)", results["good"]),
        ("no-violations (acceptable)", results["no-violations"]),
        ("too-short (<30 chars)", results["too-short"]),
        ("too-long (>500 chars)", results["too-long"]),
        ("workflow-summary", results["workflow-summary"]),
        ("first-person", results["first-person"]),
        ("vague", results["vague"]),
        ("no-description", results["no-description"]),
    ]

    for label, items in cats:
        pct = len(items) / total * 100 if total else 0
        print(f"  {label:40s}  {len(items):4d}  ({pct:5.1f}%)")

    violation_count = sum(len(results[k]) for k in ["too-short", "too-long", "workflow-summary", "first-person", "vague", "no-description"])
    print(f"\n  Total violations:                         {violation_count:4d}")
    print(f"  Violation JSONL: {output_jsonl.relative_to(repo_root)}")

    # Detail sections for each violation type
    for label, key in [("TOO SHORT", "too-short"), ("TOO LONG", "too-long"),
                       ("WORKFLOW SUMMARY", "workflow-summary"),
                       ("FIRST PERSON", "first-person"), ("VAGUE", "vague"),
                       ("NO DESCRIPTION", "no-description")]:
        items = results[key]
        if items:
            print(f"\n--- {label} ({len(items)}) ---")
            for item in items:
                # Find the description for context
                for rec in all_records:
                    if rec["file"] == item:
                        d = rec["description"] or "(none)"
                        print(f"  {item}")
                        print(f"    -> {d[:120]}")
                        break

    print()


if __name__ == "__main__":
    main()
