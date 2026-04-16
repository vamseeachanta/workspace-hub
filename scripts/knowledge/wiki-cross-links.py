#!/usr/bin/env python3
"""wiki-cross-links.py — Automated cross-wiki link discovery.

Scans all wiki directories for entity/concept pages, extracts titles, tags,
and content keywords, then compares across wikis for concept overlap using
fuzzy matching on titles and tag intersection. Outputs discovered links in
the same format as knowledge/wikis/cross-links.md.

Phase 2 adds provenance-based (shared sources), entity co-reference,
and standards-chain link types, plus JSONL output (#2068).

Usage:
    uv run scripts/knowledge/wiki-cross-links.py --dry-run          # report only
    uv run scripts/knowledge/wiki-cross-links.py --apply            # update pages
    uv run scripts/knowledge/wiki-cross-links.py --wikis engineering,marine-engineering
    uv run scripts/knowledge/wiki-cross-links.py --min-score 0.4    # tune sensitivity
    uv run scripts/knowledge/wiki-cross-links.py --jsonl             # emit cross-links.jsonl

Issue: #2011, #2068
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]  # workspace-hub root
WIKIS_DIR = REPO_ROOT / "knowledge" / "wikis"

# Subdirectories that contain linkable content pages
CONTENT_SUBDIRS = ("concepts", "entities", "standards", "workflows")

# Skip these wikis by default (non-domain wikis)
SKIP_WIKIS = {"health-reports", "personal"}

# Minimum similarity score to consider a cross-link (0.0 to 1.0)
DEFAULT_MIN_SCORE = 0.35


# ── Data structures ──────────────────────────────────────────────────────────


@dataclass
class WikiPage:
    """Represents a single wiki page with extracted metadata."""

    wiki: str  # e.g. "engineering"
    category: str  # e.g. "concepts", "entities"
    slug: str  # e.g. "cathodic-protection-design"
    title: str  # from frontmatter
    tags: Set[str] = field(default_factory=set)
    keywords: Set[str] = field(default_factory=set)
    sources: Set[str] = field(default_factory=set)  # frontmatter sources
    entities: Set[str] = field(default_factory=set)  # entity co-references
    existing_cross_links: Set[str] = field(default_factory=set)
    file_path: Path = field(default_factory=Path)

    @property
    def page_id(self) -> str:
        """Unique identifier: wiki/category/slug."""
        return f"{self.wiki}/{self.category}/{self.slug}"

    @property
    def short_id(self) -> str:
        """Short form used in cross-links.md: category/slug."""
        return f"{self.category}/{self.slug}"


@dataclass
class CrossLink:
    """A discovered cross-wiki link between two pages."""

    source: WikiPage
    target: WikiPage
    score: float
    link_type: str  # human-readable reason
    link_types: List[str] = field(default_factory=list)  # machine-readable types

    def __hash__(self):
        # Deduplicate: A->B and B->A are different entries
        return hash((self.source.page_id, self.target.page_id))

    def __eq__(self, other):
        return (
            self.source.page_id == other.source.page_id
            and self.target.page_id == other.target.page_id
        )


# ── Parsing ──────────────────────────────────────────────────────────────────


def _parse_yaml_list(fm_text: str, key: str) -> List[str]:
    """Parse a YAML list field from frontmatter (inline or multi-line)."""
    # Inline format: key: [a, b, c]
    inline_match = re.search(rf"^{key}:\s*\[(.*?)\]", fm_text, re.MULTILINE)
    if inline_match:
        raw = inline_match.group(1)
        return [t.strip().strip("\"'") for t in raw.split(",") if t.strip()]

    # Multi-line format: key:\n  - a\n  - b
    block_match = re.search(
        rf"^{key}:\s*\n((?:\s+-\s+.*\n?)+)", fm_text, re.MULTILINE
    )
    if block_match:
        return [
            t.strip().lstrip("- ").strip("\"'")
            for t in block_match.group(1).strip().split("\n")
            if t.strip()
        ]

    return []


def parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter fields from markdown text."""
    result = {"title": "", "tags": [], "sources": []}
    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        return result

    fm_text = fm_match.group(1)

    # Title
    title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', fm_text, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # Tags — handle both [a, b] and - a\n- b formats
    result["tags"] = _parse_yaml_list(fm_text, "tags")

    # Sources — same two formats
    result["sources"] = _parse_yaml_list(fm_text, "sources")

    return result


