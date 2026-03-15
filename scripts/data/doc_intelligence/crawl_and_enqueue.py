# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "beautifulsoup4", "requests"]
# ///
"""Crawl seed URLs, extract document links, and enqueue for fetching."""

import argparse
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


DOCUMENT_EXTENSIONS = frozenset(
    {".pdf", ".docx", ".xlsx", ".xls", ".doc", ".csv", ".zip"}
)


def extract_document_links(html: str, base_url: str) -> list[str]:
    """Parse HTML and return deduplicated absolute URLs pointing to documents.

    Filters to links whose path ends with a supported document extension
    (.pdf, .docx, .xlsx, .xls, .doc, .csv, .zip), case-insensitive.
    Relative URLs are resolved against base_url.

    Args:
        html: Raw HTML string.
        base_url: Base URL used to resolve relative hrefs.

    Returns:
        Deduplicated list of absolute document URLs.
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    result: list[str] = []

    for tag in soup.find_all("a", href=True):
        href: str = tag["href"].strip()
        if not href:
            continue

        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)

        # Only keep http/https links
        if parsed.scheme not in ("http", "https"):
            continue

        ext = Path(parsed.path).suffix.lower()
        if ext not in DOCUMENT_EXTENSIONS:
            continue

        if absolute not in seen:
            seen.add(absolute)
            result.append(absolute)

    return result


def filter_by_domain(urls: list[str], allowed_domains: list[str]) -> list[str]:
    """Keep only URLs whose hostname is in allowed_domains.

    An empty allowed_domains list means all domains are permitted.

    Args:
        urls: List of absolute URL strings.
        allowed_domains: Allowlist of hostname strings (e.g. ["example.com"]).

    Returns:
        Filtered list of URLs.
    """
    if not allowed_domains:
        return list(urls)

    allowed_set = set(allowed_domains)
    return [u for u in urls if urlparse(u).hostname in allowed_set]


def crawl_seed_urls(
    seed_urls: list[str],
    allowed_domains: list[str] | None = None,
    fetcher=None,
) -> list[str]:
    """Fetch each seed URL, extract document links, and return deduplicated list.

    Args:
        seed_urls: Pages to crawl for document links.
        allowed_domains: Optional domain allowlist; None or [] means allow all.
        fetcher: Optional UrlFetcher-compatible object.  If None a default
            UrlFetcher is instantiated (which makes real network calls).

    Returns:
        Deduplicated list of absolute document URLs found across all seed pages.
    """
    if fetcher is None:
        from scripts.data.doc_intelligence.fetcher import UrlFetcher
        fetcher = UrlFetcher()

    seen: set[str] = set()
    result: list[str] = []

    for seed in seed_urls:
        try:
            fetch_result = fetcher.fetch(seed)
        except Exception:
            continue

        if fetch_result is None:
            continue

        html = fetch_result.content_bytes.decode("utf-8", errors="replace")
        links = extract_document_links(html, base_url=seed)

        if allowed_domains:
            links = filter_by_domain(links, allowed_domains)

        for link in links:
            if link not in seen:
                seen.add(link)
                result.append(link)

    return result


def main() -> None:
    """CLI entry point for crawl-and-enqueue."""
    parser = argparse.ArgumentParser(
        description="Crawl seed URLs and extract document links."
    )
    parser.add_argument(
        "--seeds",
        metavar="FILE",
        required=True,
        help="File with seed URLs, one per line",
    )
    parser.add_argument(
        "--allowed-domains",
        metavar="DOMAINS",
        default="",
        help="Comma-separated domain allowlist (empty = allow all)",
    )
    parser.add_argument(
        "--output-urls",
        metavar="FILE",
        help="Write discovered URL list to this file (one per line)",
    )
    parser.add_argument(
        "--create-queue",
        metavar="QUEUE_YAML",
        help="Create a YAML fetch queue at this path",
    )

    args = parser.parse_args()

    seeds_path = Path(args.seeds)
    seed_urls = [
        line.strip()
        for line in seeds_path.read_text().splitlines()
        if line.strip()
    ]

    allowed_domains = (
        [d.strip() for d in args.allowed_domains.split(",") if d.strip()]
        if args.allowed_domains
        else []
    )

    urls = crawl_seed_urls(seed_urls, allowed_domains=allowed_domains)

    if args.output_urls:
        out_path = Path(args.output_urls)
        out_path.write_text("\n".join(urls) + ("\n" if urls else ""))
        print(f"Wrote {len(urls)} URLs to {out_path}")

    if args.create_queue:
        from scripts.data.doc_intelligence.fetch_queue_manager import create_queue
        queue_path = Path(args.create_queue)
        create_queue(urls, queue_path)
        print(f"Queue created: {queue_path} ({len(urls)} URLs)")

    if not args.output_urls and not args.create_queue:
        for url in urls:
            print(url)


if __name__ == "__main__":
    main()
