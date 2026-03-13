"""Tests for UrlFetcher — caching, content-type detection, robots.txt."""

import hashlib
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import MagicMock, patch

import pytest

from scripts.data.doc_intelligence.fetcher import FetchResult, UrlFetcher


@pytest.fixture
def cache_dir(tmp_dir):
    d = tmp_dir / "cache"
    d.mkdir()
    return d


class TestFetchResult:
    def test_fields(self):
        r = FetchResult(
            content_bytes=b"hello",
            content_type="text/html",
            cached=False,
            status_code=200,
        )
        assert r.content_bytes == b"hello"
        assert r.content_type == "text/html"
        assert r.cached is False
        assert r.status_code == 200


class TestUrlFetcherCacheKey:
    def test_cache_path_uses_domain_and_hash(self, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir)
        url = "https://example.com/page.html"
        path = fetcher._cache_path(url)
        assert "example.com" in str(path)
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        assert url_hash in path.name

    def test_cache_path_extension_from_url(self, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir)
        path = fetcher._cache_path("https://example.com/doc.pdf")
        assert path.suffix == ".pdf"

    def test_cache_path_defaults_to_html(self, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir)
        path = fetcher._cache_path("https://example.com/page")
        assert path.suffix == ".html"


class TestUrlFetcherCacheHitMiss:
    def test_cache_hit_returns_cached_content(self, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir)
        url = "https://example.com/cached.html"
        # Pre-populate cache
        cp = fetcher._cache_path(url)
        cp.parent.mkdir(parents=True, exist_ok=True)
        cp.write_bytes(b"<html>cached</html>")

        result = fetcher.fetch(url)
        assert result.cached is True
        assert result.content_bytes == b"<html>cached</html>"
        assert result.status_code == 200

    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_cache_miss_fetches_and_caches(self, mock_requests, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)
        url = "https://example.com/fresh.html"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"<html>fresh</html>"
        mock_resp.headers = {"Content-Type": "text/html; charset=utf-8"}
        mock_requests.get.return_value = mock_resp

        result = fetcher.fetch(url)
        assert result.cached is False
        assert result.content_bytes == b"<html>fresh</html>"
        assert result.content_type == "text/html"
        assert result.status_code == 200

        # Verify cached to disk
        cp = fetcher._cache_path(url)
        assert cp.exists()
        assert cp.read_bytes() == b"<html>fresh</html>"

    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_no_cache_flag_bypasses_cache(self, mock_requests, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)
        url = "https://example.com/bypass.html"

        # Pre-populate cache
        cp = fetcher._cache_path(url)
        cp.parent.mkdir(parents=True, exist_ok=True)
        cp.write_bytes(b"<html>old</html>")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"<html>new</html>"
        mock_resp.headers = {"Content-Type": "text/html"}
        mock_requests.get.return_value = mock_resp

        result = fetcher.fetch(url, no_cache=True)
        assert result.cached is False
        assert result.content_bytes == b"<html>new</html>"


class TestUrlFetcherContentType:
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_detects_pdf_content_type(self, mock_requests, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"%PDF-1.4"
        mock_resp.headers = {"Content-Type": "application/pdf"}
        mock_requests.get.return_value = mock_resp

        result = fetcher.fetch("https://example.com/doc.pdf")
        assert result.content_type == "application/pdf"


class TestUrlFetcherRobotsTxt:
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_blocked_by_robots_returns_none(self, mock_requests, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)
        url = "https://example.com/blocked"

        # Mock robots.txt response
        robots_resp = MagicMock()
        robots_resp.status_code = 200
        robots_resp.text = "User-agent: *\nDisallow: /blocked"

        mock_requests.get.return_value = robots_resp

        result = fetcher.fetch(url)
        assert result is None


class TestUrlFetcherErrors:
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_http_error_returns_result_with_status(self, mock_requests, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)

        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.content = b"Not Found"
        mock_resp.headers = {"Content-Type": "text/html"}

        # robots.txt returns 404 (allows all)
        robots_resp = MagicMock()
        robots_resp.status_code = 404
        robots_resp.text = ""
        mock_requests.get.side_effect = [robots_resp, mock_resp]

        result = fetcher.fetch("https://example.com/missing")
        assert result.status_code == 404