def extract_keywords(text: str) -> Set[str]:
    """Extract meaningful keywords from page body (headings + bold terms)."""
    keywords = set()

    # Extract headings
    for match in re.finditer(r"^#{1,4}\s+(.+)$", text, re.MULTILINE):
        heading = match.group(1).strip()
        # Normalize heading to lowercase words
        words = re.findall(r"[a-z][a-z0-9-]+", heading.lower())
        keywords.update(words)

    # Extract bold terms
    for match in re.finditer(r"\*\*([^*]+)\*\*", text):
        term = match.group(1).strip().lower()
        words = re.findall(r"[a-z][a-z0-9-]+", term)
        keywords.update(words)

    return keywords


# Common short uppercase words that are NOT meaningful entities
_ENTITY_STOPWORDS = frozenset({
    "THE", "AND", "FOR", "NOT", "BUT", "ARE", "WAS", "HAS", "HAD", "ITS",
    "CAN", "MAY", "USE", "SET", "GET", "ALL", "NEW", "OLD", "SEE", "RUN",
    "YES", "KEY", "TOP", "END", "ADD", "FIT", "MAX", "MIN", "REF", "PDF",
    "CSV", "PNG", "JPG", "GIF", "SVG", "URL", "CLI", "CWD", "TMP",
    "TODO", "NOTE", "THEN", "WHEN", "WITH", "FROM", "EACH", "ALSO",
    "MUST", "WILL", "DOES", "THIS", "THAT", "THEY", "USED", "USES",
    "NEXT", "LAST", "FILE", "PAGE", "LINK", "TEXT", "CODE", "DATA",
    "NAME", "TYPE", "LEFT", "TRUE", "NULL", "NONE",
})


def extract_entities(text: str) -> Set[str]:
    """Extract named entities from page body for co-reference linking.

    Looks for:
    - CamelCase tool names: OrcaFlex, BEMRosetta, DeepLines
    - Standards codes: DNV-RP-C205, API-579, ISO-19901-7
    - Uppercase acronyms (3+ chars): OCIMF, SIGTTO, ASTM, FPSO
    - Standards references: "API 2SK", "ISO 19901"
    """
    entities = set()

    # CamelCase tool/product names (e.g. OrcaFlex, BEMRosetta, DeepLines)
    for match in re.finditer(r"\b([A-Z][a-z]+[A-Z][A-Za-z0-9]*)\b", text):
        entities.add(match.group(1))

    # Hyphenated standard codes: DNV-RP-C205, DNV-OS-E301, API-579-1
    for match in re.finditer(
        r"\b([A-Z]{2,}-(?:[A-Z]{2,}-)?[A-Z0-9][A-Za-z0-9-]*)\b", text
    ):
        entities.add(match.group(1))

    # Uppercase acronyms (3+ chars, not common words)
    for match in re.finditer(r"\b([A-Z]{3,})\b", text):
        acronym = match.group(1)
        if acronym not in _ENTITY_STOPWORDS:
            entities.add(acronym)

    # Standards references with space: "API 2SK", "ISO 19901", "ASME B31"
    for match in re.finditer(r"\b([A-Z]{2,})\s+(\d{2,}[A-Za-z0-9]*)\b", text):
        prefix = match.group(1)
        if prefix not in _ENTITY_STOPWORDS:
            entities.add(f"{prefix} {match.group(2)}")

    return entities


def extract_existing_cross_links(text: str, wiki_name: str) -> Set[str]:
    """Extract existing cross-wiki link targets from a page."""
    links = set()
    # Match relative path links to other wikis
    # Pattern: (../../../other-wiki/wiki/category/slug.md)
    for match in re.finditer(
        r"\.\./(?:\.\./)*([a-z-]+)/wiki/([a-z-]+)/([a-z0-9-]+)\.md", text
    ):
        target_wiki = match.group(1)
        target_category = match.group(2)
        target_slug = match.group(3)
        if target_wiki != wiki_name:
            links.add(f"{target_wiki}/{target_category}/{target_slug}")
    return links


