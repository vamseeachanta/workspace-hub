#!/usr/bin/env python3
"""pyramid-conformance-check.py — Tier-1 automated conformance checks for the intelligence pyramid.

Implements the top-5 priority checks from pyramid-conformance-checks.md (#2206):
  DT-1:  Wiki frontmatter completeness
  ACC-1: docs/README.md links to intelligence ecosystem
  OWN-3: Transient artifacts not in normative directories
  ID-1:  Registry entries have content-based identity (doc_key/content_hash)
  ACC-3: Child artifacts backlink to parent operating model

Each check emits pass/fail with evidence. Script exits 0 if all pass, 1 if any fail.

Usage:
    uv run scripts/knowledge/pyramid-conformance-check.py [--check CHECK_ID] [--json] [--sample N]
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
WIKIS_DIR = REPO_ROOT / "knowledge" / "wikis"
DOC_INTEL_DIR = REPO_ROOT / "docs" / "document-intelligence"
INDEX_JSONL = REPO_ROOT / "data" / "document-index" / "index.jsonl"

# Wiki domains to scan (skip health-reports — temporary)
WIKI_DOMAINS = ["engineering", "marine-engineering", "maritime-law", "naval-architecture", "personal"]

# Frontmatter fields required by DT-1 (from #2209 GR-1 / llm_wiki.py schema)
DT1_REQUIRED_FIELDS = {"title", "tags", "added", "last_updated"}
DT1_RECOMMENDED_FIELDS = {"sources"}

# Parent operating model filename (ACC-3 target)
PARENT_MODEL = "llm-wiki-resource-doc-intelligence-operating-model.md"
PARENT_MODEL_ALIASES = [PARENT_MODEL, "#2205", "operating-model", "operating model"]

# Child artifacts that must backlink to parent (ACC-3)
CHILD_ARTIFACTS = [
    DOC_INTEL_DIR / "standards-codes-provenance-reuse-contract.md",
    DOC_INTEL_DIR / "durable-vs-transient-knowledge-boundary.md",
    DOC_INTEL_DIR / "pyramid-conformance-checks.md",
]

# Normative directories where transient artifacts must not appear (OWN-3)
NORMATIVE_DIRS = [
    DOC_INTEL_DIR,
    REPO_ROOT / "docs" / "standards",
    REPO_ROOT / "docs" / "governance",
]

# Transient artifact patterns (OWN-3)
TRANSIENT_PATTERNS = [
    "session-handoff-*",
    "handoff-*",
    "*-session-*.md",
]

# Intelligence ecosystem link targets for ACC-1
ACC1_LINK_TARGETS = [
    ("knowledge/wikis", "LLM-Wiki knowledge base"),
    ("document-intelligence", "Document intelligence architecture"),
]


@dataclass
class CheckResult:
    check_id: str
    name: str
    status: str  # "pass", "fail", "error"
    detail: str
    evidence: List[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


def parse_frontmatter(filepath: Path) -> Optional[dict]:
    """Extract YAML frontmatter from a markdown file. Returns None if no frontmatter."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return None

    if not text.startswith("---"):
        return None

    end = text.find("\n---", 3)
    if end == -1:
        return None

    fm_text = text[3:end].strip()
    result = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip().lower()
            val = val.strip()
            # Handle YAML list inline syntax [a, b, c]
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
            elif val == "":
                val = None
            result[key] = val
    return result


# ──────────────────────────────────────────────────────
# DT-1: Wiki Frontmatter Completeness
# ──────────────────────────────────────────────────────

def check_dt1(sample_size: int = 0) -> CheckResult:
    """Verify wiki pages have required frontmatter fields.

    Scans all wiki domains. Reports missing fields per page.
    """
    total_pages = 0
    failing_pages = []
    domain_stats = {}

    for domain in WIKI_DOMAINS:
        wiki_dir = WIKIS_DIR / domain / "wiki"
        if not wiki_dir.exists():
            continue

        domain_total = 0
        domain_fail = 0

        for md_file in wiki_dir.rglob("*.md"):
            # Skip index.md and log.md — they have different schemas
            if md_file.name in ("index.md", "log.md", "overview.md"):
                continue

            total_pages += 1
            domain_total += 1

            fm = parse_frontmatter(md_file)
            if fm is None:
                domain_fail += 1
                if len(failing_pages) < 20:
                    rel = md_file.relative_to(REPO_ROOT)
                    failing_pages.append(f"{rel}: no frontmatter")
                continue

            missing = DT1_REQUIRED_FIELDS - set(fm.keys())
            if missing:
                domain_fail += 1
                if len(failing_pages) < 20:
                    rel = md_file.relative_to(REPO_ROOT)
                    failing_pages.append(f"{rel}: missing {', '.join(sorted(missing))}")

        domain_stats[domain] = {"total": domain_total, "failing": domain_fail}

    total_failing = sum(d["failing"] for d in domain_stats.values())
    pass_rate = ((total_pages - total_failing) / total_pages * 100) if total_pages > 0 else 0

    status = "pass" if total_failing == 0 else "fail"
    detail = (
        f"{total_pages} wiki pages scanned, {total_failing} missing required frontmatter "
        f"({pass_rate:.1f}% pass rate)"
    )

    return CheckResult(
        check_id="DT-1",
        name="Wiki frontmatter completeness",
        status=status,
        detail=detail,
        evidence=failing_pages[:20],
        stats={"total_pages": total_pages, "failing": total_failing,
               "pass_rate": round(pass_rate, 1), "by_domain": domain_stats},
    )


