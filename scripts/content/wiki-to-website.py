#!/usr/bin/env python3
"""Convert wiki knowledge pages to website-ready markdown for aceengineer.com.

Reads wiki pages from knowledge/wikis/*, strips internal references,
adds SEO metadata and CTAs, outputs to docs/content-pipeline/output/.

Usage:
    uv run scripts/content/wiki-to-website.py                           # all domains
    uv run scripts/content/wiki-to-website.py --domain engineering      # one domain
    uv run scripts/content/wiki-to-website.py --page path/to/page.md   # single page
    uv run scripts/content/wiki-to-website.py --dry-run                 # preview only
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class PageMeta(NamedTuple):
    title: str
    description: str
    keywords: list[str]
    domain: str
    category: str  # concepts, entities, standards, workflows
    source_path: Path
    url_slug: str


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
)
WIKI_ROOT = REPO_ROOT / "knowledge" / "wikis"
OUTPUT_ROOT = REPO_ROOT / "docs" / "content-pipeline" / "output"

DOMAIN_MAP: dict[str, str] = {
    "engineering": "engineering",
    "marine-engineering": "marine",
    "naval-architecture": "naval-architecture",
    "maritime-law": "maritime-law",
}

# Output subdirectory for each wiki category
CATEGORY_OUTPUT_MAP: dict[str, str] = {
    "concepts": "",       # goes into domain root
    "entities": "",       # goes into domain root
    "standards": "standards",
    "workflows": "services",
}

SITE_URL = "https://aceengineer.com"
CONTACT_URL = f"{SITE_URL}/contact"

CTA_BLOCK = f"""
---

## Work With Us

ACE Engineer provides expert engineering consulting across offshore, marine, and subsea disciplines. Our team combines deep domain expertise with modern computational tools to deliver reliable, auditable results.

[Contact us]({CONTACT_URL}) to discuss how we can support your project.

*Visit [aceengineer.com]({SITE_URL}) for our full range of services.*
"""

# Patterns to strip from content
INTERNAL_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # GitHub issue references with optional context: (#1234, closed 2026-04-04)
    (re.compile(r"\((?:issue\s*)?#\d{3,5},?\s*(?:closed\s+\d{4}-\d{2}-\d{2})?\s*\)\.?", re.IGNORECASE), ""),
    # Standalone issue refs: #1234, issue #1234
    (re.compile(r"(?:issue\s*)?#\d{3,5}", re.IGNORECASE), ""),
    # Internal file paths: `scripts/foo/bar.sh`, `docs/methodology/...`
    (re.compile(r"`(?:scripts|docs|\.claude|knowledge)/[^`]+`"), ""),
    # Source metadata lines referencing internal seeds
    (re.compile(r"^sources:\s*\n(?:\s+-\s+[\w-]+\n)*", re.MULTILINE), ""),
    # Cross-wiki relative links: [text](../../../marine-engineering/wiki/...)
    (re.compile(r"\[([^\]]+)\]\(\.\./\.\./\.\./[^)]+\)"), r"\1"),
    # Internal cross-reference links: [text](../concepts/foo.md)
    (re.compile(r"\[([^\]]+)\]\(\.\./(?:concepts|entities|sources|standards|workflows)/[^)]+\)"), r"\1"),
    # Wiki-style links: [[Page Name]]
    (re.compile(r"\[\[([^\]]+)\]\]"), r"\1"),
    # Source references: **Source**: [text](../sources/...)
    (re.compile(r"\*\*Source\*\*:\s*\[[^\]]*\]\([^)]*\)\s*\n?"), ""),
    # Cross-wiki references: **Cross-wiki (...)**: [text](...)
    (re.compile(r"\*\*Cross-wiki[^*]*\*\*:\s*\[[^\]]*\]\([^)]*\)[^\n]*\n?"), ""),
    # Related entity/concept with internal links
    (re.compile(r"\*\*Related (?:entity|concept|standard|issue)\*\*:\s*\[[^\]]*\]\([^)]*\)[^\n]*\n?"), ""),
]

# Additional cleanup patterns applied after stripping
CLEANUP_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Empty parentheses left after issue stripping: (, closed 2026-04-04) or ()
    (re.compile(r"\s*\(,?\s*(?:closed\s+\d{4}-\d{2}-\d{2})?\s*\)\.?"), ""),
    # Multiple blank lines -> double
    (re.compile(r"\n{3,}"), "\n\n"),
    # Empty cross-references section
    (re.compile(r"## Cross-References\s*\n\n(?=##|\Z)"), ""),
    # Empty related pages section
    (re.compile(r"## Related Pages\s*\n\n(?=##|\Z)"), ""),
    # Trailing whitespace
    (re.compile(r"[ \t]+\n"), "\n"),
]


# ---------------------------------------------------------------------------
# Frontmatter extraction and generation
# ---------------------------------------------------------------------------

def extract_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Extract YAML frontmatter and return (metadata_dict, body)."""
    meta: dict[str, str] = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            for line in fm_text.split("\n"):
                line = line.strip()
                if ":" in line and not line.startswith("-"):
                    key, _, value = line.partition(":")
                    meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body


