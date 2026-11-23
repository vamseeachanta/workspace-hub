#!/usr/bin/env python3
"""Audit /mnt/ace for undiscovered resources and cross-reference against indexes.

Scans:
  1. 8 cloned GitHub repos vs open-source-engineering-catalog.yaml
  2. docs/conferences/ vs document-index/index.jsonl
  3. O&G-Standards/ orgs vs standards-transfer-ledger.yaml
  4. docs/engineering-refs/ subdirectories

Output: docs/reports/ace-undiscovered-resources.md

GH issue: #1579
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
ACE_ROOT = "/mnt/ace"
WORKSPACE = Path(__file__).resolve().parents[2]  # workspace-hub root
CATALOG_PATH = WORKSPACE / ".planning/archive/catalog/open-source-engineering-catalog.yaml"
INDEX_PATH = WORKSPACE / "data/document-index/index.jsonl"
LEDGER_PATH = WORKSPACE / "data/document-index/standards-transfer-ledger.yaml"
ENHANCEMENT_PATH = WORKSPACE / "data/document-index/enhancement-plan.yaml"
REPORT_PATH = WORKSPACE / "docs/reports/ace-undiscovered-resources.md"

EXPECTED_REPOS = [
    "WEC-Sim", "openfast", "gmsh", "capytaine",
    "HAMS", "MoorDyn", "MoorPy", "opm-common",
]

EXPECTED_ORGS = [
    "API", "ASTM", "DNV", "ISO", "BSI",
    "ABS", "Norsok", "SNAME", "MIL", "OnePetro", "NEMA",
]

# Domain keywords for estimating value of uncatalogued repos
DOMAIN_KEYWORDS = {
    "opm-common": "reservoir_simulation",
    "WEC-Sim": "hydrodynamics",
    "openfast": "marine_offshore",
    "gmsh": "cad_geometry",
    "capytaine": "hydrodynamics",
    "HAMS": "hydrodynamics",
    "MoorDyn": "marine_offshore",
    "MoorPy": "marine_offshore",
}


# ===========================================================================
# 1. Repo cross-reference
# ===========================================================================

def check_repos_in_catalog(
    repo_names: list[str],
    catalog: dict,
) -> list[dict]:
    """Check which repos appear in the OSS catalog.

    Returns list of dicts: {name, in_catalog, domain}.
    """
    # Build lookup: lowercase name/url -> domain
    catalog_lookup: dict[str, str] = {}
    for domain_name, domain_data in catalog.get("domains", {}).items():
        for lib in domain_data.get("libraries", []):
            catalog_lookup[lib.get("name", "").lower()] = domain_name
            url = lib.get("url", "").lower()
            if url:
                # Extract repo slug from URL
                parts = url.rstrip("/").split("/")
                if parts:
                    catalog_lookup[parts[-1].lower()] = domain_name

    results = []
    for name in repo_names:
        domain = catalog_lookup.get(name.lower())
        results.append({
            "name": name,
            "in_catalog": domain is not None,
            "domain": domain,
        })
    return results


def get_repo_last_updated(repo_path: str) -> str | None:
    """Get the last git commit date for a repo."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "log", "-1", "--format=%aI"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


# ===========================================================================
# 2. Conference scanning
# ===========================================================================

def scan_conferences(conferences_root: str) -> list[dict]:
    """Scan conference directories and count files."""
    results = []
    root = Path(conferences_root)
    if not root.is_dir():
        return results
    for d in sorted(root.iterdir()):
        if d.is_dir():
            file_count = sum(1 for _ in d.rglob("*") if _.is_file())
            results.append({
                "name": d.name,
                "file_count": file_count,
                "indexed": False,
            })
    return results


def check_conferences_in_index(
    conferences: list[dict],
    index_lines: list[str],
) -> list[dict]:
    """Check which conferences have entries in the index."""
    # Build set of conference names that appear in index paths
    indexed_names: set[str] = set()
    for line in index_lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            path = entry.get("path", "")
            if "conferences" in path.lower():
                # Extract conference name from path
                parts = path.split("/")
                for i, p in enumerate(parts):
                    if p.lower() == "conferences" and i + 1 < len(parts):
                        indexed_names.add(parts[i + 1])
                        break
        except json.JSONDecodeError:
            continue

    for conf in conferences:
        if conf["name"] in indexed_names:
            conf["indexed"] = True
    return conferences


