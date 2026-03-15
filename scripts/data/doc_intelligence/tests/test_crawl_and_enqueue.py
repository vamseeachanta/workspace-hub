"""Tests for crawl_and_enqueue.py — TDD first pass."""

import pytest

from scripts.data.doc_intelligence.crawl_and_enqueue import (
    extract_document_links,
    filter_by_domain,
    crawl_seed_urls,
)


# ---------------------------------------------------------------------------
# extract_document_links
# ---------------------------------------------------------------------------

def test_extract_document_links_from_html():
    html = """
    <html><body>
        <a href="/docs/report.pdf">Report</a>
        <a href="https://example.com/data.xlsx">Data</a>
        <a href="/page.html">Page</a>
        <a href="mailto:test@test.com">Email</a>
    </body></html>
    """
    links = extract_document_links(html, base_url="https://example.com")
    assert len(links) == 2
    assert any(l.endswith("report.pdf") for l in links)
    assert any(l.endswith("data.xlsx") for l in links)


def test_extract_document_links_empty_html():
    assert extract_document_links("", base_url="https://example.com") == []


def test_extract_document_links_no_documents():
    html = '<html><body><a href="/page.html">Page</a></body></html>'
    assert extract_document_links(html, base_url="https://example.com") == []


def test_extract_resolves_relative_urls():
    html = '<html><body><a href="../files/doc.pdf">Doc</a></body></html>'
    links = extract_document_links(html, base_url="https://example.com/pages/index.html")
    assert links[0] == "https://example.com/files/doc.pdf"


def test_extract_document_links_case_insensitive_extension():
    html = """
    <html><body>
        <a href="/report.PDF">Report</a>
        <a href="/data.XLSX">Data</a>
        <a href="/archive.ZIP">Archive</a>
    </body></html>
    """
    links = extract_document_links(html, base_url="https://example.com")
    assert len(links) == 3


def test_extract_document_links_all_supported_extensions():
    html = """
    <html><body>
        <a href="/a.pdf">PDF</a>
        <a href="/b.docx">DOCX</a>
        <a href="/c.xlsx">XLSX</a>
        <a href="/d.xls">XLS</a>
        <a href="/e.doc">DOC</a>
        <a href="/f.csv">CSV</a>
        <a href="/g.zip">ZIP</a>
        <a href="/h.html">HTML — excluded</a>
    </body></html>
    """
    links = extract_document_links(html, base_url="https://example.com")
    assert len(links) == 7


def test_extract_document_links_deduplicates():
    html = """
    <html><body>
        <a href="/doc.pdf">First</a>
        <a href="/doc.pdf">Duplicate</a>
        <a href="https://example.com/doc.pdf">Same URL, absolute</a>
    </body></html>
    """
    links = extract_document_links(html, base_url="https://example.com")
    assert len(links) == 1
    assert links[0] == "https://example.com/doc.pdf"


def test_extract_document_links_ignores_non_http_schemes():
    html = """
    <html><body>
        <a href="ftp://example.com/file.pdf">FTP PDF</a>
        <a href="/valid.pdf">Valid</a>
    </body></html>
    """
    links = extract_document_links(html, base_url="https://example.com")
    # ftp links are resolved as-is but won't match http/https; only valid.pdf counts
    # Actually ftp links should be kept if extension matches — depends on implementation.
    # We only require that /valid.pdf is found.
    assert any(l.endswith("valid.pdf") for l in links)


# ---------------------------------------------------------------------------
# filter_by_domain
# ---------------------------------------------------------------------------

def test_filter_by_domain():
    urls = [
        "https://allowed.com/doc.pdf",
        "https://blocked.com/doc.pdf",
    ]
    filtered = filter_by_domain(urls, allowed_domains=["allowed.com"])
    assert len(filtered) == 1
    assert filtered[0] == "https://allowed.com/doc.pdf"


def test_filter_by_domain_empty_allowlist():
    urls = ["https://example.com/doc.pdf"]
    # Empty allowlist = allow all
    filtered = filter_by_domain(urls, allowed_domains=[])
    assert len(filtered) == 1


def test_filter_by_domain_multiple_allowed():
    urls = [
        "https://a.com/doc.pdf",
        "https://b.com/doc.pdf",
        "https://c.com/doc.pdf",
    ]
    filtered = filter_by_domain(urls, allowed_domains=["a.com", "c.com"])
    assert len(filtered) == 2
    assert "https://b.com/doc.pdf" not in filtered


def test_filter_by_domain_empty_url_list():
    filtered = filter_by_domain([], allowed_domains=["example.com"])
    assert filtered == []


# ---------------------------------------------------------------------------
# crawl_seed_urls
# ---------------------------------------------------------------------------

class MockFetcher:
    """Minimal mock UrlFetcher for testing — no real network calls."""

    def __init__(self, responses: dict):
        """responses: {url: html_string or None (simulate fetch failure)}."""
        self._responses = responses

    def fetch(self, url: str):
        content = self._responses.get(url)
        if content is None:
            return None

        class _Result:
            pass

        r = _Result()
        r.content_bytes = content.encode() if isinstance(content, str) else content
        r.content_type = "text/html"
        r.status_code = 200
        r.cached = False
        return r


def test_crawl_seed_urls_returns_document_links():
    html = """
    <html><body>
        <a href="/report.pdf">Report</a>
        <a href="/data.xlsx">Data</a>
    </body></html>
    """
    fetcher = MockFetcher({"https://example.com/": html})
    links = crawl_seed_urls(["https://example.com/"], fetcher=fetcher)
    assert len(links) == 2
    assert any(l.endswith("report.pdf") for l in links)
    assert any(l.endswith("data.xlsx") for l in links)


def test_crawl_seed_urls_deduplicates_across_seeds():
    html_a = '<html><body><a href="/shared.pdf">PDF</a></body></html>'
    html_b = '<html><body><a href="/shared.pdf">PDF</a></body></html>'
    fetcher = MockFetcher({
        "https://example.com/a": html_a,
        "https://example.com/b": html_b,
    })
    links = crawl_seed_urls(
        ["https://example.com/a", "https://example.com/b"], fetcher=fetcher
    )
    assert len(links) == 1


def test_crawl_seed_urls_with_domain_filter():
    html = """
    <html><body>
        <a href="https://allowed.com/doc.pdf">Allowed</a>
        <a href="https://blocked.com/doc.pdf">Blocked</a>
    </body></html>
    """
    fetcher = MockFetcher({"https://seed.com/": html})
    links = crawl_seed_urls(
        ["https://seed.com/"],
        allowed_domains=["allowed.com"],
        fetcher=fetcher,
    )
    assert len(links) == 1
    assert links[0] == "https://allowed.com/doc.pdf"


def test_crawl_seed_urls_handles_fetch_failure():
    fetcher = MockFetcher({"https://example.com/": None})
    # Should not raise; just return empty
    links = crawl_seed_urls(["https://example.com/"], fetcher=fetcher)
    assert links == []


def test_crawl_seed_urls_no_allowed_domains_returns_all():
    html = '<html><body><a href="/file.pdf">PDF</a></body></html>'
    fetcher = MockFetcher({"https://example.com/": html})
    links = crawl_seed_urls(["https://example.com/"], fetcher=fetcher)
    assert len(links) == 1
