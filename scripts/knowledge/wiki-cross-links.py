#!/usr/bin/env python3
"""wiki-cross-links.py — Automated cross-wiki link discovery.

Scans all wiki directories for entity/concept pages, extracts titles, tags,
and content keywords, then compares across wikis for concept overlap using
fuzzy matching on titles and tag intersection. Outputs discovered links in
the same format as knowledge/wikis/cross-links.md.

Usage:
    uv run scripts/knowledge/wiki-cross-links.py --dry-run          # report only
    uv run scripts/knowledge/wiki-cross-links.py --apply            # update pages
    uv run scripts/knowledge/wiki-cross-links.py --wikis engineering,marine-engineering
    uv run scripts/knowledge/wiki-cross-links.py --min-score 0.4    # tune sensitivity

Issue: #2011
"""

import argparse
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

    def __hash__(self):
        # Deduplicate: A->B and B->A are different entries
        return hash((self.source.page_id, self.target.page_id))

    def __eq__(self, other):
        return (
            self.source.page_id == other.source.page_id
            and self.target.page_id == other.target.page_id
        )


# ── Parsing ──────────────────────────────────────────────────────────────────


def parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter fields from markdown text."""
    result = {"title": "", "tags": []}
    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        return result

    fm_text = fm_match.group(1)

    # Title
    title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', fm_text, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # Tags — handle both [a, b] and - a\n- b formats
    tags_match = re.search(r"^tags:\s*\[(.*?)\]", fm_text, re.MULTILINE)
    if tags_match:
        raw = tags_match.group(1)
        result["tags"] = [
            t.strip().strip("\"'") for t in raw.split(",") if t.strip()
        ]
    else:
        # Multi-line YAML list
        tags_block = re.search(
            r"^tags:\s*\n((?:\s+-\s+.*\n?)+)", fm_text, re.MULTILINE
        )
        if tags_block:
            result["tags"] = [
                t.strip().lstrip("- ").strip("\"'")
                for t in tags_block.group(1).strip().split("\n")
                if t.strip()
            ]

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
            existing = extract_existing_cross_links(text, wiki_name)

            page = WikiPage(
                wiki=wiki_name,
                category=subdir_name,
                slug=slug,
                title=title,
                tags=tags,
                keywords=keywords,
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


def compute_similarity(page_a: WikiPage, page_b: WikiPage) -> Tuple[float, str]:
    """Compute weighted similarity score between two pages from different wikis.

    Returns (score, reason_string).
    """
    s_slug = slug_similarity(page_a.slug, page_b.slug)
    s_title = title_similarity(page_a.title, page_b.title)
    s_tags = tag_overlap(page_a.tags, page_b.tags)
    s_keywords = keyword_overlap(page_a.keywords, page_b.keywords)

    # Weighted composite score
    # High weight on slug/title similarity (strongest signal for concept overlap)
    # Medium weight on tags (curated by author)
    # Low weight on keywords (noisy but catches non-obvious connections)
    score = (s_slug * 0.30) + (s_title * 0.30) + (s_tags * 0.25) + (s_keywords * 0.15)

    # Build human-readable reason
    reasons = []
    if s_slug > 0.5:
        reasons.append(f"similar slugs ({s_slug:.0%})")
    if s_title > 0.5:
        reasons.append(f"similar titles ({s_title:.0%})")
    if s_tags > 0.0:
        shared_tags = page_a.tags & page_b.tags
        if shared_tags:
            reasons.append(f"shared tags: {', '.join(sorted(shared_tags))}")
    if s_keywords > 0.1:
        shared_kw = page_a.keywords & page_b.keywords
        top_kw = sorted(shared_kw)[:5]
        if top_kw:
            reasons.append(f"shared keywords: {', '.join(top_kw)}")

    reason = "; ".join(reasons) if reasons else f"composite score {score:.2f}"
    return score, reason


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
                    score, reason = compute_similarity(page_a, page_b)
                    if score >= min_score:
                        # Create bidirectional links
                        links.append(
                            CrossLink(
                                source=page_a,
                                target=page_b,
                                score=score,
                                link_type=reason,
                            )
                        )
                        links.append(
                            CrossLink(
                                source=page_b,
                                target=page_a,
                                score=score,
                                link_type=reason,
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

    if args.dry_run:
        if not args.quiet:
            print("--- cross-links.md preview ---")
            print(md_content)
            print("--- end preview ---")
            print()
            print("[dry-run] No files modified. Use --apply to update pages.")
    else:
        # Write cross-links.md
        output_path.write_text(md_content, encoding="utf-8")
        if not args.quiet:
            print(f"Wrote: {output_path}")

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
