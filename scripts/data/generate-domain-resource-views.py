#!/usr/bin/env python3
"""
ABOUTME: Generates per-domain resource markdown pages from multiple YAML sources.
Reads: online-resource-registry.yaml, standards-transfer-ledger.yaml, registry.yaml
Writes: docs/resources/<domain>-resources.md for each domain.
Usage: uv run --no-project python scripts/data/generate-domain-resource-views.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

HUB_ROOT = Path(__file__).resolve().parents[2]

# --- Source paths ---
RESOURCE_REGISTRY_PATH = HUB_ROOT / "data/document-index/online-resource-registry.yaml"
STANDARDS_LEDGER_PATH = HUB_ROOT / "data/document-index/standards-transfer-ledger.yaml"
DOC_REGISTRY_PATH = HUB_ROOT / "data/document-index/registry.yaml"

# --- Output ---
OUTPUT_DIR = HUB_ROOT / "docs" / "resources"

# --- Domains to generate ---
TARGET_DOMAINS = [
    "orcawave", "orcaflex", "structural", "hydrodynamics",
    "pipeline", "naval_architecture", "fatigue", "subsea",
    "marine", "cfd", "oil_and_gas", "cad", "materials",
    "data_science", "visualization", "sustainability",
]


def filter_by_domain(entries: list, domain: str) -> list:
    """Filter a list of entries/standards by domain field."""
    return [e for e in entries if e.get("domain", "") == domain]


def compute_gaps(
    domain: str,
    resource_entries: list,
    standards: list,
) -> dict:
    """Compute gap analysis for a domain.

    Returns dict with:
      - undownloaded_resources: list of entries with download_status=not_started
      - standard_gaps: list of standards with status=gap
      - reference_only: count of reference-only resources
    """
    domain_resources = filter_by_domain(resource_entries, domain)
    domain_standards = filter_by_domain(standards, domain)

    undownloaded = [
        e for e in domain_resources
        if e.get("download_status") == "not_started"
    ]
    reference_only = [
        e for e in domain_resources
        if e.get("download_status") == "reference_only"
    ]
    standard_gaps = [
        s for s in domain_standards
        if s.get("status") == "gap"
    ]

    return {
        "undownloaded_resources": undownloaded,
        "standard_gaps": standard_gaps,
        "reference_only_count": len(reference_only),
    }


def generate_domain_view(
    domain: str,
    resource_entries: list,
    standards: list,
    doc_counts: dict,
) -> str:
    """Generate a markdown page for a single domain.

    Args:
        domain: domain name
        resource_entries: all entries from online-resource-registry.yaml
        standards: all standards from standards-transfer-ledger.yaml
        doc_counts: by_domain dict from registry.yaml
    """
    domain_resources = filter_by_domain(resource_entries, domain)
    domain_standards = filter_by_domain(standards, domain)
    gaps = compute_gaps(domain, resource_entries, standards)

    # Separate by type
    github_repos = [e for e in domain_resources if e.get("type") == "github_repo"]
    papers = [e for e in domain_resources if e.get("type") == "paper"]
    standard_portals = [e for e in domain_resources if e.get("type") == "standard_portal"]
    tutorials = [e for e in domain_resources if e.get("type") in ("tutorial", "course_material")]
    data_apis = [e for e in domain_resources if e.get("type") == "data_api"]
    tools = [e for e in domain_resources if e.get("type") in ("tool", "library")]
    other = [
        e for e in domain_resources
        if e.get("type") not in ("github_repo", "paper", "standard_portal", "tutorial", "course_material", "data_api", "tool", "library")
    ]

    # Doc count for this domain
    local_doc_count = doc_counts.get(domain, 0)
    # Try with hyphens if underscore version not found
    if local_doc_count == 0:
        domain_hyphen = domain.replace("_", "-")
        local_doc_count = doc_counts.get(domain_hyphen, 0)

    # Build markdown
    title = domain.replace("_", " ").title()
    lines = [
        f"# {title} Resources",
        f"",
        f"> Auto-generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d')} by generate-domain-resource-views.py",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Online Resources | {len(domain_resources)} |",
        f"| Standards | {len(domain_standards)} |",
        f"| Local Documents | {local_doc_count:,} |",
        f"| GitHub Repositories | {len(github_repos)} |",
        f"| Undownloaded Resources | {len(gaps['undownloaded_resources'])} |",
        f"| Standard Gaps | {len(gaps['standard_gaps'])} |",
        f"",
    ]

    # --- Online Resources ---
    lines.append("## Online Resources")
    lines.append("")
    if domain_resources:
        lines.append("| Name | Type | Status | Score | URL |")
        lines.append("|------|------|--------|-------|-----|")
        for e in sorted(domain_resources, key=lambda x: (-x.get("relevance_score", 0), x["name"])):
            status_icon = {
                "not_started": "⬜",
                "downloaded": "✅",
                "indexed": "📚",
                "extracted": "🔍",
                "reference_only": "📄",
            }.get(e.get("download_status", ""), "❓")
            lines.append(
                f"| {e['name']} | {e.get('type', '')} | {status_icon} {e.get('download_status', '')} "
                f"| {e.get('relevance_score', '')} | [{e['url'][:60]}...]({e['url']}) |"
                if len(e.get("url", "")) > 60
                else f"| {e['name']} | {e.get('type', '')} | {status_icon} {e.get('download_status', '')} "
                     f"| {e.get('relevance_score', '')} | [{e['url']}]({e['url']}) |"
            )
        lines.append("")
    else:
        lines.append("*No online resources cataloged for this domain.*")
        lines.append("")

    # --- Standards ---
    lines.append("## Standards")
    lines.append("")
    if domain_standards:
        lines.append("| ID | Title | Org | Status |")
        lines.append("|----|-------|-----|--------|")
        for s in sorted(domain_standards, key=lambda x: x.get("id", "")):
            status_icon = {
                "done": "✅",
                "reference": "📖",
                "gap": "❌",
                "wrk_captured": "🔧",
            }.get(s.get("status", ""), "❓")
            lines.append(
                f"| {s.get('id', '')} | {s.get('title', '')} | {s.get('org', '')} | {status_icon} {s.get('status', '')} |"
            )
        lines.append("")
    else:
        lines.append("*No standards cataloged for this domain.*")
        lines.append("")

    # --- Local Document Count ---
    lines.append("## Local Document Count")
    lines.append("")
    if local_doc_count > 0:
        lines.append(f"Total documents indexed locally: **{local_doc_count:,}**")
    else:
        lines.append("*No local documents indexed for this domain yet.*")
    lines.append("")

    # --- GitHub Repositories ---
    lines.append("## GitHub Repositories")
    lines.append("")
    if github_repos:
        for e in sorted(github_repos, key=lambda x: (-x.get("relevance_score", 0), x["name"])):
            lines.append(f"- [{e['name']}]({e['url']}) — {e.get('notes', 'No description')}")
        lines.append("")
    else:
        lines.append("*No GitHub repositories cataloged for this domain.*")
        lines.append("")

    # --- Gap Analysis ---
    lines.append("## Gap Analysis")
    lines.append("")

    undownloaded = gaps["undownloaded_resources"]
    standard_gaps = gaps["standard_gaps"]

    if undownloaded:
        lines.append(f"### Undownloaded Resources ({len(undownloaded)})")
        lines.append("")
        lines.append("These resources are cataloged but not yet downloaded locally:")
        lines.append("")
        for e in sorted(undownloaded, key=lambda x: (-x.get("relevance_score", 0), x["name"])):
            lines.append(f"- **[{e.get('relevance_score', '?')}]** [{e['name']}]({e['url']})")
            if e.get("local_backup_path"):
                lines.append(f"  - Target: `{e['local_backup_path']}`")
        lines.append("")

    if standard_gaps:
        lines.append(f"### Missing Standards ({len(standard_gaps)})")
        lines.append("")
        lines.append("Standards with status=gap (not yet acquired):")
        lines.append("")
        for s in sorted(standard_gaps, key=lambda x: x.get("id", "")):
            lines.append(f"- **{s.get('id', '')}**: {s.get('title', '')} ({s.get('org', '')})")
        lines.append("")

    if not undownloaded and not standard_gaps:
        lines.append("*No gaps identified — all resources either downloaded or reference-only.*")
        lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point — read all sources and generate domain views."""
    # Load sources
    print("Loading data sources...")
    with open(RESOURCE_REGISTRY_PATH) as f:
        resource_data = yaml.safe_load(f)
    resource_entries = resource_data.get("entries", [])
    print(f"  online-resource-registry: {len(resource_entries)} entries")

    with open(STANDARDS_LEDGER_PATH) as f:
        ledger_data = yaml.safe_load(f)
    standards = ledger_data.get("standards", [])
    print(f"  standards-transfer-ledger: {len(standards)} standards")

    with open(DOC_REGISTRY_PATH) as f:
        doc_data = yaml.safe_load(f)
    doc_counts = doc_data.get("by_domain", {})
    print(f"  registry.yaml: {len(doc_counts)} domains")

    # Generate views
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = []

    for domain in TARGET_DOMAINS:
        domain_resources = filter_by_domain(resource_entries, domain)
        domain_standards = filter_by_domain(standards, domain)
        domain_hyphen = domain.replace("_", "-")
        doc_count = doc_counts.get(domain, doc_counts.get(domain_hyphen, 0))

        # Skip domains with zero resources AND zero standards AND zero docs
        if len(domain_resources) == 0 and len(domain_standards) == 0 and doc_count == 0:
            print(f"  Skipping {domain} (no resources, standards, or docs)")
            continue

        md = generate_domain_view(
            domain=domain,
            resource_entries=resource_entries,
            standards=standards,
            doc_counts=doc_counts,
        )

        filename = f"{domain.replace('_', '-')}-resources.md"
        out_path = OUTPUT_DIR / filename
        out_path.write_text(md)
        generated.append((domain, len(domain_resources), len(domain_standards), doc_count))
        print(f"  Generated: {filename} ({len(domain_resources)} resources, {len(domain_standards)} standards, {doc_count:,} docs)")

    print(f"\n=== Domain Resource Views Generated ===")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Total views: {len(generated)}")
    print()
    print(f"{'Domain':<25} {'Resources':>10} {'Standards':>10} {'Documents':>12}")
    print(f"{'-'*25} {'-'*10} {'-'*10} {'-'*12}")
    for domain, res_count, std_count, doc_count in generated:
        print(f"{domain:<25} {res_count:>10} {std_count:>10} {doc_count:>12,}")

    return generated


if __name__ == "__main__":
    main()
