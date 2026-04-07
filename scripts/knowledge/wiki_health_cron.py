#!/usr/bin/env python3
"""wiki-health-cron.py - Automated health checks for the LLM wiki ecosystem.

Cron job script that:
1. Runs llm-wiki lint on all domain wikis
2. Scans for cross-wiki link opportunities
3. Detects knowledge gaps
4. Writes structured report to knowledge/wikis/health-reports/

Usage:
    uv run scripts/knowledge/wiki_health_cron.py
"""

import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WIKIS_DIR = REPO_ROOT / "knowledge" / "wikis"
REPORTS_DIR = WIKIS_DIR / "health-reports"
LINK_RE = re.compile(r']\(([^)]+\.md[^)]*)\)')
MD_FILE_RE = re.compile(r'\.md$')


def get_wiki_domains():
    """List all wiki domains."""
    if not WIKIS_DIR.exists():
        return []
    return sorted([d.name for d in WIKIS_DIR.iterdir()
                   if d.is_dir() and d.name != "health-reports"])


def run_lint(domain):
    """Run lint checks on a wiki domain."""
    wiki_root = WIKIS_DIR / domain
    wiki_dir = wiki_root / "wiki"

    if not wiki_root.exists():
        return {"domain": domain, "status": "missing", "page_count": 0,
                "source_count": 0, "entity_count": 0, "concept_count": 0,
                "link_density": 0.0, "issues": [{"severity": "critical",
                "category": "missing", "message": f"Wiki directory not found"}]}

    issues = []

    # Orphan check
    issues.extend(_check_orphans(wiki_dir))

    # Empty check
    issues.extend(_check_empty(wiki_dir))

    # Index check
    issues.extend(_check_index(wiki_dir))

    # Log check
    issues.extend(_check_log(wiki_dir))

    # Link density
    density = _check_density(wiki_dir)
    if density < 1.0:
        stats = _count_pages(wiki_dir)
        if stats["total"] > 3:
            issues.append({"severity": "warning", "category": "cross-refs",
                          "message": f"Low link density ({density:.1f} avg/page)"})

    stats = _count_pages(wiki_dir)
    status = "healthy" if not issues else "has_issues"

    return {
        "domain": domain, "status": status,
        "page_count": stats["total"],
        "source_count": stats["sources"],
        "entity_count": stats["entities"],
        "concept_count": stats["concepts"],
        "link_density": round(density, 2),
        "issues": issues,
        "issue_summary": dict(Counter(i["category"] for i in issues))
    }


def _check_orphans(wiki_dir):
    """Find pages with no inbound links from other wiki pages."""
    if not wiki_dir.exists():
        return []

    all_pages = {}
    for cat in ["entities", "concepts", "sources", "comparisons"]:
        subdir = wiki_dir / cat
        if subdir.exists():
            for md_file in subdir.glob("*.md"):
                all_pages[md_file.name] = str(md_file)

    if len(all_pages) <= 1:
        return []

    linked = set()
    for subdir_name in ["entities", "concepts", "sources", "comparisons"]:
        subdir = wiki_dir / subdir_name
        if subdir.exists():
            for md_file in subdir.glob("*.md"):
                links = LINK_RE.findall(md_file.read_text())
                for link in links:
                    linked.add(os.path.basename(link))

    # Index also links to pages
    index = wiki_dir / "index.md"
    if index.exists():
        links = LINK_RE.findall(index.read_text())
        for link in links:
            linked.add(os.path.basename(link))

    orphans = []
    for page_name in sorted(set(all_pages.keys()) - linked):
        if len(orphans) >= 5:
            break
        orphans.append({"severity": "warning", "category": "orphan",
                       "page": all_pages[page_name],
                       "message": f"No inbound links to {page_name}"})
    return orphans


def _check_empty(wiki_dir):
    """Find pages that are placeholder-only."""
    if not wiki_dir.exists():
        return []

    empty = []
    for cat in ["entities", "concepts", "sources"]:
        subdir = wiki_dir / cat
        if subdir.exists():
            for md_file in subdir.glob("*.md"):
                content = md_file.read_text()
                lines = [l for l in content.splitlines()
                        if l.strip() and not l.startswith("---")
                        and not l.startswith(">") and not l.startswith("#")]
                meaningful = [l for l in lines
                            if "auto-generated" not in l.lower()
                            and "placeholder" not in l.lower()]
                if not meaningful:
                    empty.append({"severity": "info", "category": "empty",
                                "page": str(md_file),
                                "message": "Page has no meaningful content"})
    return empty[:3]