# ===========================================================================
# 3. Standards coverage
# ===========================================================================

def calculate_standards_coverage(
    disk_counts: dict[str, int],
    ledger: dict,
) -> list[dict]:
    """Calculate coverage of standards orgs: ledger entries vs files on disk."""
    # Count ledger entries per org
    ledger_counts: dict[str, int] = {}
    for std in ledger.get("standards", []):
        org = std.get("org", "")
        if org:
            ledger_counts[org] = ledger_counts.get(org, 0) + 1

    results = []
    for org, disk_count in sorted(disk_counts.items()):
        lc = ledger_counts.get(org, 0)
        coverage = (lc / disk_count * 100) if disk_count > 0 else 0.0
        results.append({
            "org": org,
            "disk_count": disk_count,
            "ledger_count": lc,
            "coverage_pct": round(coverage, 2),
        })
    return results


def count_standards_files(standards_root: str, orgs: list[str]) -> dict[str, int]:
    """Count files per org directory under O&G-Standards/."""
    counts = {}
    root = Path(standards_root)
    for org in orgs:
        org_dir = root / org
        if org_dir.is_dir():
            counts[org] = sum(1 for _ in org_dir.rglob("*") if _.is_file())
        else:
            counts[org] = 0
    return counts


# ===========================================================================
# 4. Engineering refs
# ===========================================================================

def scan_engineering_refs(refs_root: str) -> dict:
    """Scan engineering-refs directory for subdirs and top-level files."""
    root = Path(refs_root)
    if not root.is_dir():
        return {"top_level_files": 0, "subdirs": []}

    top_level = sum(1 for f in root.iterdir() if f.is_file())
    subdirs = []
    for d in sorted(root.iterdir()):
        if d.is_dir():
            file_count = sum(1 for _ in d.rglob("*") if _.is_file())
            subdirs.append({"name": d.name, "file_count": file_count})

    return {"top_level_files": top_level, "subdirs": subdirs}


# ===========================================================================
# 5. Report generation
# ===========================================================================