# ──────────────────────────────────────────────────────
# ACC-1: docs/README.md Links Intelligence Ecosystem
# ──────────────────────────────────────────────────────

def check_acc1() -> CheckResult:
    """Verify docs/README.md contains links to intelligence ecosystem assets."""
    readme = REPO_ROOT / "docs" / "README.md"
    if not readme.exists():
        return CheckResult(
            check_id="ACC-1",
            name="docs/README links intelligence",
            status="error",
            detail="docs/README.md not found",
        )

    content = readme.read_text(encoding="utf-8", errors="replace").lower()
    found = []
    missing = []

    for pattern, label in ACC1_LINK_TARGETS:
        if pattern.lower() in content:
            found.append(f"{label} ({pattern})")
        else:
            missing.append(f"{label} ({pattern})")

    status = "pass" if not missing else "fail"
    detail = f"{len(found)}/{len(ACC1_LINK_TARGETS)} intelligence links found in docs/README.md"
    evidence = []
    if missing:
        evidence = [f"MISSING: {m}" for m in missing]
    if found:
        evidence += [f"FOUND: {f}" for f in found]

    return CheckResult(
        check_id="ACC-1",
        name="docs/README links intelligence",
        status=status,
        detail=detail,
        evidence=evidence,
        stats={"found": len(found), "missing": len(missing), "total": len(ACC1_LINK_TARGETS)},
    )


# ──────────────────────────────────────────────────────
# OWN-3: Transient Not in Normative Directories
# ──────────────────────────────────────────────────────

def check_own3() -> CheckResult:
    """Detect L6 session/handoff artifacts in L3-adjacent normative directories."""
    violations = []

    for normative_dir in NORMATIVE_DIRS:
        if not normative_dir.exists():
            continue

        for pattern in TRANSIENT_PATTERNS:
            for match in normative_dir.glob(pattern):
                rel = match.relative_to(REPO_ROOT)
                violations.append(str(rel))

        # Also check for .planning/ subdirs inside normative dirs
        for planning_dir in normative_dir.rglob(".planning"):
            if planning_dir.is_dir():
                rel = planning_dir.relative_to(REPO_ROOT)
                violations.append(f"{rel}/ (.planning dir in normative path)")

    status = "pass" if not violations else "fail"
    detail = (
        f"{len(violations)} transient artifact(s) found in normative directories"
        if violations
        else "No transient artifacts in normative directories"
    )

    return CheckResult(
        check_id="OWN-3",
        name="Transient not in normative dir",
        status=status,
        detail=detail,
        evidence=violations[:20],
        stats={"violations": len(violations)},
    )


# ──────────────────────────────────────────────────────
# ID-1: Registry Has doc_key (content_hash)
# ──────────────────────────────────────────────────────

# Accept both 32-char (current index) and 64-char (spec) hex values
DOC_KEY_RE = re.compile(r"^[0-9a-fA-F]{32,64}$")
DOC_KEY_PREFIXED_RE = re.compile(r"^sha256:[0-9a-fA-F]{32,64}$")