def _check_index(wiki_dir):
    """Check index.md exists and has YAML frontmatter."""
    index = wiki_dir / "index.md"
    issues = []
    if not index.exists():
        issues.append({"severity": "critical", "category": "index",
                      "message": "index.md missing"})
    else:
        content = index.read_text()
        if not content.startswith("---"):
            issues.append({"severity": "warning", "category": "index",
                          "message": "Missing YAML frontmatter"})
    return issues


def _check_log(wiki_dir):
    """Check log.md exists."""
    log = wiki_dir / "log.md"
    issues = []
    if not log.exists():
        issues.append({"severity": "critical", "category": "log",
                      "message": "log.md missing"})
    return issues


def _check_density(wiki_dir):
    """Calculate average links per page."""
    if not wiki_dir.exists():
        return 0.0

    total = 0
    pages = 0
    for md_file in wiki_dir.rglob("*.md"):
        total += len(LINK_RE.findall(md_file.read_text()))
        pages += 1

    return total / pages if pages > 0 else 0.0


def _count_pages(wiki_dir):
    """Count pages by category."""
    counts = {"total": 0, "sources": 0, "entities": 0, "concepts": 0}

    for cat in ["sources", "entities", "concepts"]:
        subdir = wiki_dir / cat
        if subdir.exists():
            count = len(list(subdir.glob("*.md")))
            counts[cat] = count
            counts["total"] += count

    # Add index, log, overview
    for f in wiki_dir.iterdir():
        if f.is_file() and f.suffix == ".md":
            counts["total"] += 1

    return counts


def scan_cross_links():
    """Find potential cross-wiki links between domain wikis."""
    domains = get_wiki_domains()
    suggestions = []

    # Build entity index
    entity_index = {}
    for domain in domains:
        wiki_dir = WIKIS_DIR / domain / "wiki" / "entities"
        if wiki_dir.exists():
            for md_file in wiki_dir.glob("*.md"):
                content = md_file.read_text()
                m = re.search(r'title: "(.*?)"', content)
                title = m.group(1) if m else md_file.stem.replace("-", " ").title()
                slug = md_file.stem.lower()
                entity_index[slug] = {
                    "source_wiki": domain,
                    "title": title,
                    "path": str(md_file.relative_to(REPO_ROOT))
                }
                for word in md_file.stem.split("-"):
                    if len(word) > 3:
                        if word.lower() not in entity_index:
                            entity_index[word.lower()] = entity_index[slug]

    # Scan all wiki pages for mentions of entities in OTHER wikis
    for domain in domains:
        wiki_dir = WIKIS_DIR / domain / "wiki"
        if not wiki_dir.exists():
            continue

        for md_file in wiki_dir.rglob("*.md"):
            content = md_file.read_text().lower()
            for term, info in entity_index.items():
                if info["source_wiki"] == domain:
                    continue
                if term in content and len(term) > 3:
                    suggestions.append({
                        "from_wiki": domain,
                        "from_page": str(md_file.relative_to(REPO_ROOT)),
                        "mentions": term,
                        "links_to_wiki": info["source_wiki"],
                        "links_to_page": info["path"]
                    })

    return suggestions[:20]


def detect_knowledge_gaps():
    """Find concepts mentioned in sources but lacking concept pages."""
    domains = get_wiki_domains()
    gaps = []

    for domain in domains:
        wiki_dir = WIKIS_DIR / domain / "wiki"
        if not wiki_dir.exists():
            continue

        concept_slugs = set()
        concepts_dir = wiki_dir / "concepts"
        if concepts_dir.exists():
            for f in concepts_dir.glob("*.md"):
                concept_slugs.add(f.stem.lower())

        sources_dir = wiki_dir / "sources"
        if not sources_dir.exists():
            continue

        for md_file in sources_dir.glob("*.md"):
            content = md_file.read_text()
            mentions = re.findall(r'\[\[([^\]]+)\]\]', content)
            for mention in mentions:
                concept_slug = mention.strip("[]").lower().replace(" ", "-")
                if concept_slug not in concept_slugs:
                    gaps.append({
                        "wiki": domain,
                        "source_page": str(md_file.relative_to(REPO_ROOT)),
                        "missing_concept": mention.strip("[]")
                    })

    return gaps[:10]


