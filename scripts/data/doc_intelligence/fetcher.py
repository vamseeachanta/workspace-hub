"""URL fetcher with caching, robots.txt compliance, and rate limiting."""

import hashlib
import ipaddress
import json
import logging
import socket
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests


USER_AGENT = "workspace-hub-doc-intelligence/1.0"
MAX_DOWNLOAD_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_SCHEMES = {"http", "https"}

logger = logging.getLogger(__name__)


@dataclass
class FetchResult:
    """Result of a URL fetch operation."""

    content_bytes: bytes
    content_type: str
    cached: bool
    status_code: int


def _is_private_ip(hostname: str) -> bool:
    """Return True if hostname resolves to a private/loopback/link-local IP."""
    try:
        infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC)
    except socket.gaierror:
        return False
    for _, _, _, _, sockaddr in infos:
        addr = ipaddress.ip_address(sockaddr[0])
        if addr.is_private or addr.is_loopback or addr.is_link_local:
            return True
    return False


def validate_url(url: str) -> str | None:
    """Validate URL scheme and destination. Returns error message or None."""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        return f"Blocked scheme: {parsed.scheme} (only http/https allowed)"
    hostname = parsed.hostname
    if not hostname:
        return "No hostname in URL"
    if _is_private_ip(hostname):
        return f"Blocked: {hostname} resolves to private/loopback address"
    return None


class UrlFetcher:
    """Fetch URLs with disk cache, robots.txt checking, and rate limiting."""

    def __init__(
        self,
        cache_dir: Path | None = None,
        rate_limit: float = 1.0,
        max_bytes: int = MAX_DOWNLOAD_BYTES,
    ):
        self._cache_dir = cache_dir or Path("data/doc-intelligence/cache")
        self._rate_limit = rate_limit
        self._max_bytes = max_bytes
        self._last_fetch: dict[str, float] = {}

    def _cache_path(self, url: str) -> Path:
        """Compute cache file path: {cache_dir}/{domain}/{hash[:16]}.{ext}"""
        parsed = urlparse(url)
        domain = parsed.hostname or "unknown"
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        path_part = parsed.path.rstrip("/")
        ext = Path(path_part).suffix if Path(path_part).suffix else ".html"
        return self._cache_dir / domain / f"{url_hash}{ext}"

    def _cache_meta_path(self, url: str) -> Path:
        """Path for cache metadata (content-type, final URL)."""
        return self._cache_path(url).with_suffix(".meta.json")

    def _read_cache(self, url: str) -> FetchResult | None:
        """Read cached content + metadata. Returns None on cache miss."""
        cache_path = self._cache_path(url)
        meta_path = self._cache_meta_path(url)
        if not cache_path.exists():
            return None
        # Read content type from metadata if available
        content_type = "text/html"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            content_type = meta.get("content_type", content_type)
        elif cache_path.suffix == ".pdf":
            content_type = "application/pdf"
        return FetchResult(
            content_bytes=cache_path.read_bytes(),
            content_type=content_type,
            cached=True,
            status_code=200,
        )

    def _write_cache(self, url: str, content: bytes, content_type: str) -> None:
        """Write content + metadata to cache."""
        cache_path = self._cache_path(url)
        meta_path = self._cache_meta_path(url)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(content)
        meta_path.write_text(json.dumps({
            "content_type": content_type,
            "url": url,
        }))

    def _check_robots(self, url: str) -> bool:
        """Return True if URL is allowed by robots.txt."""
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = RobotFileParser()
        try:
            resp = requests.get(
                robots_url, headers={"User-Agent": USER_AGENT}, timeout=10
            )
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
                return rp.can_fetch(USER_AGENT, url)
        except requests.RequestException:
            logger.warning(
                "robots.txt fetch failed for %s — allowing", parsed.netloc
            )
        # If robots.txt is inaccessible, assume allowed (standard convention)
        return True

    def _rate_wait(self, domain: str) -> None:
        """Enforce per-domain rate limiting."""
        if self._rate_limit <= 0:
            return
        now = time.monotonic()
        last = self._last_fetch.get(domain, 0)
        wait = self._rate_limit - (now - last)
        if wait > 0:
            time.sleep(wait)
        self._last_fetch[domain] = time.monotonic()

    def _download_with_limit(self, url: str) -> requests.Response:
        """Stream-download with size limit and redirect safety."""
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=30,
            stream=True,
            allow_redirects=False,
        )
        # Reject redirects — prevents SSRF via redirect to private IPs
        if resp.is_redirect or resp.status_code in (301, 302, 303, 307, 308):
            location = resp.headers.get("Location", "")
            resp.close()
            raise ValueError(
                f"Redirects not followed for safety: {url} -> {location}"
            )
        # Check Content-Length header first
        content_length = resp.headers.get("Content-Length")
        if content_length and int(content_length) > self._max_bytes:
            resp.close()
            raise ValueError(
                f"Response too large: {content_length} bytes "
                f"(max {self._max_bytes})"
            )
        # Stream with size tracking
        chunks = []
        total = 0
        for chunk in resp.iter_content(chunk_size=8192):
            total += len(chunk)
            if total > self._max_bytes:
                resp.close()
                raise ValueError(
                    f"Response exceeded {self._max_bytes} bytes during download"
                )
            chunks.append(chunk)
        resp._content = b"".join(chunks)
        return resp

    def fetch(self, url: str, no_cache: bool = False) -> FetchResult | None:
        """Fetch a URL, returning FetchResult or None if blocked.

        Returns None when robots.txt disallows the URL.
        Raises ValueError for blocked URLs (SSRF, size limit, redirects).
        """
        # Validate URL safety
        error = validate_url(url)
        if error:
            raise ValueError(error)

        # Check cache first (unless bypassed)
        if not no_cache:
            cached = self._read_cache(url)
            if cached:
                return cached

        # Check robots.txt
        if not self._check_robots(url):
            return None

        # Rate limit
        parsed = urlparse(url)
        domain = parsed.hostname or "unknown"
        self._rate_wait(domain)

        # Fetch with size limit
        resp = self._download_with_limit(url)

        # Parse content type (strip charset etc.)
        raw_ct = resp.headers.get("Content-Type", "text/html")
        content_type = raw_ct.split(";")[0].strip()

        result = FetchResult(
            content_bytes=resp.content,
            content_type=content_type,
            cached=False,
            status_code=resp.status_code,
        )

        # Cache successful responses with metadata
        if resp.status_code == 200:
            self._write_cache(url, resp.content, content_type)

        return result
