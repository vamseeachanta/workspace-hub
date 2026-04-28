#!/usr/bin/env python3
"""Ingest Orcina product documentation into llm-wiki.

Ref: GH #2088, #2125
"""

from __future__ import annotations

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

from orcina_refresh import (
    HEADERS,
    atomic_write_json,
    atomic_write_text,
    fetch_conditional,
    has_changes,
    head_pdf,
    safe_get_papers_entry,
    sha256_hex,
    write_changelog,
)
from orcina_version import detect_current_version, diff_versions
from resolve_wiki_path import resolve_wiki_dir

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

PAPERS_PAGE = "https://www.orcina.com/resources/papers-and-technical-notes/"
DELAY_SECONDS = 0.3


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def empty_changes() -> dict[str, list[str]]:
    return {"added": [], "removed": [], "modified": []}


def parse_toc_xml(toc_url: str) -> list[dict]:
    """Parse MadCap Flare Toc.xml and return topic entries."""
    req = urllib.request.Request(toc_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode("utf-8", errors="replace")

    soup = BeautifulSoup(content, "html.parser")
    entries = []
    for tag in soup.find_all("tocentry"):
        link = tag.get("link")
        if not link:
            continue
        section_path = []
        for parent in tag.parents:
            if getattr(parent, "name", None) == "tocentry" and parent.get("title"):
                section_path.append(parent.get("title"))
        section_path.reverse()
        entries.append({
            "link": link,
            "title": tag.get("title", ""),
            "section_path": section_path,
        })
    return entries


def html_to_markdown(html_content: str, source_url: str = "") -> tuple[str, str]:
    """Convert HTML to simple markdown. Returns (title, markdown)."""
    soup = BeautifulSoup(html_content, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "link", "meta", "noscript"]):
        tag.decompose()

    main = soup.find("body") or soup
    md_lines: list[str] = []
    _convert_element(main, md_lines)
    markdown = re.sub(r"\n{3,}", "\n\n", "\n".join(md_lines)).strip()
    if source_url:
        markdown = f"<!-- source: {source_url} -->\n\n{markdown}"
    return title, markdown


def _convert_element(element, lines: list[str], depth: int = 0) -> None:
    from bs4 import NavigableString, Tag

    if isinstance(element, NavigableString):
        text = str(element).strip()
        if text:
            lines.append(text)
        return
    if not isinstance(element, Tag):
        return

    classes = element.get("class", [])
    if any(c.startswith("MCBreadcrumbs") for c in classes):
        return

    tag = element.name
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        text = element.get_text(strip=True)
        if text:
            lines.append(f"\n{'#' * int(tag[1])} {text}\n")
        return
    if tag == "p":
        text = element.get_text(" ", strip=True)
        if text:
            lines.append(f"\n{text}\n")
        return
    if tag in ("ul", "ol"):
        for i, li in enumerate(element.find_all("li", recursive=False)):
            prefix = f"{i + 1}." if tag == "ol" else "-"
            text = li.get_text(" ", strip=True)
            if text:
                lines.append(f"{prefix} {text}")
        lines.append("")
        return
    if tag == "table":
        _convert_table(element, lines)
        return
    if tag == "pre":
        lines.append(f"\n```\n{element.get_text()}\n```\n")
        return

    for child in element.children:
        _convert_element(child, lines, depth + 1)


def _convert_table(table, lines: list[str]) -> None:
    rows = table.find_all("tr")
    md_rows = []
    for row in rows:
        cells = row.find_all(["th", "td"])
        cell_texts = [c.get_text(strip=True).replace("|", "\\|").replace("\n", " ") for c in cells]
        if cell_texts:
            md_rows.append("| " + " | ".join(cell_texts) + " |")
    if not md_rows:
        return
    lines.append("")
    lines.append(md_rows[0])
    ncols = max(row.count("|") - 1 for row in md_rows)
    lines.append("|" + "|".join(["---"] * max(ncols, 1)) + "|")
    lines.extend(md_rows[1:])
    lines.append("")