def extract_title(meta: dict[str, str], body: str) -> str:
    """Get title from frontmatter or first H1."""
    if "title" in meta:
        return meta["title"]
    match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Untitled"


def extract_tags(meta: dict[str, str]) -> list[str]:
    """Get tags from frontmatter."""
    raw = meta.get("tags", "")
    if not raw:
        return []
    # Handle both [a, b, c] and YAML list formats
    raw = raw.strip("[]")
    return [t.strip() for t in raw.split(",") if t.strip()]


def generate_description(title: str, body: str) -> str:
    """Generate a concise SEO description from page content."""
    # Use the first substantial paragraph after the title
    lines = body.split("\n")
    para_lines: list[str] = []
    in_para = False
    for line in lines:
        stripped = line.strip()
        # Skip headings, tables, code blocks, empty lines, bold-only lines
        if (
            stripped.startswith("#")
            or stripped.startswith("|")
            or stripped.startswith("```")
            or stripped.startswith("**Full title")
            or stripped.startswith("**Scope")
        ):
            if in_para and para_lines:
                break
            continue
        if not stripped:
            if in_para and para_lines:
                break
            continue
        # Strip inline markdown bold/italic for clean descriptions
        clean = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", stripped)
        in_para = True
        para_lines.append(clean)

    if para_lines:
        desc = " ".join(para_lines)
        # Truncate to ~160 chars for SEO
        if len(desc) > 160:
            desc = desc[:157].rsplit(" ", 1)[0] + "..."
        return desc
    return f"{title} - ACE Engineer technical reference."


def generate_url_slug(source_path: Path, domain: str) -> str:
    """Generate a URL slug from the source file path."""
    stem = source_path.stem
    # Convert snake_case or kebab-case to consistent slug
    slug = stem.lower().replace("_", "-")
    return slug


def build_page_meta(source_path: Path, domain_key: str) -> PageMeta:
    """Build metadata for a wiki page."""
    content = source_path.read_text(encoding="utf-8")
    meta, body = extract_frontmatter(content)
    title = extract_title(meta, body)
    tags = extract_tags(meta)
    # Strip internal references before generating the description
    clean_body = strip_internal_references(body)
    clean_body = cleanup_whitespace(clean_body)
    description = generate_description(title, clean_body)
    slug = generate_url_slug(source_path, domain_key)

    # Determine category from path
    category = "concepts"
    for cat in ("concepts", "entities", "standards", "workflows"):
        if cat in source_path.parts:
            category = cat
            break

    return PageMeta(
        title=title,
        description=description,
        keywords=tags,
        domain=domain_key,
        category=category,
        source_path=source_path,
        url_slug=slug,
    )


# ---------------------------------------------------------------------------
# Content transformation
# ---------------------------------------------------------------------------

def strip_internal_references(body: str) -> str:
    """Remove internal cross-references, file paths, issue numbers."""
    for pattern, replacement in INTERNAL_PATTERNS:
        body = pattern.sub(replacement, body)
    return body


def cleanup_whitespace(body: str) -> str:
    """Clean up formatting artifacts left by stripping."""
    for pattern, replacement in CLEANUP_PATTERNS:
        body = pattern.sub(replacement, body)
    return body.strip()


def add_author_line(body: str) -> str:
    """Add author attribution after the title."""
    lines = body.split("\n", 1)
    if lines and lines[0].startswith("# "):
        rest = lines[1] if len(lines) > 1 else ""
        return f"{lines[0]}\n\n*By [ACE Engineer]({SITE_URL}) -- Expert Offshore and Marine Engineering Consulting*\n{rest}"
    return body