def scan_wiki(wiki_dir: Path, wiki_name: str) -> List[WikiPage]:
    """Scan a wiki directory and return all content pages."""
    pages = []
    wiki_content_dir = wiki_dir / "wiki"

    if not wiki_content_dir.is_dir():
        return pages

    for subdir_name in CONTENT_SUBDIRS:
        subdir = wiki_content_dir / subdir_name
        if not subdir.is_dir():
            continue

        for md_file in sorted(subdir.glob("*.md")):
            slug = md_file.stem
            try:
                text = md_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            fm = parse_frontmatter(text)
            title = fm["title"] or slug.replace("-", " ").title()
            tags = {t.lower() for t in fm["tags"]}
            keywords = extract_keywords(text)
            sources = {s.lower() for s in fm["sources"] if s}
            entities = extract_entities(text)
            existing = extract_existing_cross_links(text, wiki_name)

            page = WikiPage(
                wiki=wiki_name,
                category=subdir_name,
                slug=slug,
                title=title,
                tags=tags,
                keywords=keywords,
                sources=sources,
                entities=entities,
                existing_cross_links=existing,
                file_path=md_file,
            )
            pages.append(page)

    return pages


# ── Matching ─────────────────────────────────────────────────────────────────


def slug_similarity(a: str, b: str) -> float:
    """Fuzzy similarity between two slugs (hyphenated names)."""
    return SequenceMatcher(None, a, b).ratio()