def main():
    """Run all health checks and write report."""
    now = datetime.utcnow()
    domains = get_wiki_domains()

    if not domains:
        print("[ERROR] No wiki domains found")
        return 1

    print(f"[wiki-health] Checking {len(domains)} wikis: {', '.join(domains)}")

    # Lint each wiki
    results = []
    for domain in domains:
        print(f"  Linting {domain}...")
        result = run_lint(domain)
        results.append(result)

    # Cross-link scan
    print("  Scanning cross-wiki links...")
    cross_links = scan_cross_links()

    # Knowledge gap detection
    print("  Detecting knowledge gaps...")
    gaps = detect_knowledge_gaps()

    # Summary
    total_issues = sum(len(r["issues"]) for r in results)
    total_pages = sum(r.get("page_count", 0) for r in results
                     if isinstance(r.get("page_count"), int))

    # Write JSON report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M UTC"),
        "wikis_checked": len(domains),
        "total_pages": total_pages,
        "total_issues": total_issues,
        "domain_results": results,
        "cross_link_suggestions": cross_links,
        "knowledge_gaps": gaps
    }
    report_path = REPORTS_DIR / f"health-{now.strftime('%Y-%m-%d')}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Write markdown summary
    summary_path = REPORTS_DIR / f"health-{now.strftime('%Y-%m-%d')}.md"
    lines = [
        f"# Wiki Health Report - {now.strftime('%Y-%m-%d')}",
        "",
        "## Summary",
        "",
        f"- Wikis checked: {len(domains)}",
        f"- Total pages: {total_pages}",
        f"- Total issues: {total_issues}",
        f"- Cross-link suggestions: {len(cross_links)}",
        f"- Knowledge gaps: {len(gaps)}",
        ""
    ]

    for r in results:
        status = "OK" if r["status"] == "healthy" else "ISSUES"
        lines.append(f"## {r['domain']} - {status}")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        for key in ["page_count", "source_count", "entity_count",
                    "concept_count", "link_density"]:
            val = r.get(key, "N/A")
            lines.append(f"| {key.replace('_', ' ').title()} | {val} |")
        lines.append("")
        if r["issues"]:
            lines.append("### Issues")
            lines.append("")
            for issue in r["issues"][:5]:
                sev = issue.get("severity", "").upper()
                cat = issue.get("category", "")
                msg = issue.get("message", "")
                page = issue.get("page", "")
                lines.append(f"- [{sev}] **{cat}**: {msg} ({page})")
            lines.append("")

    if cross_links:
        lines.append("## Cross-Wiki Link Suggestions")
        lines.append("")
        lines.append("| From Wiki | Page | Mentions | Links To Wiki | Page |")
        lines.append("|-----------|------|----------|---------------|------|")
        for cl in cross_links[:10]:
            from_p = cl["from_page"].split("/")[-1]
            to_p = cl["links_to_page"].split("/")[-1]
            lines.append(f"| {cl['from_wiki']} | {from_p} | "
                        f"{cl['mentions']} | {cl['links_to_wiki']} | {to_p} |")
        lines.append("")

    if gaps:
        lines.append("## Knowledge Gaps")
        lines.append("")
        for g in gaps[:5]:
            src = g["source_page"].split("/")[-1]
            lines.append(f"- [{g['wiki']}] {src} mentions missing concept: "
                        f"**{g['missing_concept']}**")
        lines.append("")

    summary_path.write_text("\n".join(lines))

    # Console output
    print()
    print(f"[wiki-health] Report: {report_path.relative_to(REPO_ROOT)}")
    print(f"[wiki-health] Summary: {summary_path.relative_to(REPO_ROOT)}")
    print()
    print(f"{'Domain':<25} {'Status':<10} {'Pages':<8} {'Issues':<8} "
          f"{'Links/pg':<10}")
    print("-" * 65)
    for r in results:
        print(f"{r['domain']:<25} {r['status']:<10} "
              f"{r.get('page_count', 0):<8} "
              f"{len(r.get('issues', [])):<8} "
              f"{r.get('link_density', 0.0):<10.1f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
