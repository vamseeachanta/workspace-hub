"""URL fetcher with caching, robots.txt compliance, and rate limiting."""

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests


USER_AGENT = "workspace-hub-doc-intelligence/1.0"


@dataclass
class FetchResult:
    """Result of a URL fetch operation."""

    content_bytes: bytes
    content_type: str
    cached: bool
    status_code: int


class UrlFetcher:
    """Fetch URLs with disk cache, robots.txt checking, and rate limiting."""

    def __init__(
        self,
        cache_dir: Path | None = None,
        rate_limit: float = 1.0,
    ):
        self._cache_dir = cache_dir or Path("data/doc-intelligence/cache")
        self._rate_limit = rate_limit
        self._last_fetch: dict[str, float] = {}

    def _cache_path(self, url: str) -> Path:
        """Compute cache file path: {cache_dir}/{domain}/{hash[:16]}.{ext}"""
        parsed = urlparse(url)
        domain = parsed.hostname or "unknown"
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        path_part = parsed.path.rstrip("/")
        ext = Path(path_part).suffix if Path(path_part).suffix else ".html"
        return self._cache_dir / domain / f"{url_hash}{ext}"

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
            pass
        # If robots.txt is inaccessible, assume allowed
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

    def fetch(self, url: str, no_cache: bool = False) -> FetchResult | None:
        """Fetch a URL, returning FetchResult or None if blocked by robots.txt.

        Returns None when robots.txt disallows the URL.
        """
        cache_path = self._cache_path(url)

        # Check cache first (unless bypassed)
        if not no_cache and cache_path.exists():
            content_type = (
                "application/pdf" if cache_path.suffix == ".pdf" else "text/html"
            )
            return FetchResult(
                content_bytes=cache_path.read_bytes(),
                content_type=content_type,
                cached=True,
                status_code=200,
            )

        # Check robots.txt
        if not self._check_robots(url):
            return None

        # Rate limit
        parsed = urlparse(url)
        domain = parsed.hostname or "unknown"
        self._rate_wait(domain)

        # Fetch
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)

        # Parse content type (strip charset etc.)
        raw_ct = resp.headers.get("Content-Type", "text/html")
        content_type = raw_ct.split(";")[0].strip()

        result = FetchResult(
            content_bytes=resp.content,
            content_type=content_type,
            cached=False,
            status_code=resp.status_code,
        )

        # Cache successful responses
        if resp.status_code == 200:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(resp.content)

        return result