def title_similarity(a: str, b: str) -> float:
    """Fuzzy similarity between two titles."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def tag_overlap(a: Set[str], b: Set[str]) -> float:
    """Jaccard similarity of tag sets."""
    if not a or not b:
        return 0.0
    intersection = a & b
    union = a | b
    return len(intersection) / len(union) if union else 0.0


def keyword_overlap(a: Set[str], b: Set[str]) -> float:
    """Jaccard similarity of keyword sets."""
    if not a or not b:
        return 0.0
    intersection = a & b
    union = a | b
    return len(intersection) / len(union) if union else 0.0


def entity_overlap(a: Set[str], b: Set[str]) -> float:
    """Jaccard similarity of entity sets."""
    if not a or not b:
        return 0.0
    intersection = a & b
    union = a | b
    return len(intersection) / len(union) if union else 0.0


def source_overlap_score(a: Set[str], b: Set[str]) -> Tuple[float, Set[str]]:
    """Compute provenance score from shared sources.

    Returns (score, shared_sources). Score is 0.3 per shared source, capped at 0.6.
    """
    if not a or not b:
        return 0.0, set()
    shared = a & b
    if not shared:
        return 0.0, set()
    return min(len(shared) * 0.3, 0.6), shared


def compute_similarity(page_a: WikiPage, page_b: WikiPage) -> Tuple[float, str]:
    """Compute weighted similarity score between two pages from different wikis.

    Returns (score, reason_string).

    Scoring factors:
      - Slug similarity (0.25 weight)
      - Title similarity (0.25 weight)
      - Tag overlap (0.20 weight)
      - Keyword overlap (0.10 weight)
      - Entity co-reference overlap (0.20 weight)
      - Provenance bonus: shared sources add up to +0.6
      - Standards-chain bonus: standards pages get boosted tag weight
    """
    s_slug = slug_similarity(page_a.slug, page_b.slug)
    s_title = title_similarity(page_a.title, page_b.title)
    s_tags = tag_overlap(page_a.tags, page_b.tags)
    s_keywords = keyword_overlap(page_a.keywords, page_b.keywords)
    s_entities = entity_overlap(page_a.entities, page_b.entities)

    # Standards-chain boost: if both pages are in standards/ category,
    # tag overlap is a stronger signal (standards reference each other)
    tag_weight = 0.20
    if page_a.category == "standards" and page_b.category == "standards":
        tag_weight = 0.30

    # Weighted composite score
    score = (
        (s_slug * 0.25)
        + (s_title * 0.25)
        + (s_tags * tag_weight)
        + (s_keywords * 0.10)
        + (s_entities * 0.20)
    )

    # Provenance bonus: shared sources are a strong signal
    s_provenance, shared_sources = source_overlap_score(
        page_a.sources, page_b.sources
    )
    score += s_provenance

    # Build human-readable reason and collect link_types
    reasons = []
    link_types = []

    if s_slug > 0.5:
        reasons.append(f"similar slugs ({s_slug:.0%})")
        link_types.append("slug-similarity")
    if s_title > 0.5:
        reasons.append(f"similar titles ({s_title:.0%})")
        link_types.append("title-similarity")
    if s_tags > 0.0:
        shared_tags = page_a.tags & page_b.tags
        if shared_tags:
            reasons.append(f"shared tags: {', '.join(sorted(shared_tags))}")
            link_types.append("shared-tags")
    if s_keywords > 0.1:
        shared_kw = page_a.keywords & page_b.keywords
        top_kw = sorted(shared_kw)[:5]
        if top_kw:
            reasons.append(f"shared keywords: {', '.join(top_kw)}")
            link_types.append("shared-keywords")
    if shared_sources:
        reasons.append(f"shared sources: {', '.join(sorted(shared_sources))}")
        link_types.append("shared-provenance")
    if s_entities > 0.05:
        shared_ents = page_a.entities & page_b.entities
        top_ents = sorted(shared_ents)[:5]
        if top_ents:
            reasons.append(f"shared entities: {', '.join(top_ents)}")
            link_types.append("entity-coref")
    if page_a.category == "standards" and page_b.category == "standards" and s_tags > 0.0:
        link_types.append("standards-chain")

    reason = "; ".join(reasons) if reasons else f"composite score {score:.2f}"
    if not link_types:
        link_types.append("composite")
    return score, reason, link_types


def discover_cross_links(
    all_pages: Dict[str, List[WikiPage]],
    min_score: float = DEFAULT_MIN_SCORE,
) -> List[CrossLink]:
    """Compare all pages across different wikis and discover cross-links."""
    links = []
    wiki_names = sorted(all_pages.keys())

    for i, wiki_a in enumerate(wiki_names):
        for wiki_b in wiki_names[i + 1 :]:
            for page_a in all_pages[wiki_a]:
                for page_b in all_pages[wiki_b]:
                    score, reason, ltypes = compute_similarity(page_a, page_b)
                    if score >= min_score:
                        # Create bidirectional links
                        links.append(
                            CrossLink(
                                source=page_a,
                                target=page_b,
                                score=score,
                                link_type=reason,
                                link_types=ltypes,
                            )
                        )
                        links.append(
                            CrossLink(
                                source=page_b,
                                target=page_a,
                                score=score,
                                link_type=reason,
                                link_types=ltypes,
                            )
                        )

    # Sort by score descending, then by source page_id
    links.sort(key=lambda x: (-x.score, x.source.page_id))
    return links


# ── Output ───────────────────────────────────────────────────────────────────


def format_cross_links_md(links: List[CrossLink], all_pages: Dict[str, List[WikiPage]]) -> str:
    """Format cross-links as markdown in the same format as cross-links.md."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Deduplicate: keep only one direction per pair (A->B), group by wiki pair
    seen_pairs: Set[Tuple[str, str]] = set()
    unique_links: List[CrossLink] = []
    for link in links:
        pair_key = tuple(sorted([link.source.page_id, link.target.page_id]))
        if pair_key not in seen_pairs:
            seen_pairs.add(pair_key)
            unique_links.append(link)

    # Group by wiki pair
    pair_groups: Dict[Tuple[str, str], List[CrossLink]] = defaultdict(list)
    for link in unique_links:
        pair = tuple(sorted([link.source.wiki, link.target.wiki]))
        pair_groups[pair].append(link)

    lines = [
        "---",
        'title: "Cross-Wiki Link Index"',
        f"created: {today}",
        f"last_updated: {today}",
        f"total_cross_references: {len(unique_links)}",
        "auto_generated: true",
        "generator: scripts/knowledge/wiki-cross-links.py",
        "---",
        "",
        "# Cross-Wiki Link Index",
        "",
        "Bidirectional cross-references discovered between wiki domains.",
        f"Auto-generated by `wiki-cross-links.py` on {today} (issue #2011).",
        "",
    ]

    row_num = 0
    for pair_key in sorted(pair_groups.keys()):
        wiki_a, wiki_b = pair_key
        group = pair_groups[pair_key]
        group.sort(key=lambda x: (-x.score, x.source.page_id))

        lines.append(f"## {wiki_a.replace('-', ' ').title()} <-> {wiki_b.replace('-', ' ').title()} ({len(group)} links)")
        lines.append("")
        lines.append("| # | Source Wiki | Source Page | Target Wiki | Target Page | Score | Link Type |")
        lines.append("|---|------------|------------|-------------|-------------|-------|-----------|")

        for link in group:
            row_num += 1
            lines.append(
                f"| {row_num} | {link.source.wiki} | {link.source.short_id} "
                f"| {link.target.wiki} | {link.target.short_id} "
                f"| {link.score:.2f} | {link.link_type} |"
            )

        lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Wiki Pair | Cross-References |")
    lines.append("|-----------|-----------------|")
    for pair_key in sorted(pair_groups.keys()):
        wiki_a, wiki_b = pair_key
        lines.append(f"| {wiki_a} <-> {wiki_b} | {len(pair_groups[pair_key])} |")
    lines.append(f"| **Total** | **{len(unique_links)}** |")
    lines.append("")

    return "\n".join(lines)


