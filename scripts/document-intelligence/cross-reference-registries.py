#!/usr/bin/env python3
"""Cross-reference online and local document registries.

Compares online-resource-registry.yaml (247 online resources) against
the standards-transfer-ledger.yaml (425 local standards) to find:
- Matched pairs (same standard in both registries)
- Online-only entries (download candidates)
- Local-only entries (upload/publish candidates)
- Domain-level coverage comparison

Uses difflib.SequenceMatcher for fuzzy title matching — no external deps.

Usage:
    uv run python scripts/document-intelligence/cross-reference-registries.py
    uv run python scripts/document-intelligence/cross-reference-registries.py --threshold 0.6

Issue: #1613
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional

import yaml


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "document-index"
DEFAULT_ONLINE = DATA_DIR / "online-resource-registry.yaml"
DEFAULT_LEDGER = DATA_DIR / "standards-transfer-ledger.yaml"
DEFAULT_REGISTRY = DATA_DIR / "registry.yaml"
DEFAULT_REPORT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "document-intelligence"
    / "registry-cross-reference-report.md"
)


# ---------------------------------------------------------------------------
# Similarity / matching
# ---------------------------------------------------------------------------


def title_similarity(a: str, b: str) -> float:
    """Compute similarity between two title strings using SequenceMatcher.

    Returns a float in [0, 1].
    """
    # Normalize: lowercase, strip, remove common noise words
    def _norm(s: str) -> str:
        s = s.lower().strip()
        for noise in ["pdf", ".pdf", "(", ")", "_", "-", "  "]:
            s = s.replace(noise, " ")
        return " ".join(s.split())

    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def find_matches(
    online_entries: List[Dict],
    ledger_entries: List[Dict],
    threshold: float = 0.5,
) -> List[Dict]:
    """Find matching pairs between online and ledger entries.

    Returns a list of match dicts with keys:
    online_id, ledger_id, online_name, ledger_title, similarity.
    """
    matches = []
    # Track which ledger entries have been matched to avoid duplicates
    matched_ledger_ids = set()

    for online in online_entries:
        online_name = online.get("name", "")
        best_match = None
        best_score = 0.0

        for ledger in ledger_entries:
            if ledger["id"] in matched_ledger_ids:
                continue
            ledger_title = ledger.get("title", "")
            score = title_similarity(online_name, ledger_title)
            if score > best_score:
                best_score = score
                best_match = ledger

        if best_match and best_score >= threshold:
            matches.append({
                "online_id": online["id"],
                "ledger_id": best_match["id"],
                "online_name": online.get("name", ""),
                "ledger_title": best_match.get("title", ""),
                "similarity": round(best_score, 3),
                "online_domain": online.get("domain", ""),
                "ledger_domain": best_match.get("domain", ""),
            })
            matched_ledger_ids.add(best_match["id"])

    return matches


def find_online_only(
    online_entries: List[Dict], matches: List[Dict]
) -> List[Dict]:
    """Return online entries not matched to any local entry."""
    matched_ids = {m["online_id"] for m in matches}
    return [e for e in online_entries if e["id"] not in matched_ids]


def find_local_only(
    ledger_entries: List[Dict], matches: List[Dict]
) -> List[Dict]:
    """Return local ledger entries not matched to any online entry."""
    matched_ids = {m["ledger_id"] for m in matches}
    return [e for e in ledger_entries if e["id"] not in matched_ids]


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def _generate_report(
    online_entries: List[Dict],
    ledger_entries: List[Dict],
    registry_data: Dict,
    matches: List[Dict],
    online_only: List[Dict],
    local_only: List[Dict],
) -> str:
    """Generate a markdown cross-reference report."""
    lines = []
    lines.append("# Registry Cross-Reference Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")

    # Summary
    total_online = len(online_entries)
    total_local = len(ledger_entries)
    match_count = len(matches)
    match_rate = match_count / total_online * 100 if total_online else 0

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Online resource entries: **{total_online}**")
    lines.append(f"- Local standards (ledger): **{total_local}**")
    lines.append(f"- Matched pairs: **{match_count}** ({match_rate:.1f}% of online)")
    lines.append(f"- Online-only (download candidates): **{len(online_only)}**")
    lines.append(f"- Local-only (no online reference): **{len(local_only)}**")
    lines.append("")

    # Matched pairs
    if matches:
        lines.append("## Matched Pairs")
        lines.append("")
        lines.append("| Online Resource | Local Standard | Similarity |")
        lines.append("|---|---|---|")
        for m in sorted(matches, key=lambda x: x["similarity"], reverse=True):
            lines.append(
                f"| {m['online_name'][:50]} | {m['ledger_title'][:50]} | {m['similarity']:.2f} |"
            )
        lines.append("")

    # Top 20 online resources without local copies (download candidates)
    lines.append("## Top 20 Download Candidates (Online-Only)")
    lines.append("")
    lines.append("Online resources with no matching local standard — sorted by relevance.")
    lines.append("")
    if online_only:
        # Sort by relevance_score descending
        sorted_online = sorted(
            online_only, key=lambda x: x.get("relevance_score", 0), reverse=True
        )
        lines.append("| # | Name | Domain | Type | Relevance |")
        lines.append("|---|---|---|---|---|")
        for i, e in enumerate(sorted_online[:20], 1):
            lines.append(
                f"| {i} | {e.get('name', e['id'])[:55]} | {e.get('domain', '')} "
                f"| {e.get('type', '')} | {e.get('relevance_score', 'N/A')} |"
            )
        lines.append("")
    else:
        lines.append("*None — all online resources have local matches.*")
        lines.append("")

    # Top 20 local docs without online references (publish candidates)
    lines.append("## Top 20 Publish Candidates (Local-Only)")
    lines.append("")
    lines.append("Local standards with no matching online resource.")
    lines.append("")
    if local_only:
        lines.append("| # | ID | Title | Domain | Status |")
        lines.append("|---|---|---|---|---|")
        for i, e in enumerate(local_only[:20], 1):
            lines.append(
                f"| {i} | {e['id']} | {e.get('title', '')[:50]} "
                f"| {e.get('domain', '')} | {e.get('status', '')} |"
            )
        lines.append("")
    else:
        lines.append("*None — all local standards have online references.*")
        lines.append("")

    # Domain-level coverage comparison
    lines.append("## Domain-Level Coverage Comparison")
    lines.append("")

    # Online domains
    online_domains = Counter(e.get("domain", "unknown") for e in online_entries)
    # Ledger domains
    ledger_domains = Counter(e.get("domain", "unknown") for e in ledger_entries)
    # Registry summary domains (from registry.yaml)
    registry_domains = registry_data.get("by_domain", {})

    all_domains = sorted(
        set(online_domains.keys()) | set(ledger_domains.keys()) | set(registry_domains.keys())
    )

    lines.append("| Domain | Online Resources | Standards (Ledger) | Local Files (Registry) |")
    lines.append("|---|---|---|---|")
    for d in all_domains:
        o = online_domains.get(d, 0)
        l = ledger_domains.get(d, 0)
        r = registry_domains.get(d, 0)
        lines.append(f"| {d} | {o} | {l} | {r:,} |")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------


def run_cross_reference(
    online_path: str,
    ledger_path: str,
    registry_path: str,
    report_output: str,
    threshold: float = 0.5,
) -> Dict:
    """Run the full cross-reference pipeline."""
    # Load data
    with open(online_path) as f:
        online_data = yaml.safe_load(f)
    with open(ledger_path) as f:
        ledger_data = yaml.safe_load(f)
    with open(registry_path) as f:
        registry_data = yaml.safe_load(f)

    online_entries = online_data.get("entries", [])
    ledger_entries = ledger_data.get("standards", [])

    # Find matches
    matches = find_matches(online_entries, ledger_entries, threshold=threshold)
    online_only = find_online_only(online_entries, matches)
    local_only = find_local_only(ledger_entries, matches)

    # Generate report
    report = _generate_report(
        online_entries, ledger_entries, registry_data,
        matches, online_only, local_only,
    )
    Path(report_output).parent.mkdir(parents=True, exist_ok=True)
    with open(report_output, "w") as f:
        f.write(report)

    return {
        "match_count": len(matches),
        "online_only_count": len(online_only),
        "local_only_count": len(local_only),
        "total_online": len(online_entries),
        "total_local": len(ledger_entries),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross-reference online and local document registries"
    )
    parser.add_argument("--online", default=str(DEFAULT_ONLINE))
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--report-output", default=str(DEFAULT_REPORT))
    parser.add_argument("--threshold", type=float, default=0.5)

    args = parser.parse_args()
    result = run_cross_reference(
        online_path=args.online,
        ledger_path=args.ledger,
        registry_path=args.registry,
        report_output=args.report_output,
        threshold=args.threshold,
    )

    print(f"Cross-reference complete:")
    print(f"  Matched pairs:  {result['match_count']}")
    print(f"  Online-only:    {result['online_only_count']}")
    print(f"  Local-only:     {result['local_only_count']}")
    print(f"  Match rate:     {result['match_count'] / result['total_online'] * 100:.1f}%"
          if result["total_online"] else "")
    print(f"\nReport: {args.report_output}")


if __name__ == "__main__":
    main()