def fetch_page(url: str) -> str | None:
    """Fetch a URL as UTF-8 text, falling back to URL-encoded paths."""
    for candidate in (url, _quote_path(url)):
        try:
            req = urllib.request.Request(candidate, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception:
            continue
    return None


def _quote_path(url: str) -> str:
    from urllib.parse import urlparse, urlunparse

    parts = urlparse(url)
    return urlunparse(parts._replace(path=quote(parts.path, safe="/")))


def topic_url(info: dict, link: str) -> str:
    return info["base_url"] + link


def topic_filename(link: str) -> str:
    md_filename = re.sub(r"\.html?$", ".md", link.lstrip("/"), flags=re.IGNORECASE)
    md_filename = md_filename.replace(" ", "_")
    return re.sub(r"^Content/html/", "", md_filename)


def build_topic_entry(md_filename: str, title: str, toc_entry: dict, page_url: str, markdown: str, http_meta: dict | None = None) -> dict:
    sections = re.findall(r"^#{1,3}\s+(.+)$", markdown, re.MULTILINE)[:15]
    entry = {
        "file": md_filename,
        "title": title,
        "section_path": toc_entry.get("section_path", []),
        "sections": sections,
        "source_url": page_url,
        "size_bytes": len(markdown),
        "word_count": len(markdown.split()),
    }
    if http_meta is not None:
        entry["http_meta"] = http_meta
    return entry


def ingest_product(
    product_key: str,
    info: dict,
    output_root: Path,
    refresh: bool = False,
    force_full: bool = False,
    upstream_version: str | None = None,
) -> dict:
    """Ingest all topics for one product."""
    print(f"\n{'=' * 60}\nProcessing {info['label']} ({product_key})\n{'=' * 60}")

    product_dir = output_root / product_key / "topics"
    product_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_root / product_key / "index.json"
    stored = _read_json(index_path) if refresh and not force_full else {}
    stored_topics_by_url = {t.get("source_url"): t for t in stored.get("topics", []) if t.get("source_url")}

    print(f"  Fetching TOC from {info['toc_url']} ...")
    toc_entries = parse_toc_xml(info["toc_url"])
    print(f"  Found {len(toc_entries)} topic pages in TOC")

    entries = []
    errors = 0
    skipped = 0
    changes = empty_changes()
    use_refresh_cache = refresh and not force_full and index_path.exists()

    for i, toc_entry in enumerate(toc_entries):
        link = toc_entry["link"]
        page_url = topic_url(info, link)
        title_from_toc = toc_entry["title"]
        if (i + 1) % 25 == 0 or i == 0:
            print(f"  [{i + 1}/{len(toc_entries)}] {title_from_toc}")

        cached = stored_topics_by_url.get(page_url) if use_refresh_cache else None
        body: bytes | None
        http_meta: dict | None = None
        if cached:
            status, http_meta, body = fetch_conditional(page_url, cached.get("http_meta"))
            if status == "unchanged":
                entries.append({**cached, "http_meta": http_meta})
                continue
            html = (body or b"").decode("utf-8", errors="replace")
            changes["modified"].append(page_url)
        else:
            html = fetch_page(page_url)
            if use_refresh_cache:
                changes["added"].append(page_url)

        if html is None or len(html) < 200:
            errors += 1
            continue

        title, markdown = html_to_markdown(html, page_url)
        title = title or title_from_toc
        if not markdown or len(markdown) < 30:
            skipped += 1
            continue

        md_filename = topic_filename(link)
        out_path = product_dir / md_filename
        atomic_write_text(out_path, f"# {title}\n\n{markdown}")
        entries.append(build_topic_entry(md_filename, title, toc_entry, page_url, markdown, http_meta))
        time.sleep(DELAY_SECONDS)

    live_urls = {topic_url(info, entry["link"]) for entry in toc_entries}
    if use_refresh_cache:
        for url in stored_topics_by_url:
            if url not in live_urls:
                changes["removed"].append(url)

    total_words = sum(e["word_count"] for e in entries)
    total_bytes = sum(e["size_bytes"] for e in entries)
    product_index = {
        "product": info["label"],
        "base_url": info["base_url"],
        "generated": utcnow_iso(),
        "topic_count": len(entries),
        "total_words": total_words,
        "total_size_mb": round(total_bytes / 1024 / 1024, 2),
        "errors": errors,
        "skipped": skipped,
        "upstream_version": upstream_version,
        "topics": entries,
    }
    atomic_write_json(index_path, product_index)

    print(f"  Done: {len(entries)} topics, {total_words:,} words, {total_bytes / 1024 / 1024:.1f} MB")
    print(f"  Errors: {errors}, Skipped: {skipped}")
    return {
        "label": info["label"],
        "topic_count": len(entries),
        "total_words": total_words,
        "total_size_mb": round(total_bytes / 1024 / 1024, 2),
        "errors": errors,
        "index_path": f"{product_key}/index.json",
        "product_key": product_key,
        "entries": entries,
        "changes": changes,
        "stored_version": stored.get("upstream_version"),
    }


def ingest_supplementary(output_root: Path, refresh: bool = False, force_full: bool = False) -> dict:
    """Fetch supplementary resource pages."""
    print(f"\n{'=' * 60}\nProcessing supplementary pages\n{'=' * 60}")
    supp_dir = output_root / "supplementary"
    supp_dir.mkdir(parents=True, exist_ok=True)
    meta_path = supp_dir / "supplementary_meta.json"
    stored_meta = _read_json(meta_path) if refresh and not force_full else {}

    entries = []
    new_meta = {}
    changes = empty_changes()
    versions = {"orcaflex": None, "orcawave": None, "orcfxapi": None}

    for name, url in SUPPLEMENTARY_URLS:
        print(f"  Fetching {name} from {url}")
        cached = stored_meta.get(url) if refresh and not force_full else None
        if cached:
            status, meta, body = fetch_conditional(url, cached)
            new_meta[url] = meta
            if status == "unchanged":
                existing = _supplementary_entry(supp_dir / f"{name}.md", name, url)
                if existing:
                    entries.append(existing)
                continue
            html = (body or b"").decode("utf-8", errors="replace")
            changes["modified"].append(url)
        else:
            html = fetch_page(url)
            if refresh and not force_full:
                changes["added"].append(url)
            if html is not None:
                new_meta[url] = {"last_modified": None, "etag": None, "content_hash": sha256_hex(html.encode("utf-8"))}

        if html is None:
            print("    FAILED")
            continue

        if name == "releases":
            versions = detect_current_version(html)

        title, markdown = html_to_markdown(html, url)
        if not markdown:
            continue
        out_path = supp_dir / f"{name}.md"
        atomic_write_text(out_path, (f"# {title}\n\n" if title else "") + markdown)
        entries.append({
            "file": f"supplementary/{name}.md",
            "title": title or name,
            "source_url": url,
            "size_bytes": len(markdown),
            "word_count": len(markdown.split()),
        })
        time.sleep(DELAY_SECONDS)

    for url in stored_meta:
        if url not in new_meta:
            changes["removed"].append(url)

    atomic_write_json(meta_path, new_meta)
    return {"entries": entries, "changes": changes, "versions": versions}


def _supplementary_entry(path: Path, name: str, url: str) -> dict | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    return {
        "file": f"supplementary/{name}.md",
        "title": name,
        "source_url": url,
        "size_bytes": len(text),
        "word_count": len(text.split()),
    }


def extract_pdf_links(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf") and "orcina.com" in href:
            pdf_links.append({"url": href, "title": a.get_text(strip=True) or Path(href).stem})
    seen = set()
    unique = []
    for item in pdf_links:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)
    return unique


def safe_pdf_filename(url: str) -> str:
    return re.sub(r"[^\w\-.]", "_", Path(url).stem)


def download_bytes(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def pdftotext_bytes(pdf_bytes: bytes) -> str:
    tmp_dir = tempfile.mkdtemp(prefix="orcina-pdfs-")
    pdf_path = os.path.join(tmp_dir, "source.pdf")
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    result = subprocess.run(["pdftotext", "-layout", pdf_path, "-"], capture_output=True, text=True, timeout=30)
    return result.stdout.strip()


def ingest_papers(output_root: Path, refresh: bool = False, force_full: bool = False) -> dict:
    """Scrape papers, download PDFs, and convert changed PDFs to markdown."""
    print(f"\n{'=' * 60}\nProcessing papers & technical notes (PDFs)\n{'=' * 60}")
    papers_dir = output_root / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)
    meta_path = papers_dir / "papers_meta.json"
    stored_meta = _read_json(meta_path) if refresh and not force_full else {}

    print(f"  Fetching papers listing from {PAPERS_PAGE}")
    html = fetch_page(PAPERS_PAGE)
    if html is None:
        print("  FAILED to fetch papers page")
        return {"entries": [], "changes": empty_changes()}

    pdf_links = extract_pdf_links(html)
    print(f"  Found {len(pdf_links)} PDF links")
    entries = []
    new_meta = {}
    changes = empty_changes()

    for i, pdf_info in enumerate(pdf_links):
        url = pdf_info["url"]
        title = pdf_info["title"]
        safe_filename = safe_pdf_filename(url)
        print(f"  [{i + 1}/{len(pdf_links)}] {title[:60]}")

        cached = stored_meta.get(url) if refresh and not force_full else None
        head = head_pdf(url) if refresh and not force_full else None
        if cached and head and cached.get("last_modified") == head.get("last_modified") and cached.get("content_length") == head.get("content_length"):
            entry = safe_get_papers_entry(stored_meta, url)
            if entry:
                new_meta[url] = cached
                entries.append(entry)
                continue

        try:
            pdf_bytes = download_bytes(url)
        except Exception as exc:
            print(f"    Download failed: {exc}")
            continue
        bytes_hash = sha256_hex(pdf_bytes)
        if cached and cached.get("bytes_sha256") == bytes_hash:
            entry = safe_get_papers_entry(stored_meta, url)
            if entry:
                new_meta[url] = {
                    **cached,
                    "last_modified": (head or {}).get("last_modified"),
                    "content_length": (head or {}).get("content_length"),
                }
                entries.append(entry)
                continue

        try:
            text = pdftotext_bytes(pdf_bytes)
        except Exception as exc:
            print(f"    pdftotext failed: {exc}")
            continue
        if not text or len(text) < 100:
            print("    Skipped (empty/too short)")
            continue

        markdown = f"<!-- source: {url} -->\n\n# {title}\n\n{text}"
        out_path = papers_dir / f"{safe_filename}.md"
        atomic_write_text(out_path, markdown)
        entry = {
            "file": f"papers/{safe_filename}.md",
            "title": title,
            "source_url": url,
            "size_bytes": len(markdown),
            "word_count": len(markdown.split()),
            "type": "pdf",
            "downloaded": utcnow_iso(),
        }
        new_meta[url] = {
            "last_modified": (head or {}).get("last_modified"),
            "content_length": (head or {}).get("content_length"),
            "bytes_sha256": bytes_hash,
            "entry": entry,
        }
        entries.append(entry)
        if cached:
            changes["modified"].append(url)
        elif refresh and not force_full:
            changes["added"].append(url)
        time.sleep(DELAY_SECONDS)

    for url in stored_meta:
        if url in new_meta:
            continue
        changes["removed"].append(url)
        entry = safe_get_papers_entry(stored_meta, url)
        if not entry:
            print(f"  Warning: legacy/partial papers_meta entry for {url}; skipping disk delete")
            continue
        try:
            (papers_dir / Path(entry["file"]).name).unlink()
        except FileNotFoundError:
            pass

    atomic_write_json(meta_path, new_meta)
    print(f"  Done: {len(entries)} papers converted, {sum(e.get('word_count', 0) for e in entries):,} words")
    return {"entries": entries, "changes": changes}


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def version_label(versions: dict[str, str | None]) -> str:
    for key in ("orcaflex", "orcawave", "orcfxapi"):
        if versions.get(key):
            return f"{key}-{versions[key]}"
    return "unknown-version"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest Orcina docs into llm-wiki")
    parser.add_argument("--output-dir", default=None, help="Root output directory")
    parser.add_argument("--products", nargs="*", default=list(PRODUCTS.keys()), choices=list(PRODUCTS.keys()))
    parser.add_argument("--refresh", action="store_true", help="Only reprocess changed upstream content")
    parser.add_argument("--force-full", action="store_true", help="Ignore refresh cache and perform a full crawl")
    args = parser.parse_args(argv)

    output_root = Path(args.output_dir) if args.output_dir else resolve_wiki_dir()
    output_root.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_root}")
    print(f"Products:         {', '.join(args.products)}")
    print(f"Crawl delay:      {DELAY_SECONDS}s")

    supp_result = ingest_supplementary(output_root, refresh=args.refresh, force_full=args.force_full)
    current_versions = supp_result.get("versions", {})
    stored_versions = {}
    product_results = []

    for product_key in args.products:
        stored_versions[product_key] = _read_json(output_root / product_key / "index.json").get("upstream_version")
        product_results.append(
            ingest_product(
                product_key,
                PRODUCTS[product_key],
                output_root,
                refresh=args.refresh,
                force_full=args.force_full,
                upstream_version=current_versions.get(product_key),
            )
        )

    paper_result = ingest_papers(output_root, refresh=args.refresh, force_full=args.force_full)
    master_index = {
        "generated": utcnow_iso(),
        "generator": "ingest-orcina.py",
        "issue": "https://github.com/vamseeachanta/workspace-hub/issues/2088",
        "products": {r["product_key"]: {k: v for k, v in r.items() if k not in ("entries", "changes", "product_key", "stored_version")} for r in product_results},
        "supplementary": {"page_count": len(supp_result["entries"]), "pages": supp_result["entries"]},
        "papers": {
            "paper_count": len(paper_result["entries"]),
            "total_words": sum(e.get("word_count", 0) for e in paper_result["entries"]),
            "papers": paper_result["entries"],
        },
    }
    atomic_write_json(output_root / "index.json", master_index)

    all_changes = {
        "product_topics": {r["product_key"]: r["changes"] for r in product_results},
        "supplementary": supp_result["changes"],
        "papers": paper_result["changes"],
        "version_bump": diff_versions(stored_versions, current_versions) if args.refresh else {},
    }
    if args.refresh and has_changes(all_changes):
        path = write_changelog(output_root, version_label(current_versions), all_changes)
        print(f"  Changelog: {path}")

    print(f"\n{'=' * 60}\nSUMMARY\n{'=' * 60}")
    for info in master_index["products"].values():
        print(f"  {info['label']:12s}: {info['topic_count']:4d} topics, {info['total_words']:>8,} words, {info['total_size_mb']:.1f} MB")
    print(f"  {'Supplementary':12s}: {len(supp_result['entries']):4d} pages")
    print(f"  {'Papers/Notes':12s}: {len(paper_result['entries']):4d} PDFs, {sum(e.get('word_count', 0) for e in paper_result['entries']):>8,} words")
    print(f"\n  Master index: {output_root / 'index.json'}")
    print(f"  Output dir:   {output_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
