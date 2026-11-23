#!/usr/bin/env python3
"""
ABOUTME: Surface data-intelligence artifacts for a /work session context.
ABOUTME: Queries standards-transfer-ledger, worked_examples, test_vectors, and
ABOUTME: doc-intelligence registry to provide domain-relevant briefing material
ABOUTME: when starting work on a WRK item.
ABOUTME: Issue: #1321 (WRK-5126)

Usage:
    python data-intelligence-context.py --domain marine
    python data-intelligence-context.py --domain pipeline --wrk-id WRK-499
    python data-intelligence-context.py --category engineering --subcategory cathodic-protection
    python data-intelligence-context.py --wrk-file .claude/work-queue/working/WRK-5015.md
    python data-intelligence-context.py --domain marine --format json

Outputs a concise briefing of relevant data intelligence for the session.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Resolve workspace root
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_HUB = SCRIPT_DIR.parent.parent

# Data paths
LEDGER_PATH = WORKSPACE_HUB / "data" / "document-index" / "standards-transfer-ledger.yaml"
WORKED_EXAMPLES_PATH = WORKSPACE_HUB / "data" / "doc-intelligence" / "worked_examples.jsonl"
TEST_VECTORS_INDEX = WORKSPACE_HUB / "tests" / "fixtures" / "test_vectors" / "INDEX.yaml"
REGISTRY_PATH = WORKSPACE_HUB / "data" / "document-index" / "registry.yaml"

# Mapping from WRK subcategory / category to standards-ledger domains.
# The ledger uses: materials, structural, pipeline, process, marine, cad,
# installation, cathodic-protection, regulatory, drilling
# WRK items use category + subcategory. This map bridges the gap.
SUBCATEGORY_TO_DOMAIN: dict[str, str] = {
    "cathodic-protection": "cathodic-protection",
    "pipeline": "pipeline",
    "marine": "marine",
    "structural": "structural",
    "materials": "materials",
    "process": "process",
    "cad": "cad",
    "installation": "installation",
    "regulatory": "regulatory",
    "drilling": "drilling",
    "naval-architecture": "marine",
    "mooring": "marine",
    "subsea": "pipeline",
    "riser": "pipeline",
    "energy-economics": "process",
}


def _safe_yaml_load(path: Path) -> Any:
    """Load YAML without hard PyYAML dependency; fall back to regex parsing."""
    try:
        import yaml
        with open(path, encoding="utf-8", errors="replace") as f:
            return yaml.safe_load(f)
    except ImportError:
        # Minimal fallback — won't cover all cases but handles ledger
        return None


def _parse_wrk_frontmatter(wrk_path: Path) -> dict[str, str]:
    """Extract key frontmatter fields from a WRK markdown file."""
    text = wrk_path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    raw = m.group(1)
    result: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip("'\"").strip("[]")
            if key in ("category", "subcategory", "id", "title"):
                result[key] = val
    return result


def resolve_domain(
    domain: Optional[str],
    category: Optional[str],
    subcategory: Optional[str],
    wrk_file: Optional[str],
) -> tuple[str, dict[str, str]]:
    """
    Resolve a single domain string from the various input channels.
    Returns (domain, wrk_meta).
    """
    wrk_meta: dict[str, str] = {}

    # If wrk_file provided, extract category/subcategory from frontmatter
    if wrk_file:
        wrk_path = Path(wrk_file)
        if not wrk_path.is_absolute():
            wrk_path = WORKSPACE_HUB / wrk_path
        if wrk_path.exists():
            wrk_meta = _parse_wrk_frontmatter(wrk_path)
            if not category:
                category = wrk_meta.get("category")
            if not subcategory:
                subcategory = wrk_meta.get("subcategory")

    # Direct domain wins
    if domain:
        return domain, wrk_meta

    # Try subcategory mapping
    if subcategory and subcategory in SUBCATEGORY_TO_DOMAIN:
        return SUBCATEGORY_TO_DOMAIN[subcategory], wrk_meta

    # Try category mapping (less specific)
    if category and category in SUBCATEGORY_TO_DOMAIN:
        return SUBCATEGORY_TO_DOMAIN[category], wrk_meta

    return "", wrk_meta


# ---------------------------------------------------------------------------
# Data queries
# ---------------------------------------------------------------------------


def query_standards(domain: str, wrk_id: Optional[str] = None) -> dict[str, Any]:
    """Find standards matching the domain from the ledger."""
    data = _safe_yaml_load(LEDGER_PATH)
    if not data or "standards" not in data:
        return {"error": "ledger not available", "standards": [], "summary": {}}

    standards = data["standards"]
    matched = [s for s in standards if s.get("domain") == domain]

    # Group by status
    by_status: dict[str, int] = {}
    for s in matched:
        st = s.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1

    # Find specific WRK-linked standards
    wrk_linked = []
    if wrk_id:
        wrk_linked = [s for s in standards if s.get("wrk_id") == wrk_id]

    # Top reference standards (for briefing — limit to 10)
    top_refs = []
    for s in matched[:10]:
        top_refs.append({
            "id": s.get("id", "?"),
            "title": s.get("title", "?"),
            "status": s.get("status", "?"),
            "wrk_id": s.get("wrk_id"),
            "notes": (s.get("notes", "") or "")[:120],
        })

    return {
        "domain": domain,
        "total_in_domain": len(matched),
        "by_status": by_status,
        "wrk_linked": [
            {"id": s.get("id"), "title": s.get("title"), "wrk_id": s.get("wrk_id")}
            for s in wrk_linked
        ],
        "top_standards": top_refs,
        "gap_count": by_status.get("gap", 0),
    }


def query_worked_examples(domain: str) -> dict[str, Any]:
    """Find worked examples matching the domain."""
    if not WORKED_EXAMPLES_PATH.exists():
        return {"error": "worked_examples.jsonl not found", "count": 0, "samples": []}

    matched = []
    total = 0
    # Domain mapping: worked_examples uses 'naval-architecture' for marine domain
    domain_aliases = {domain}
    if domain == "marine":
        domain_aliases.add("naval-architecture")
    elif domain == "naval-architecture":
        domain_aliases.add("marine")

    with open(WORKED_EXAMPLES_PATH, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                rec = json.loads(line)
                total += 1
                if rec.get("domain") in domain_aliases:
                    matched.append(rec)
            except json.JSONDecodeError:
                continue

    # Summarize
    sources: dict[str, int] = {}
    for r in matched:
        src = r.get("source", {})
        doc = src.get("document") or src.get("manifest") or "unknown"
        sources[doc] = sources.get(doc, 0) + 1

    # Top sources
    top_sources = sorted(sources.items(), key=lambda x: -x[1])[:5]

    return {
        "domain": domain,
        "count": len(matched),
        "total_in_corpus": total,
        "top_sources": [{"document": d, "count": c} for d, c in top_sources],
    }


def query_test_vectors(domain: str) -> dict[str, Any]:
    """Check curated test vectors available for the domain."""
    data = _safe_yaml_load(TEST_VECTORS_INDEX)
    if not data or "domains" not in data:
        return {"available": False, "count": 0}

    dom_info = data.get("domains", {}).get(domain, {})
    if not dom_info:
        return {"available": False, "count": 0, "domain": domain}

    return {
        "available": True,
        "domain": domain,
        "count": dom_info.get("count", 0),
        "fixture_file": dom_info.get("fixture_file", ""),
        "gold": dom_info.get("gold", 0),
        "silver": dom_info.get("silver", 0),
        "bronze": dom_info.get("bronze", 0),
    }


def query_doc_registry(domain: str) -> dict[str, Any]:
    """Get document index statistics for the domain."""
    data = _safe_yaml_load(REGISTRY_PATH)
    if not data:
        return {"available": False}

    by_domain = data.get("by_domain", {})
    count = by_domain.get(domain, 0)

    return {
        "available": count > 0,
        "domain": domain,
        "document_count": count,
        "total_documents": data.get("total_docs", 0),
        "total_summaries": data.get("total_summaries", 0),
    }


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def format_text(
    domain: str,
    standards: dict[str, Any],
    examples: dict[str, Any],
    vectors: dict[str, Any],
    registry: dict[str, Any],
    wrk_meta: dict[str, str],
) -> str:
    """Format a human-readable briefing for the terminal."""
    lines: list[str] = []
    lines.append("## Data Intelligence Briefing")
    if wrk_meta.get("id"):
        lines.append(f"  WRK: {wrk_meta.get('id')} — {wrk_meta.get('title', '')}")
    lines.append(f"  Domain: {domain}")
    lines.append("")

    # Standards
    if standards.get("total_in_domain", 0) > 0:
        lines.append(f"  Standards ({standards['total_in_domain']} in '{domain}'):")
        for status, count in sorted(standards.get("by_status", {}).items()):
            lines.append(f"    {status}: {count}")
        if standards.get("gap_count", 0) > 0:
            lines.append(f"    >> {standards['gap_count']} gaps available for new WRK items")
        if standards.get("wrk_linked"):
            lines.append("    WRK-linked standards:")
            for s in standards["wrk_linked"][:5]:
                lines.append(f"      {s['id']}: {s['title']} (WRK: {s['wrk_id']})")
        if standards.get("top_standards"):
            lines.append("    Key standards:")
            for s in standards["top_standards"][:5]:
                tag = f" [WRK: {s['wrk_id']}]" if s.get("wrk_id") else ""
                lines.append(f"      {s['id']}: {s['title']}{tag}")
    else:
        lines.append(f"  Standards: no entries for domain '{domain}'")
    lines.append("")

    # Worked examples
    if examples.get("count", 0) > 0:
        lines.append(f"  Worked Examples ({examples['count']} records):")
        for src in examples.get("top_sources", []):
            lines.append(f"    {src['document']}: {src['count']} examples")
    else:
        lines.append(f"  Worked Examples: none for domain '{domain}'")
    lines.append("")

    # Test vectors
    if vectors.get("available"):
        lines.append(f"  Test Vectors ({vectors['count']} curated):")
        lines.append(f"    Gold: {vectors.get('gold', 0)} | Silver: {vectors.get('silver', 0)} | Bronze: {vectors.get('bronze', 0)}")
        lines.append(f"    Fixture: {vectors.get('fixture_file', 'N/A')}")
    else:
        lines.append(f"  Test Vectors: none curated for domain '{domain}'")
    lines.append("")

    # Document index
    if registry.get("available"):
        lines.append(f"  Document Index: {registry['document_count']:,} pages in '{domain}'")
        lines.append(f"    (of {registry['total_documents']:,} total, {registry['total_summaries']:,} summarized)")
    else:
        lines.append(f"  Document Index: no entries for domain '{domain}'")

    return "\n".join(lines)


def format_json(
    domain: str,
    standards: dict[str, Any],
    examples: dict[str, Any],
    vectors: dict[str, Any],
    registry: dict[str, Any],
    wrk_meta: dict[str, str],
) -> str:
    """Format as JSON for machine consumption."""
    return json.dumps(
        {
            "domain": domain,
            "wrk_meta": wrk_meta,
            "standards": standards,
            "worked_examples": examples,
            "test_vectors": vectors,
            "document_index": registry,
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Data intelligence context for /work sessions (WRK-5126)"
    )
    parser.add_argument("--domain", help="Domain to query (e.g. marine, pipeline, structural)")
    parser.add_argument("--category", help="WRK category (e.g. engineering)")
    parser.add_argument("--subcategory", help="WRK subcategory (e.g. cathodic-protection)")
    parser.add_argument("--wrk-file", help="Path to WRK .md file (auto-extracts domain)")
    parser.add_argument("--wrk-id", help="WRK ID to find linked standards (e.g. WRK-499)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    if not any([args.domain, args.category, args.subcategory, args.wrk_file]):
        parser.print_help()
        print("\nError: at least one of --domain, --category, --subcategory, or --wrk-file required",
              file=sys.stderr)
        return 1

    domain, wrk_meta = resolve_domain(args.domain, args.category, args.subcategory, args.wrk_file)

    if not domain:
        print(f"Could not resolve domain from inputs: category={args.category}, "
              f"subcategory={args.subcategory}, wrk_file={args.wrk_file}", file=sys.stderr)
        print("## Data Intelligence Briefing\n  Domain: (unresolved — no matching domain)")
        return 0  # non-fatal: just no intel to show

    # Run queries
    standards = query_standards(domain, args.wrk_id)
    examples = query_worked_examples(domain)
    vectors = query_test_vectors(domain)
    registry = query_doc_registry(domain)

    # Format output
    if args.format == "json":
        print(format_json(domain, standards, examples, vectors, registry, wrk_meta))
    else:
        print(format_text(domain, standards, examples, vectors, registry, wrk_meta))

    return 0


if __name__ == "__main__":
    sys.exit(main())