def check_id1(sample_size: int = 10000) -> CheckResult:
    """Verify registry entries include a content-based identity field.

    Samples the first N records of index.jsonl for efficiency (file is 547MB+).
    """
    if not INDEX_JSONL.exists():
        return CheckResult(
            check_id="ID-1",
            name="Registry has doc_key",
            status="error",
            detail=f"Index file not found: {INDEX_JSONL.relative_to(REPO_ROOT)}",
        )

    total = 0
    has_key = 0
    missing_key = 0
    invalid_key = 0
    sample_failures = []

    with open(INDEX_JSONL, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if sample_size and total >= sample_size:
                break

            line = line.strip()
            if not line:
                continue

            total += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                missing_key += 1
                continue

            # Check for content_hash or doc_key field
            key_val = record.get("content_hash") or record.get("doc_key")
            if not key_val:
                missing_key += 1
                if len(sample_failures) < 10:
                    path = record.get("path", "<unknown>")
                    sample_failures.append(f"No doc_key: {path[:80]}")
            elif DOC_KEY_RE.match(str(key_val)) or DOC_KEY_PREFIXED_RE.match(str(key_val)):
                has_key += 1
            else:
                invalid_key += 1
                if len(sample_failures) < 10:
                    path = record.get("path", "<unknown>")
                    sample_failures.append(f"Invalid key format ({str(key_val)[:20]}...): {path[:60]}")

    pass_rate = (has_key / total * 100) if total > 0 else 0
    status = "pass" if (missing_key == 0 and invalid_key == 0) else "fail"
    detail = (
        f"Sampled {total:,} records: {has_key:,} valid, "
        f"{missing_key:,} missing, {invalid_key:,} invalid format "
        f"({pass_rate:.1f}% pass)"
    )

    return CheckResult(
        check_id="ID-1",
        name="Registry has doc_key",
        status=status,
        detail=detail,
        evidence=sample_failures,
        stats={"sampled": total, "valid": has_key, "missing": missing_key,
               "invalid_format": invalid_key, "pass_rate": round(pass_rate, 1)},
    )


# ──────────────────────────────────────────────────────
# ACC-3: Child Artifacts Backlink Parent
# ──────────────────────────────────────────────────────

def check_acc3() -> CheckResult:
    """Verify child artifacts (provenance contract, boundary policy, this doc) link to parent model."""
    results = []
    missing = []

    for child_path in CHILD_ARTIFACTS:
        if not child_path.exists():
            missing.append(f"NOT FOUND: {child_path.relative_to(REPO_ROOT)}")
            continue

        content = child_path.read_text(encoding="utf-8", errors="replace")
        found = False
        for alias in PARENT_MODEL_ALIASES:
            if alias in content:
                found = True
                break

        rel = child_path.relative_to(REPO_ROOT)
        if found:
            results.append(f"LINKED: {rel}")
        else:
            missing.append(f"NO BACKLINK: {rel}")

    total = len(CHILD_ARTIFACTS)
    linked = total - len(missing)
    status = "pass" if not missing else "fail"
    detail = f"{linked}/{total} child artifacts link to parent operating model"

    return CheckResult(
        check_id="ACC-3",
        name="Child artifacts backlink parent",
        status=status,
        detail=detail,
        evidence=results + missing,
        stats={"total": total, "linked": linked, "missing": len(missing)},
    )


# ──────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────

ALL_CHECKS = {
    "DT-1": check_dt1,
    "ACC-1": check_acc1,
    "OWN-3": check_own3,
    "ID-1": check_id1,
    "ACC-3": check_acc3,
}


def run_checks(check_ids: Optional[List[str]] = None, sample_size: int = 10000,
               json_output: bool = False) -> int:
    """Run selected checks and report results. Returns 0 if all pass, 1 otherwise."""
    checks_to_run = check_ids or list(ALL_CHECKS.keys())
    results = []

    for cid in checks_to_run:
        fn = ALL_CHECKS.get(cid)
        if not fn:
            print(f"Unknown check: {cid}", file=sys.stderr)
            continue

        # Pass sample_size to checks that accept it
        if cid in ("DT-1", "ID-1"):
            result = fn(sample_size=sample_size)
        else:
            result = fn()

        results.append(result)

    if json_output:
        output = {
            "timestamp": datetime.now().isoformat(),
            "checks": [asdict(r) for r in results],
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r.status == "pass"),
                "failed": sum(1 for r in results if r.status == "fail"),
                "errors": sum(1 for r in results if r.status == "error"),
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print("=" * 60)
        print(" Pyramid Conformance Check — Tier 1")
        print(f" {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)

        for r in results:
            symbol = {"pass": "✓", "fail": "✗", "error": "⚠"}.get(r.status, "?")
            print(f"\n{symbol}  [{r.check_id}] {r.name}")
            print(f"   {r.detail}")
            if r.evidence:
                for ev in r.evidence[:10]:
                    print(f"   · {ev}")
                if len(r.evidence) > 10:
                    print(f"   ... and {len(r.evidence) - 10} more")

        passed = sum(1 for r in results if r.status == "pass")
        failed = sum(1 for r in results if r.status == "fail")
        errors = sum(1 for r in results if r.status == "error")
        print(f"\n{'=' * 60}")
        print(f" Results: {passed} passed, {failed} failed, {errors} errors")
        print(f"{'=' * 60}")

    any_failure = any(r.status in ("fail", "error") for r in results)
    return 1 if any_failure else 0


def main():
    parser = argparse.ArgumentParser(
        description="Tier-1 pyramid conformance checks (#2206)",
    )
    parser.add_argument(
        "--check", "-c",
        action="append",
        choices=list(ALL_CHECKS.keys()),
        help="Run specific check(s). Omit to run all.",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--sample", "-s",
        type=int,
        default=10000,
        help="Sample size for large-file checks (default: 10000, 0=all)",
    )
    args = parser.parse_args()

    sys.exit(run_checks(
        check_ids=args.check,
        sample_size=args.sample,
        json_output=args.json,
    ))


if __name__ == "__main__":
    main()
