"""Tests for UrlFetcher — caching, content-type, robots.txt, SSRF, size limits."""

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.data.doc_intelligence.fetcher import (
    FetchResult,
    UrlFetcher,
    validate_url,
)


@pytest.fixture
def cache_dir(tmp_dir):
    d = tmp_dir / "cache"
    d.mkdir()
    return d


def _make_stream_response(
    content: bytes, status_code=200, headers=None, is_redirect=False
):
    """Create a mock response that supports stream=True and iter_content."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.content = content
    resp.headers = headers or {"Content-Type": "text/html"}
    resp.iter_content = MagicMock(return_value=[content])
    resp.is_redirect = is_redirect
    resp.close = MagicMock()
    return resp


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


class TestValidateUrl:
    def test_http_allowed(self):
        assert validate_url("http://example.com/page") is None

    def test_https_allowed(self):
        assert validate_url("https://example.com/page") is None

    def test_file_scheme_blocked(self):
        err = validate_url("file:///etc/passwd")
        assert err is not None
        assert "scheme" in err.lower()

    def test_ftp_scheme_blocked(self):
        err = validate_url("ftp://example.com/file")
        assert err is not None

    def test_no_hostname_blocked(self):
        err = validate_url("http://")
        assert err is not None

    @patch("scripts.data.doc_intelligence.fetcher.socket.getaddrinfo")
    def test_localhost_blocked(self, mock_getaddr):
        mock_getaddr.return_value = [
            (2, 1, 6, "", ("127.0.0.1", 0)),
        ]
        err = validate_url("http://localhost/admin")
        assert err is not None
        assert "private" in err.lower() or "loopback" in err.lower()

    @patch("scripts.data.doc_intelligence.fetcher.socket.getaddrinfo")
    def test_private_ip_blocked(self, mock_getaddr):
        mock_getaddr.return_value = [
            (2, 1, 6, "", ("192.168.1.1", 0)),
        ]
        err = validate_url("http://internal-service.local/api")
        assert err is not None

    @patch("scripts.data.doc_intelligence.fetcher.socket.getaddrinfo")
    def test_public_ip_allowed(self, mock_getaddr):
        mock_getaddr.return_value = [
            (2, 1, 6, "", ("93.184.216.34", 0)),
        ]
        assert validate_url("https://example.com/page") is None


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
    @patch("scripts.data.doc_intelligence.fetcher.validate_url", return_value=None)
    def test_cache_hit_returns_cached_content(self, _mock_val, cache_dir):
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

    @patch("scripts.data.doc_intelligence.fetcher.validate_url", return_value=None)
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_cache_miss_fetches_and_caches(self, mock_requests, _mock_val, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)
        url = "https://example.com/fresh.html"

        content = b"<html>fresh</html>"
        # robots.txt → 404 (allow all)
        robots_resp = MagicMock()
        robots_resp.status_code = 404
        robots_resp.text = ""
        # actual fetch (streamed)
        fetch_resp = _make_stream_response(
            content, headers={"Content-Type": "text/html; charset=utf-8"}
        )
        mock_requests.get.side_effect = [robots_resp, fetch_resp]

        result = fetcher.fetch(url)
        assert result.cached is False
        assert result.content_bytes == content
        assert result.content_type == "text/html"
        assert result.status_code == 200

        # Verify cached to disk
        cp = fetcher._cache_path(url)
        assert cp.exists()
        assert cp.read_bytes() == content

    @patch("scripts.data.doc_intelligence.fetcher.validate_url", return_value=None)
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_no_cache_flag_bypasses_cache(self, mock_requests, _mock_val, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)
        url = "https://example.com/bypass.html"

        # Pre-populate cache
        cp = fetcher._cache_path(url)
        cp.parent.mkdir(parents=True, exist_ok=True)
        cp.write_bytes(b"<html>old</html>")

        robots_resp = MagicMock()
        robots_resp.status_code = 404
        robots_resp.text = ""
        fetch_resp = _make_stream_response(
            b"<html>new</html>", headers={"Content-Type": "text/html"}
        )
        mock_requests.get.side_effect = [robots_resp, fetch_resp]

        result = fetcher.fetch(url, no_cache=True)
        assert result.cached is False
        assert result.content_bytes == b"<html>new</html>"


class TestUrlFetcherContentType:
    @patch("scripts.data.doc_intelligence.fetcher.validate_url", return_value=None)
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_detects_pdf_content_type(self, mock_requests, _mock_val, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)

        robots_resp = MagicMock()
        robots_resp.status_code = 404
        robots_resp.text = ""
        fetch_resp = _make_stream_response(
            b"%PDF-1.4", headers={"Content-Type": "application/pdf"}
        )
        mock_requests.get.side_effect = [robots_resp, fetch_resp]

        result = fetcher.fetch("https://example.com/doc.pdf")
        assert result.content_type == "application/pdf"


class TestUrlFetcherRobotsTxt:
    @patch("scripts.data.doc_intelligence.fetcher.validate_url", return_value=None)
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_blocked_by_robots_returns_none(self, mock_requests, _mock_val, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)
        url = "https://example.com/blocked"

        robots_resp = MagicMock()
        robots_resp.status_code = 200
        robots_resp.text = "User-agent: *\nDisallow: /blocked"
        mock_requests.get.return_value = robots_resp

        result = fetcher.fetch(url)
        assert result is None


class TestUrlFetcherErrors:
    @patch("scripts.data.doc_intelligence.fetcher.validate_url", return_value=None)
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_http_error_returns_result_with_status(
        self, mock_requests, _mock_val, cache_dir
    ):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)

        robots_resp = MagicMock()
        robots_resp.status_code = 404
        robots_resp.text = ""
        fetch_resp = _make_stream_response(
            b"Not Found",
            status_code=404,
            headers={"Content-Type": "text/html"},
        )
        mock_requests.get.side_effect = [robots_resp, fetch_resp]

        result = fetcher.fetch("https://example.com/missing")
        assert result.status_code == 404


class TestUrlFetcherSizeLimit:
    @patch("scripts.data.doc_intelligence.fetcher.validate_url", return_value=None)
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_rejects_oversized_content_length(
        self, mock_requests, _mock_val, cache_dir
    ):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0, max_bytes=1024)

        robots_resp = MagicMock()
        robots_resp.status_code = 404
        robots_resp.text = ""
        fetch_resp = MagicMock()
        fetch_resp.status_code = 200
        fetch_resp.is_redirect = False
        fetch_resp.headers = {"Content-Length": "999999", "Content-Type": "text/html"}
        fetch_resp.close = MagicMock()
        mock_requests.get.side_effect = [robots_resp, fetch_resp]

        with pytest.raises(ValueError, match="too large"):
            fetcher.fetch("https://example.com/huge.html")

    @patch("scripts.data.doc_intelligence.fetcher.validate_url", return_value=None)
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_rejects_oversized_stream(self, mock_requests, _mock_val, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0, max_bytes=100)

        robots_resp = MagicMock()
        robots_resp.status_code = 404
        robots_resp.text = ""
        fetch_resp = MagicMock()
        fetch_resp.status_code = 200
        fetch_resp.is_redirect = False
        fetch_resp.headers = {"Content-Type": "text/html"}
        fetch_resp.iter_content = MagicMock(
            return_value=[b"x" * 60, b"x" * 60]
        )
        fetch_resp.close = MagicMock()
        mock_requests.get.side_effect = [robots_resp, fetch_resp]

        with pytest.raises(ValueError, match="exceeded"):
            fetcher.fetch("https://example.com/stream.html")


class TestUrlFetcherRedirectBlocking:
    @patch("scripts.data.doc_intelligence.fetcher.validate_url", return_value=None)
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_redirect_raises_valueerror(self, mock_requests, _mock_val, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)

        robots_resp = MagicMock()
        robots_resp.status_code = 404
        robots_resp.text = ""
        redirect_resp = _make_stream_response(
            b"",
            status_code=302,
            headers={"Location": "http://127.0.0.1/admin", "Content-Type": "text/html"},
            is_redirect=True,
        )
        mock_requests.get.side_effect = [robots_resp, redirect_resp]

        with pytest.raises(ValueError, match="Redirect"):
            fetcher.fetch("https://example.com/redirect")


class TestUrlFetcherCacheMetadata:
    @patch("scripts.data.doc_intelligence.fetcher.validate_url", return_value=None)
    @patch("scripts.data.doc_intelligence.fetcher.requests")
    def test_extensionless_pdf_url_preserves_content_type_in_cache(
        self, mock_requests, _mock_val, cache_dir
    ):
        """PDF served from extensionless URL should be cached with correct type."""
        fetcher = UrlFetcher(cache_dir=cache_dir, rate_limit=0)
        url = "https://example.com/download?id=123"

        robots_resp = MagicMock()
        robots_resp.status_code = 404
        robots_resp.text = ""
        fetch_resp = _make_stream_response(
            b"%PDF-1.4", headers={"Content-Type": "application/pdf"}
        )
        mock_requests.get.side_effect = [robots_resp, fetch_resp]

        # First fetch
        result = fetcher.fetch(url)
        assert result.content_type == "application/pdf"
        assert result.cached is False

        # Second fetch (from cache) — should preserve content type
        result2 = fetcher.fetch(url)
        assert result2.cached is True
        assert result2.content_type == "application/pdf"


class TestUrlFetcherSsrf:
    def test_file_url_raises(self, cache_dir):
        fetcher = UrlFetcher(cache_dir=cache_dir)
        with pytest.raises(ValueError, match="scheme"):
            fetcher.fetch("file:///etc/passwd")

    @patch("scripts.data.doc_intelligence.fetcher.socket.getaddrinfo")
    def test_localhost_raises(self, mock_getaddr, cache_dir):
        mock_getaddr.return_value = [(2, 1, 6, "", ("127.0.0.1", 0))]
        fetcher = UrlFetcher(cache_dir=cache_dir)
        with pytest.raises(ValueError, match="private"):
            fetcher.fetch("http://localhost/admin")