def transform_page(source_path: Path, meta: PageMeta) -> str:
    """Transform a wiki page into website-ready content."""
    content = source_path.read_text(encoding="utf-8")
    _, body = extract_frontmatter(content)

    # Apply transformations
    body = strip_internal_references(body)
    body = cleanup_whitespace(body)
    body = add_author_line(body)

    # Determine output URL path
    domain_slug = DOMAIN_MAP.get(meta.domain, meta.domain)
    if meta.category == "standards":
        url_path = f"/knowledge/standards/{meta.url_slug}"
    elif meta.category == "workflows":
        url_path = f"/services/{meta.url_slug}"
    else:
        url_path = f"/knowledge/{domain_slug}/{meta.url_slug}"

    # Build new frontmatter
    keywords_str = ", ".join(meta.keywords) if meta.keywords else "offshore engineering, marine engineering"
    frontmatter = f"""---
title: "{meta.title}"
description: "{meta.description}"
keywords: "{keywords_str}"
author: "ACE Engineer"
url: "{url_path}"
canonical: "{SITE_URL}{url_path}"
domain: "{domain_slug}"
---"""

    # Assemble final page
    return f"{frontmatter}\n\n{body}\n{CTA_BLOCK}\n"


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def discover_pages(domain: str | None = None) -> list[Path]:
    """Find all wiki pages eligible for publication."""
    pages: list[Path] = []
    domains = [domain] if domain else list(DOMAIN_MAP.keys())

    for d in domains:
        wiki_dir = WIKI_ROOT / d / "wiki"
        if not wiki_dir.exists():
            print(f"  [skip] Wiki directory not found: {wiki_dir}", file=sys.stderr)
            continue
        for category in ("concepts", "entities", "standards", "workflows"):
            cat_dir = wiki_dir / category
            if not cat_dir.exists():
                continue
            for page in sorted(cat_dir.glob("*.md")):
                # Skip index files and logs
                if page.name in ("index.md", "log.md", "overview.md"):
                    continue
                pages.append(page)

    return pages


# Curated list of high-SEO-value pages for initial publication
HIGH_VALUE_PAGES: list[str] = [
    # Engineering concepts -- methodology (unique differentiation)
    "knowledge/wikis/engineering/wiki/concepts/compound-engineering.md",
    "knowledge/wikis/engineering/wiki/concepts/enforcement-over-instruction.md",
    # Offshore engineering -- high search volume topics
    "knowledge/wikis/engineering/wiki/concepts/cathodic-protection-design.md",
    "knowledge/wikis/engineering/wiki/concepts/mooring-line-failure-physics.md",
    "knowledge/wikis/engineering/wiki/concepts/sn-curve-fatigue-definitions.md",
    "knowledge/wikis/engineering/wiki/concepts/fea-structural-analysis.md",
    "knowledge/wikis/engineering/wiki/concepts/hydrodynamic-analysis.md",
    "knowledge/wikis/engineering/wiki/concepts/cfd-offshore-hydrodynamics.md",
    "knowledge/wikis/engineering/wiki/concepts/pipeline-integrity-assessment.md",
    "knowledge/wikis/engineering/wiki/concepts/viv-riser-fatigue.md",
    "knowledge/wikis/engineering/wiki/concepts/free-span-viv-fatigue.md",
    "knowledge/wikis/engineering/wiki/concepts/pile-capacity-alpha-method.md",
    "knowledge/wikis/engineering/wiki/concepts/structural-analysis-offshore.md",
    "knowledge/wikis/engineering/wiki/concepts/field-development-economics.md",
    "knowledge/wikis/engineering/wiki/concepts/standards-update-tracking.md",
    "knowledge/wikis/engineering/wiki/concepts/energy-field-economics.md",
    # Standards -- professionals search for these
    "knowledge/wikis/engineering/wiki/standards/dnv-rp-c203.md",
    "knowledge/wikis/engineering/wiki/standards/dnv-rp-c205.md",
    "knowledge/wikis/engineering/wiki/standards/dnv-rp-f101.md",
    "knowledge/wikis/engineering/wiki/standards/dnv-rp-f105.md",
    "knowledge/wikis/engineering/wiki/standards/api-579-ffs.md",
    "knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md",
    "knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md",
    # Entities -- tool-specific pages (OrcaFlex searchers)
    "knowledge/wikis/engineering/wiki/entities/orcaflex-solver.md",
    "knowledge/wikis/engineering/wiki/entities/orcawave-solver.md",
    "knowledge/wikis/engineering/wiki/entities/mooring-analysis-system.md",
    "knowledge/wikis/engineering/wiki/entities/openfoam-cfd.md",
    "knowledge/wikis/engineering/wiki/entities/diffraction-analysis-system.md",
    # Incidents -- high interest, unique content
    "knowledge/wikis/engineering/wiki/entities/prelude-flng-mooring.md",
    "knowledge/wikis/engineering/wiki/entities/elba-island-mooring-incident.md",
    "knowledge/wikis/engineering/wiki/entities/hmpe-mooring-failures.md",
    "knowledge/wikis/engineering/wiki/entities/nws-lng-mooring-investigation.md",
]