def format_cross_links_jsonl(links: List[CrossLink]) -> str:
    """Format cross-links as JSONL (one JSON object per line, deduplicated).

    Each line contains: source_wiki, source_page, target_wiki, target_page,
    link_types, score, evidence, discovered.
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # Deduplicate: keep only one direction per pair (A->B)
    seen_pairs: Set[Tuple[str, str]] = set()
    lines = []

    for link in links:
        pair_key = tuple(sorted([link.source.page_id, link.target.page_id]))
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)

        record = {
            "source_wiki": link.source.wiki,
            "source_page": link.source.short_id,
            "target_wiki": link.target.wiki,
            "target_page": link.target.short_id,
            "link_types": link.link_types,
            "score": round(link.score, 2),
            "evidence": link.link_type,
            "discovered": today,
        }
        lines.append(json.dumps(record, ensure_ascii=False))

    return "\n".join(lines) + "\n" if lines else ""


def identify_new_links(
    links: List[CrossLink],
) -> Tuple[List[CrossLink], List[CrossLink]]:
    """Split links into new (not yet in page) and existing."""
    new_links = []
    existing_links = []

    for link in links:
        target_id = f"{link.target.wiki}/{link.target.category}/{link.target.slug}"
        if target_id in link.source.existing_cross_links:
            existing_links.append(link)
        else:
            new_links.append(link)

    return new_links, existing_links


def compute_relative_path(source_page: WikiPage, target_page: WikiPage) -> str:
    """Compute the relative markdown link path from source to target page."""
    # Both pages are at: knowledge/wikis/<wiki>/wiki/<category>/<slug>.md
    # Relative path from source to target:
    # ../../<target_wiki>/wiki/<target_category>/<target_slug>.md
    # But first go up from category dir (../) then from wiki dir (../)
    # then from wiki name dir (../)
    return f"../../../{target_page.wiki}/wiki/{target_page.category}/{target_page.slug}.md"


def apply_cross_link(source_page: WikiPage, target_page: WikiPage, link_type: str) -> bool:
    """Add a cross-wiki link to a page's Cross-References section.

    Returns True if the page was modified.
    """
    try:
        text = source_page.file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False

    # Check if link already exists
    target_id = f"{target_page.wiki}/{target_page.category}/{target_page.slug}"
    if target_id in source_page.existing_cross_links:
        return False

    rel_path = compute_relative_path(source_page, target_page)
    wiki_label = target_page.wiki.replace("-", " ").title()
    link_line = (
        f"- **Cross-wiki ({target_page.wiki})**: "
        f"[{target_page.title}]({rel_path}) "
        f"-- {link_type}"
    )

    # Find or create Cross-References section
    cr_pattern = re.compile(r"^## Cross-References\s*$", re.MULTILINE)
    cr_match = cr_pattern.search(text)

    if cr_match:
        # Insert after existing cross-references (before next section or EOF)
        insert_pos = cr_match.end()
        # Find the end of the cross-references section
        next_section = re.search(r"\n## ", text[insert_pos:])
        if next_section:
            insert_pos = insert_pos + next_section.start()
        else:
            insert_pos = len(text)

        # Ensure we end with a newline before inserting
        if not text[insert_pos - 1 : insert_pos] == "\n":
            link_line = "\n" + link_line

        text = text[:insert_pos].rstrip("\n") + "\n" + link_line + "\n" + text[insert_pos:]
    else:
        # Create new Cross-References section at end of file
        text = text.rstrip("\n") + "\n\n## Cross-References\n\n" + link_line + "\n"

    try:
        source_page.file_path.write_text(text, encoding="utf-8")
        return True
    except OSError:
        return False


# ── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Cross-wiki link discovery for the LLM wiki system.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Report discovered links without modifying files (default)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Update wiki pages with discovered cross-links",
    )
    parser.add_argument(
        "--wikis",
        type=str,
        default=None,
        help="Comma-separated list of wikis to scan (default: all domain wikis)",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=DEFAULT_MIN_SCORE,
        help=f"Minimum similarity score for a cross-link (default: {DEFAULT_MIN_SCORE})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write cross-links index to this file (default: knowledge/wikis/cross-links.md)",
    )
    parser.add_argument(
        "--jsonl",
        action="store_true",
        help="Also emit cross-links.jsonl alongside the markdown output",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    args = parser.parse_args()

    if args.apply:
        args.dry_run = False

    # ── Discover wikis ────────────────────────────────────────────────────────
    if args.wikis:
        wiki_names = [w.strip() for w in args.wikis.split(",")]
    else:
        wiki_names = [
            d.name
            for d in sorted(WIKIS_DIR.iterdir())
            if d.is_dir() and d.name not in SKIP_WIKIS
        ]

    if not args.quiet:
        print(f"Scanning {len(wiki_names)} wiki(s): {', '.join(wiki_names)}")

    # ── Scan all wikis ────────────────────────────────────────────────────────
    all_pages: Dict[str, List[WikiPage]] = {}
    total_pages = 0

    for wiki_name in wiki_names:
        wiki_dir = WIKIS_DIR / wiki_name
        if not wiki_dir.is_dir():
            if not args.quiet:
                print(f"  WARNING: wiki directory not found: {wiki_name}")
            continue

        pages = scan_wiki(wiki_dir, wiki_name)
        all_pages[wiki_name] = pages
        total_pages += len(pages)

        if not args.quiet:
            print(f"  {wiki_name}: {len(pages)} content pages")

    if not args.quiet:
        print(f"Total content pages: {total_pages}")
        print()

    # ── Discover cross-links ──────────────────────────────────────────────────
    links = discover_cross_links(all_pages, min_score=args.min_score)

    if not args.quiet:
        # Deduplicate for counting (each pair counted once)
        seen = set()
        unique_count = 0
        for link in links:
            pair = tuple(sorted([link.source.page_id, link.target.page_id]))
            if pair not in seen:
                seen.add(pair)
                unique_count += 1
        print(f"Discovered {unique_count} cross-link pair(s) (score >= {args.min_score})")

    # ── Identify new vs existing links ────────────────────────────────────────
    new_links, existing_links = identify_new_links(links)

    if not args.quiet:
        new_unique = set()
        for link in new_links:
            pair = tuple(sorted([link.source.page_id, link.target.page_id]))
            new_unique.add(pair)
        existing_unique = set()
        for link in existing_links:
            pair = tuple(sorted([link.source.page_id, link.target.page_id]))
            existing_unique.add(pair)
        print(f"  New links:      {len(new_unique)}")
        print(f"  Already linked: {len(existing_unique)}")
        print()

    # ── Generate cross-links.md ───────────────────────────────────────────────
    output_path = Path(args.output) if args.output else WIKIS_DIR / "cross-links.md"

    md_content = format_cross_links_md(links, all_pages)

    # ── Generate JSONL (if requested) ───────────────────────────────────────
    jsonl_content = format_cross_links_jsonl(links) if args.jsonl else ""
    jsonl_path = output_path.with_suffix(".jsonl")

    if args.dry_run:
        if not args.quiet:
            print("--- cross-links.md preview ---")
            print(md_content)
            print("--- end preview ---")
            if jsonl_content:
                print()
                print("--- cross-links.jsonl preview (first 10 lines) ---")
                for line in jsonl_content.splitlines()[:10]:
                    print(line)
                print(f"--- ({jsonl_content.count(chr(10))} total lines) ---")
            print()
            print("[dry-run] No files modified. Use --apply to update pages.")
    else:
        # Write cross-links.md
        output_path.write_text(md_content, encoding="utf-8")
        if not args.quiet:
            print(f"Wrote: {output_path}")

        # Write cross-links.jsonl (if requested)
        if jsonl_content:
            jsonl_path.write_text(jsonl_content, encoding="utf-8")
            if not args.quiet:
                print(f"Wrote: {jsonl_path}")

        # Apply new cross-links to pages
        modified_pages = 0
        for link in new_links:
            if apply_cross_link(link.source, link.target, link.link_type):
                modified_pages += 1
                if not args.quiet:
                    print(f"  Updated: {link.source.page_id} -> {link.target.page_id}")

        if not args.quiet:
            print(f"\nModified {modified_pages} page(s) with new cross-wiki links")

    # ── Exit code ─────────────────────────────────────────────────────────────
    # Exit 0 if no new links found (idempotent), exit 0 on success
    return 0


if __name__ == "__main__":
    sys.exit(main())