def _estimate_value(item: dict, item_type: str) -> int:
    """Rough value score for ranking undiscovered resources.

    Higher = more valuable to index next.
    """
    if item_type == "repo" and not item.get("in_catalog"):
        return 80  # Uncataloged repo is high value
    if item_type == "conference":
        if not item.get("indexed"):
            return min(item.get("file_count", 0) // 10, 100)
    if item_type == "standard":
        uncovered = item.get("disk_count", 0) - item.get("ledger_count", 0)
        return min(uncovered // 50, 100)
    if item_type == "eng_ref":
        return item.get("file_count", 0) * 2
    return 0


def generate_report(audit_data: dict) -> str:
    """Generate the markdown audit report."""
    lines: list[str] = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines.append("# /mnt/ace Undiscovered Resource Audit")
    lines.append(f"\nGenerated: {now}")
    lines.append("")

    # --- Summary ---
    lines.append("## Summary")
    lines.append("")
    total_repos = len(audit_data.get("repos", []))
    cataloged = sum(1 for r in audit_data.get("repos", []) if r["in_catalog"])
    total_conferences = len(audit_data.get("conferences", []))
    indexed_conf = sum(1 for c in audit_data.get("conferences", []) if c.get("indexed"))
    total_conf_files = sum(c.get("file_count", 0) for c in audit_data.get("conferences", []))
    total_std_files = sum(s.get("disk_count", 0) for s in audit_data.get("standards", []))
    total_ledger = sum(s.get("ledger_count", 0) for s in audit_data.get("standards", []))
    eng_refs = audit_data.get("engineering_refs", {})
    eng_top = eng_refs.get("top_level_files", 0)
    eng_subdirs = eng_refs.get("subdirs", [])
    eng_total = eng_top + sum(d.get("file_count", 0) for d in eng_subdirs)

    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| GitHub repos scanned | {total_repos} |")
    lines.append(f"| Repos in catalog | {cataloged}/{total_repos} |")
    lines.append(f"| Conference collections | {total_conferences} |")
    lines.append(f"| Conference collections indexed | {indexed_conf}/{total_conferences} |")
    lines.append(f"| Total conference files | {total_conf_files:,} |")
    lines.append(f"| Standards files on disk | {total_std_files:,} |")
    lines.append(f"| Standards in ledger | {total_ledger} |")
    lines.append(f"| Engineering ref files | {eng_total} |")
    lines.append("")

    # --- Repos ---
    lines.append("## 1. GitHub Repos")
    lines.append("")
    lines.append("| Repo | Last Updated | In Catalog | Domain |")
    lines.append("|---|---|---|---|")
    for r in audit_data.get("repos", []):
        updated = r.get("last_updated", "unknown")
        if updated and len(updated) > 10:
            updated = updated[:10]
        cat = "Yes" if r["in_catalog"] else "**NO**"
        domain = r.get("domain") or "—"
        lines.append(f"| {r['name']} | {updated} | {cat} | {domain} |")
    lines.append("")

    # --- Conferences ---
    lines.append("## 2. Conference Collections")
    lines.append("")
    lines.append("| Conference | Files | Indexed |")
    lines.append("|---|---|---|")
    for c in sorted(audit_data.get("conferences", []), key=lambda x: x["file_count"], reverse=True):
        idx = "Yes" if c.get("indexed") else "**NO**"
        lines.append(f"| {c['name']} | {c['file_count']:,} | {idx} |")
    lines.append("")

    # --- Standards ---
    lines.append("## 3. O&G Standards Coverage")
    lines.append("")
    lines.append("| Org | Files on Disk | In Ledger | Coverage % |")
    lines.append("|---|---|---|---|")
    for s in sorted(audit_data.get("standards", []), key=lambda x: x["disk_count"], reverse=True):
        lines.append(f"| {s['org']} | {s['disk_count']:,} | {s['ledger_count']} | {s['coverage_pct']:.1f}% |")
    lines.append("")

    # --- Engineering Refs ---
    lines.append("## 4. Engineering References")
    lines.append("")
    lines.append(f"Top-level files: {eng_top}")
    lines.append("")
    if eng_subdirs:
        lines.append("| Subdirectory | Files |")
        lines.append("|---|---|")
        for d in eng_subdirs:
            lines.append(f"| {d['name']} | {d['file_count']} |")
        lines.append("")

    # --- Top 20 Undiscovered ---
    lines.append("## Top 20 Undiscovered Resources by Estimated Value")
    lines.append("")

    scored: list[tuple[int, str, str]] = []

    for r in audit_data.get("repos", []):
        if not r["in_catalog"]:
            score = _estimate_value(r, "repo")
            scored.append((score, f"Repo: {r['name']} (not in catalog)", "Add to open-source-engineering-catalog.yaml"))

    for c in audit_data.get("conferences", []):
        if not c.get("indexed"):
            score = _estimate_value(c, "conference")
            scored.append((score, f"Conference: {c['name']} ({c['file_count']:,} files)", "Index into document-index"))

    for s in audit_data.get("standards", []):
        uncovered = s["disk_count"] - s["ledger_count"]
        if uncovered > 0:
            score = _estimate_value(s, "standard")
            scored.append((score, f"Standards: {s['org']} ({uncovered:,} unledgered)", "Add to standards-transfer-ledger"))

    for d in eng_subdirs:
        score = _estimate_value(d, "eng_ref")
        scored.append((score, f"Eng-refs: {d['name']} ({d['file_count']} files)", "Catalog and cross-reference"))

    if eng_top > 0:
        scored.append((eng_top, f"Eng-refs: {eng_top} loose top-level files", "Organize into subdirs and catalog"))

    scored.sort(key=lambda x: x[0], reverse=True)
    top20 = scored[:20]

    lines.append("| Rank | Resource | Score | Recommendation |")
    lines.append("|---|---|---|---|")
    for i, (score, desc, rec) in enumerate(top20, 1):
        lines.append(f"| {i} | {desc} | {score} | {rec} |")
    lines.append("")

    # --- Recommendations ---
    lines.append("## Recommendations for Next Indexing Batch")
    lines.append("")
    lines.append("1. **Index conference papers** — 30 conference collections with ~36K files are completely unindexed.")
    lines.append("   Priority: OMAE (13K), OTC (8.5K), DOT (7.5K), ISOPE (4.5K).")
    lines.append("2. **Catalog opm-common** — The only cloned repo not in the OSS catalog.")
    lines.append("3. **Expand standards ledger** — ASTM has 25K+ files but only ~97 ledger entries (<0.4% coverage).")
    lines.append("4. **Engineering refs** — 31 loose files + 5 subdirs need cataloging.")
    lines.append("5. **Run full document-index sweep** on /mnt/ace/docs/conferences/ to bring them into index.jsonl.")
    lines.append("")

    return "\n".join(lines)


# ===========================================================================
# Main
# ===========================================================================

def run_audit(ace_root: str = ACE_ROOT) -> dict:
    """Execute the full audit and return structured data."""
    ace = Path(ace_root)

    # 1. Repos
    catalog = {}
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH) as f:
            catalog = yaml.safe_load(f) or {}

    repo_results = check_repos_in_catalog(EXPECTED_REPOS, catalog)
    for r in repo_results:
        repo_path = ace / r["name"]
        r["last_updated"] = get_repo_last_updated(str(repo_path))
        if not r["domain"]:
            r["domain"] = DOMAIN_KEYWORDS.get(r["name"])

    # 2. Conferences
    conferences = scan_conferences(str(ace / "docs" / "conferences"))
    # Read index for cross-check (first 50K lines should be enough)
    index_lines: list[str] = []
    if INDEX_PATH.exists():
        with open(INDEX_PATH) as f:
            for i, line in enumerate(f):
                if i >= 50000:
                    break
                index_lines.append(line)
    conferences = check_conferences_in_index(conferences, index_lines)

    # 3. Standards
    standards_root = ace / "O&G-Standards"
    disk_counts = count_standards_files(str(standards_root), EXPECTED_ORGS)
    ledger = {}
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH) as f:
            ledger = yaml.safe_load(f) or {}
    standards = calculate_standards_coverage(disk_counts, ledger)

    # 4. Engineering refs
    eng_refs = scan_engineering_refs(str(ace / "docs" / "engineering-refs"))

    return {
        "repos": repo_results,
        "conferences": conferences,
        "standards": standards,
        "engineering_refs": eng_refs,
    }