def filter_internal_only(pages: list[Path]) -> list[Path]:
    """Exclude pages that are purely about internal tooling/methodology."""
    internal_keywords = {
        "agent-delegation",
        "compliance-dashboard",
        "compliance-enforcement",
        "compound-learning-loop",
        "context-budget-management",
        "git-based-pull-queue",
        "jsonl-knowledge-stores",
        "knowledge-to-website-pipeline",
        "multi-agent-parity",
        "orchestrator-worker-separation",
        "three-agent-cross-review",
        "python-type-safety",
        "shell-scripting-patterns",
        "test-driven-development",
        "claude-code",
        "codex-cli",
        "gemini-cli",
        "gsd-framework",
        "hermes",
        "llm-wiki-tool",
        "skills-system",
        "solver-queue",
    }
    return [p for p in pages if p.stem not in internal_keywords]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert wiki knowledge pages to website-ready markdown"
    )
    parser.add_argument(
        "--domain",
        choices=list(DOMAIN_MAP.keys()),
        help="Process only this wiki domain",
    )
    parser.add_argument(
        "--page",
        type=Path,
        help="Process a single page (path relative to repo root)",
    )
    parser.add_argument(
        "--high-value-only",
        action="store_true",
        default=True,
        help="Only process curated high-SEO-value pages (default)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all eligible pages (overrides --high-value-only)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing files",
    )
    args = parser.parse_args()

    print(f"Content Pipeline: wiki-to-website")
    print(f"Repo root: {REPO_ROOT}")
    print(f"Output: {OUTPUT_ROOT}")
    print()

    if args.page:
        source = REPO_ROOT / args.page
        if not source.exists():
            print(f"ERROR: Page not found: {source}", file=sys.stderr)
            sys.exit(1)
        pages = [source]
    elif args.all:
        pages = discover_pages(args.domain)
        pages = filter_internal_only(pages)
    else:
        # High-value only
        pages = []
        for rel in HIGH_VALUE_PAGES:
            p = REPO_ROOT / rel
            if p.exists():
                pages.append(p)
            else:
                print(f"  [skip] Not found: {rel}", file=sys.stderr)

    print(f"Pages to process: {len(pages)}")
    print()

    generated = 0
    skipped = 0

    for source_path in pages:
        # Determine domain from path
        domain_key = "engineering"
        for d in DOMAIN_MAP:
            if d in source_path.parts:
                domain_key = d
                break

        try:
            meta = build_page_meta(source_path, domain_key)
        except Exception as e:
            print(f"  [error] {source_path.name}: {e}", file=sys.stderr)
            skipped += 1
            continue

        # Determine output path
        domain_out = DOMAIN_MAP.get(meta.domain, meta.domain)
        cat_out = CATEGORY_OUTPUT_MAP.get(meta.category, "")
        if cat_out:
            out_dir = OUTPUT_ROOT / cat_out
        else:
            out_dir = OUTPUT_ROOT / domain_out

        out_file = out_dir / f"{meta.url_slug}.md"

        if args.dry_run:
            print(f"  [dry-run] {source_path.name} -> {out_file.relative_to(REPO_ROOT)}")
            print(f"            Title: {meta.title}")
            print(f"            Keywords: {', '.join(meta.keywords)}")
            generated += 1
            continue

        # Transform and write
        try:
            output_content = transform_page(source_path, meta)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file.write_text(output_content, encoding="utf-8")
            print(f"  [ok] {meta.title} -> {out_file.relative_to(REPO_ROOT)}")
            generated += 1
        except Exception as e:
            print(f"  [error] {source_path.name}: {e}", file=sys.stderr)
            skipped += 1

    print()
    print(f"Generated: {generated}, Skipped: {skipped}")
    if not args.dry_run and generated > 0:
        print(f"Output directory: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
