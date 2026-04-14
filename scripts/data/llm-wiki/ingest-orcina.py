#!/usr/bin/env python3
"""
Ingest Orcina product documentation (OrcaFlex, OrcaWave, OrcFxAPI) into llm-wiki.

Crawls the MadCap Flare online help via TOC XML, fetches each topic page,
converts HTML to markdown, and builds a searchable index.
Ref: GH #2088

Usage:
    python3 scripts/data/llm-wiki/ingest-orcina.py [--output-dir DIR] [--products orcaflex orcawave orcfxapi]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup

# ── Sources ──────────────────────────────────────────────────────────────────

PRODUCTS = {
    "orcaflex": {
        "label": "OrcaFlex",
        "base_url": "https://www.orcina.com/webhelp/OrcaFlex",
        "toc_url": "https://www.orcina.com/webhelp/OrcaFlex/Data/Toc.xml",
    },
    "orcawave": {
        "label": "OrcaWave",
        "base_url": "https://www.orcina.com/webhelp/OrcaWave",
        "toc_url": "https://www.orcina.com/webhelp/OrcaWave/Data/Toc.xml",
    },
    "orcfxapi": {
        "label": "OrcFxAPI",
        "base_url": "https://www.orcina.com/webhelp/OrcFxAPI",
        "toc_url": "https://www.orcina.com/webhelp/OrcFxAPI/Data/Toc.xml",
    },
}

SUPPLEMENTARY_URLS = [
    ("resources", "https://www.orcina.com/resources/"),
    ("papers", "https://www.orcina.com/resources/papers/"),
    ("papers-and-technical-notes", "https://www.orcina.com/resources/papers-and-technical-notes/"),
    ("documentation", "https://www.orcina.com/resources/documentation/"),
    ("releases", "https://www.orcina.com/releases/"),
]

HEADERS = {"User-Agent": "workspace-hub-llm-wiki/1.0 (documentation indexing)"}
DELAY_SECONDS = 0.3  # polite crawl delay


# ── TOC Parsing ──────────────────────────────────────────────────────────────

def parse_toc_xml(toc_url: str) -> list[dict]:
    """Parse MadCap Flare Toc.xml and return list of {link, title, section} entries."""
    req = urllib.request.Request(toc_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode("utf-8", errors="replace")

    soup = BeautifulSoup(content, "html.parser")
    entries = []

    # html.parser lowercases tag/attr names; find all tocentry elements with links
    for tag in soup.find_all("tocentry"):
        link = tag.get("link")
        if not link:
            continue
        title = tag.get("title", "")

        # Build section path from parent tocentry titles
        section_path = []
        for parent in tag.parents:
            if hasattr(parent, "name") and parent.name == "tocentry":
                ptitle = parent.get("title", "")
                if ptitle:
                    section_path.append(ptitle)
        section_path.reverse()

        entries.append({
            "link": link,
            "title": title,
            "section_path": section_path,
        })

    return entries


# ── HTML to Markdown conversion ──────────────────────────────────────────────

def html_to_markdown(html_content: str, source_url: str = "") -> tuple[str, str]:
    """Convert HTML to markdown using BeautifulSoup. Returns (title, markdown)."""
    soup = BeautifulSoup(html_content, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Remove non-content elements
    for tag in soup.find_all(["script", "style", "nav", "footer", "header",
                               "link", "meta", "noscript"]):
        tag.decompose()

    # MadCap Flare puts content in div.MCBreadcrumbsBox or body
    main = (soup.find("div", class_="MCBreadcrumbsBox")
            or soup.find("body")
            or soup)
    if main is None:
        return title, ""

    # For MadCap, take the whole body since content is after breadcrumbs
    if main.name != "body":
        main = main.parent if main.parent and main.parent.name == "body" else soup.find("body") or soup

    md_lines = []
    _convert_element(main, md_lines)
    markdown = "\n".join(md_lines)

    # Clean up
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    markdown = markdown.strip()

    if source_url:
        markdown = f"<!-- source: {source_url} -->\n\n{markdown}"

    return title, markdown


def _convert_element(element, lines, depth=0):
    """Recursively convert a BS4 element to markdown lines."""
    from bs4 import NavigableString, Tag

    if isinstance(element, NavigableString):
        text = str(element).strip()
        if text:
            lines.append(text)
        return

    if not isinstance(element, Tag):
        return

    tag = element.name

    # Skip MadCap navigation/breadcrumb divs
    classes = element.get("class", [])
    if any(c.startswith("MCBreadcrumbs") for c in classes):
        return
    if any(c in ("MCMiniTocBox_0", "MCRelatedTopics") for c in classes):
        return

    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(tag[1])
        text = element.get_text(strip=True)
        if text:
            lines.append(f"\n{'#' * level} {text}\n")
        return

    if tag == "p":
        # Handle paragraphs with mixed inline content
        parts = []
        for child in element.children:
            if isinstance(child, NavigableString):
                parts.append(str(child))
            elif isinstance(child, Tag):
                if child.name in ("strong", "b"):
                    parts.append(f"**{child.get_text()}**")
                elif child.name in ("em", "i"):
                    parts.append(f"*{child.get_text()}*")
                elif child.name == "code":
                    parts.append(f"`{child.get_text()}`")
                elif child.name == "a":
                    href = child.get("href", "")
                    parts.append(f"[{child.get_text()}]({href})" if href else child.get_text())
                elif child.name == "br":
                    parts.append("\n")
                elif child.name == "img":
                    parts.append(f"![{child.get('alt', '')}]({child.get('src', '')})")
                else:
                    parts.append(child.get_text())
        text = "".join(parts).strip()
        if text:
            lines.append(f"\n{text}\n")
        return

    if tag in ("ul", "ol"):
        for i, li in enumerate(element.find_all("li", recursive=False)):
            prefix = f"{i+1}." if tag == "ol" else "-"
            text = li.get_text(strip=True)
            if text:
                lines.append(f"{prefix} {text}")
        lines.append("")
        return

    if tag == "table":
        _convert_table(element, lines)
        return

    if tag == "pre":
        code = element.get_text()
        lines.append(f"\n```\n{code}\n```\n")
        return

    if tag == "code":
        lines.append(f"`{element.get_text()}`")
        return

    if tag == "a":
        text = element.get_text(strip=True)
        href = element.get("href", "")
        if text and href:
            lines.append(f"[{text}]({href})")
        elif text:
            lines.append(text)
        return

    if tag == "img":
        lines.append(f"![{element.get('alt', 'image')}]({element.get('src', '')})")
        return

    if tag in ("strong", "b"):
        text = element.get_text(strip=True)
        if text:
            lines.append(f"**{text}**")
        return

    if tag in ("em", "i"):
        text = element.get_text(strip=True)
        if text:
            lines.append(f"*{text}*")
        return

    if tag == "br":
        lines.append("")
        return

    if tag == "hr":
        lines.append("\n---\n")
        return

    if tag == "dl":
        for dt in element.find_all("dt", recursive=False):
            dd = dt.find_next_sibling("dd")
            term = dt.get_text(strip=True)
            defn = dd.get_text(strip=True) if dd else ""
            lines.append(f"\n**{term}**")
            if defn:
                lines.append(f": {defn}\n")
        return

    # Default: recurse
    for child in element.children:
        _convert_element(child, lines, depth + 1)


def _convert_table(table, lines):
    """Convert an HTML table to markdown table."""
    rows = table.find_all("tr")
    if not rows:
        return

    md_rows = []
    for row in rows:
        cells = row.find_all(["th", "td"])
        cell_texts = [c.get_text(strip=True).replace("|", "\\|").replace("\n", " ") for c in cells]
        if cell_texts:
            md_rows.append("| " + " | ".join(cell_texts) + " |")

    if md_rows:
        lines.append("")
        lines.append(md_rows[0])
        ncols = max(row.count("|") - 1 for row in md_rows)
        lines.append("|" + "|".join(["---"] * max(ncols, 1)) + "|")
        for row in md_rows[1:]:
            lines.append(row)
        lines.append("")


# ── Web Fetching ─────────────────────────────────────────────────────────────

def fetch_page(url: str) -> str | None:
    """Fetch a single URL, return HTML content or None on failure."""
    try:
        # URL-encode spaces and special chars in the path
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        # Try URL-encoding the path component
        try:
            from urllib.parse import urlparse, urlunparse
            parts = urlparse(url)
            encoded_path = quote(parts.path, safe="/")
            encoded_url = urlunparse(parts._replace(path=encoded_path))
            req = urllib.request.Request(encoded_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception:
            return None


# ── Product Ingestion ────────────────────────────────────────────────────────

def ingest_product(product_key: str, info: dict, output_root: Path) -> dict:
    """Ingest all topics for one product. Returns summary dict."""
    print(f"\n{'='*60}")
    print(f"Processing {info['label']} ({product_key})")
    print(f"{'='*60}")

    # Parse TOC
    print(f"  Fetching TOC from {info['toc_url']} ...")
    toc_entries = parse_toc_xml(info["toc_url"])
    print(f"  Found {len(toc_entries)} topic pages in TOC")

    product_dir = output_root / product_key / "topics"
    product_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    errors = 0
    skipped = 0

    for i, toc_entry in enumerate(toc_entries):
        link = toc_entry["link"]  # e.g. /Content/html/Introduction.htm
        page_url = info["base_url"] + link
        title_from_toc = toc_entry["title"]

        if (i + 1) % 25 == 0 or i == 0:
            print(f"  [{i+1}/{len(toc_entries)}] {title_from_toc}")

        html = fetch_page(page_url)
        if html is None:
            errors += 1
            continue

        if len(html) < 200:
            skipped += 1
            continue

        title, markdown = html_to_markdown(html, page_url)
        title = title or title_from_toc

        if not markdown or len(markdown) < 30:
            skipped += 1
            continue

        # Generate output filename
        md_filename = re.sub(r"\.html?$", ".md", link.lstrip("/"), flags=re.IGNORECASE)
        md_filename = md_filename.replace(" ", "_")
        # Simplify path: Content/html/Foo.htm → Foo.md
        md_filename = re.sub(r"^Content/html/", "", md_filename)

        out_path = product_dir / md_filename
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(markdown)

        # Extract headings for section index
        sections = re.findall(r"^#{1,3}\s+(.+)$", markdown, re.MULTILINE)[:15]

        entries.append({
            "file": md_filename,
            "title": title,
            "section_path": toc_entry["section_path"],
            "sections": sections,
            "source_url": page_url,
            "size_bytes": len(markdown),
            "word_count": len(markdown.split()),
        })

        # Polite delay
        time.sleep(DELAY_SECONDS)

    # Build product index
    total_words = sum(e["word_count"] for e in entries)
    total_bytes = sum(e["size_bytes"] for e in entries)

    product_index = {
        "product": info["label"],
        "base_url": info["base_url"],
        "generated": datetime.now(timezone.utc).isoformat(),
        "topic_count": len(entries),
        "total_words": total_words,
        "total_size_mb": round(total_bytes / 1024 / 1024, 2),
        "errors": errors,
        "skipped": skipped,
        "topics": entries,
    }

    index_path = output_root / product_key / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(product_index, f, indent=2)

    print(f"  Done: {len(entries)} topics, {total_words:,} words, {total_bytes/1024/1024:.1f} MB")
    print(f"  Errors: {errors}, Skipped: {skipped}")

    return {
        "label": info["label"],
        "topic_count": len(entries),
        "total_words": total_words,
        "total_size_mb": round(total_bytes / 1024 / 1024, 2),
        "errors": errors,
        "index_path": f"{product_key}/index.json",
    }


# ── Supplementary Pages ─────────────────────────────────────────────────────

def ingest_supplementary(output_root: Path) -> list[dict]:
    """Fetch supplementary resource pages."""
    print(f"\n{'='*60}")
    print("Processing supplementary pages")
    print(f"{'='*60}")

    supp_dir = output_root / "supplementary"
    supp_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    for name, url in SUPPLEMENTARY_URLS:
        print(f"  Fetching {name} from {url}")
        html = fetch_page(url)
        if html is None:
            print(f"    FAILED")
            continue

        title, markdown = html_to_markdown(html, url)
        if not markdown:
            continue

        out_path = supp_dir / f"{name}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n" if title else "")
            f.write(markdown)

        entries.append({
            "file": f"supplementary/{name}.md",
            "title": title or name,
            "source_url": url,
            "size_bytes": len(markdown),
            "word_count": len(markdown.split()),
        })

        time.sleep(DELAY_SECONDS)

    return entries


# ── Papers & Technical Notes (PDF) ───────────────────────────────────────────

PAPERS_PAGE = "https://www.orcina.com/resources/papers-and-technical-notes/"

def ingest_papers(output_root: Path) -> list[dict]:
    """Scrape the papers page, download PDFs, convert to markdown via pdftotext."""
    print(f"\n{'='*60}")
    print("Processing papers & technical notes (PDFs)")
    print(f"{'='*60}")

    papers_dir = output_root / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)

    # Fetch the papers listing page to extract PDF links
    print(f"  Fetching papers listing from {PAPERS_PAGE}")
    html = fetch_page(PAPERS_PAGE)
    if html is None:
        print("  FAILED to fetch papers page")
        return []

    soup = BeautifulSoup(html, "html.parser")
    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf") and "orcina.com" in href:
            title = a.get_text(strip=True) or Path(href).stem
            pdf_links.append({"url": href, "title": title})

    # Deduplicate by URL
    seen = set()
    unique_pdfs = []
    for p in pdf_links:
        if p["url"] not in seen:
            seen.add(p["url"])
            unique_pdfs.append(p)
    pdf_links = unique_pdfs

    print(f"  Found {len(pdf_links)} PDF links")

    entries = []
    tmp_dir = tempfile.mkdtemp(prefix="orcina-pdfs-")

    for i, pdf_info in enumerate(pdf_links):
        url = pdf_info["url"]
        title = pdf_info["title"]
        filename = Path(url).stem
        safe_filename = re.sub(r"[^\w\-.]", "_", filename)

        print(f"  [{i+1}/{len(pdf_links)}] {title[:60]}")

        # Download PDF
        pdf_path = os.path.join(tmp_dir, f"{safe_filename}.pdf")
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(pdf_path, "wb") as f:
                    f.write(resp.read())
        except Exception as e:
            print(f"    Download failed: {e}")
            continue

        # Convert PDF to text via pdftotext
        try:
            result = subprocess.run(
                ["pdftotext", "-layout", pdf_path, "-"],
                capture_output=True, text=True, timeout=30,
            )
            text = result.stdout.strip()
        except Exception as e:
            print(f"    pdftotext failed: {e}")
            continue

        if not text or len(text) < 100:
            print(f"    Skipped (empty/too short)")
            continue

        # Format as markdown
        markdown = f"<!-- source: {url} -->\n\n# {title}\n\n{text}"

        out_path = papers_dir / f"{safe_filename}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        entries.append({
            "file": f"papers/{safe_filename}.md",
            "title": title,
            "source_url": url,
            "size_bytes": len(markdown),
            "word_count": len(markdown.split()),
            "type": "pdf",
        })

        time.sleep(DELAY_SECONDS)

    print(f"  Done: {len(entries)} papers converted, {sum(e['word_count'] for e in entries):,} words")
    return entries


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ingest Orcina docs into llm-wiki")
    parser.add_argument(
        "--output-dir",
        default="/mnt/local-analysis/workspace-hub/data/llm-wiki",
        # Actual data lives on ace drive: /mnt/remote/ace-linux-1/ace/digitalmodel/llm-wiki/
        # Local path is a symlink per data-placement policy (#1540, #2102)
        help="Root output directory (default: data/llm-wiki symlink -> ace drive)",
    )
    parser.add_argument(
        "--products",
        nargs="*",
        default=list(PRODUCTS.keys()),
        choices=list(PRODUCTS.keys()),
        help="Which products to ingest (default: all)",
    )
    args = parser.parse_args()

    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_root}")
    print(f"Products:         {', '.join(args.products)}")
    print(f"Crawl delay:      {DELAY_SECONDS}s")

    master_index = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "generator": "ingest-orcina.py",
        "issue": "https://github.com/vamseeachanta/workspace-hub/issues/2088",
        "products": {},
    }

    # Ingest each product
    for product_key in args.products:
        info = PRODUCTS[product_key]
        summary = ingest_product(product_key, info, output_root)
        master_index["products"][product_key] = summary

    # Supplementary pages
    supp_entries = ingest_supplementary(output_root)
    master_index["supplementary"] = {
        "page_count": len(supp_entries),
        "pages": supp_entries,
    }

    # Papers & technical notes (PDFs)
    paper_entries = ingest_papers(output_root)
    master_index["papers"] = {
        "paper_count": len(paper_entries),
        "total_words": sum(e["word_count"] for e in paper_entries),
        "papers": paper_entries,
    }

    # Write master index
    master_path = output_root / "index.json"
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(master_index, f, indent=2)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    grand_topics = 0
    grand_words = 0
    for key, info in master_index["products"].items():
        print(f"  {info['label']:12s}: {info['topic_count']:4d} topics, {info['total_words']:>8,} words, {info['total_size_mb']:.1f} MB")
        grand_topics += info["topic_count"]
        grand_words += info["total_words"]
    print(f"  {'Supplementary':12s}: {len(supp_entries):4d} pages")
    print(f"  {'Papers/Notes':12s}: {len(paper_entries):4d} PDFs, {sum(e['word_count'] for e in paper_entries):>8,} words")
    grand_topics += len(paper_entries)
    grand_words += sum(e["word_count"] for e in paper_entries)
    print(f"  {'TOTAL':12s}: {grand_topics:4d} topics, {grand_words:>8,} words")
    print(f"\n  Master index: {master_path}")
    print(f"  Output dir:   {output_root}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