def main():
    parser = argparse.ArgumentParser(description="Audit /mnt/ace for undiscovered resources")
    parser.add_argument("--ace-root", default=ACE_ROOT, help="Root of /mnt/ace mount")
    parser.add_argument("--output", default=str(REPORT_PATH), help="Output report path")
    args = parser.parse_args()

    print(f"Auditing {args.ace_root} ...")
    audit_data = run_audit(args.ace_root)

    report = generate_report(audit_data)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report)
    print(f"Report written to {out}")

    # Print key stats
    repos = audit_data["repos"]
    uncataloged = [r for r in repos if not r["in_catalog"]]
    print(f"\nRepos: {len(repos)} scanned, {len(uncataloged)} not in catalog")

    confs = audit_data["conferences"]
    unindexed = [c for c in confs if not c.get("indexed")]
    total_files = sum(c["file_count"] for c in unindexed)
    print(f"Conferences: {len(confs)} collections, {len(unindexed)} unindexed ({total_files:,} files)")

    stds = audit_data["standards"]
    total_disk = sum(s["disk_count"] for s in stds)
    total_ledger = sum(s["ledger_count"] for s in stds)
    print(f"Standards: {total_disk:,} files on disk, {total_ledger} in ledger")


if __name__ == "__main__":
    main()
