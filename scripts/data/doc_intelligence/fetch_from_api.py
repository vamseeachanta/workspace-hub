# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
"""REST API document fetcher for BSEE Data Center, EIA API, and IMO GISIS.

Handles auth (API keys via env vars), pagination, and rate limiting.
"""
import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Generator
from urllib.parse import urlencode, urljoin

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_API_REGISTRY: dict[str, dict] = {
    "bsee": {
        "base_url": "https://www.data.bsee.gov/Main/",
        "auth_type": "public",
        "auth_env_var": None,
        "endpoints": [
            "Production",
            "WellProduction",
            "Incidents",
            "InspectionScores",
        ],
    },
    "eia": {
        "base_url": "https://api.eia.gov/v2/",
        "auth_type": "api_key",
        "auth_env_var": "EIA_API_KEY",
        "endpoints": [
            "petroleum/summary",
            "natural-gas/sum/lsum/us",
            "electricity/retail-sales",
            "total-energy/data",
        ],
    },
    "imo": {
        "base_url": "https://gisis.imo.org/",
        "auth_type": "optional",
        "auth_env_var": "IMO_API_KEY",
        "endpoints": [
            "ships/search",
            "ships/details",
            "ports/search",
        ],
    },
}


def get_api_registry() -> dict[str, dict]:
    """Return dict describing all supported APIs.

    Returns:
        {source: {base_url, auth_type, auth_env_var, endpoints: [...]}}
    """
    return {source: dict(info) for source, info in _API_REGISTRY.items()}


# ---------------------------------------------------------------------------
# URL building
# ---------------------------------------------------------------------------


def build_api_url(
    source: str,
    endpoint: str,
    params: dict | None = None,
    api_key: str | None = None,
) -> str:
    """Build URL for a known API source.

    Args:
        source: One of 'bsee', 'eia', 'imo'.
        endpoint: Path appended to the base URL.
        params: Optional query parameters dict.
        api_key: Optional API key to include as query param.

    Returns:
        Full URL string with query params.

    Raises:
        ValueError: If source is not recognised.
    """
    if source not in _API_REGISTRY:
        raise ValueError(
            f"Unknown source '{source}'. "
            f"Known sources: {list(_API_REGISTRY.keys())}"
        )

    base_url = _API_REGISTRY[source]["base_url"]
    # Ensure base ends with / so urljoin appends correctly
    if not base_url.endswith("/"):
        base_url += "/"
    # Strip leading slash from endpoint to avoid urljoin swallowing the path
    url = base_url + endpoint.lstrip("/")

    query: dict[str, str] = {}
    if params:
        query.update(params)
    if api_key:
        query["api_key"] = api_key

    if query:
        url = f"{url}?{urlencode(query)}"

    return url


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


def paginate_results(
    fetcher_fn: Callable[[str], list],
    url: str,
    page_size: int = 100,
    max_pages: int = 10,
    page_param: str = "offset",
    size_param: str = "length",
) -> Generator[list, None, None]:
    """Generator that yields pages of results.

    Calls fetcher_fn(url_with_pagination) for each page.

    Stops when:
    - max_pages reached
    - response has fewer items than page_size
    - empty response

    Args:
        fetcher_fn: Callable that accepts a URL and returns a list of records.
        url: Base URL (without pagination params).
        page_size: Number of records per page.
        max_pages: Maximum number of pages to fetch.
        page_param: Query parameter name for the offset/page cursor.
        size_param: Query parameter name for the page size.

    Yields:
        List of records for each page.
    """
    separator = "&" if "?" in url else "?"

    for page_num in range(max_pages):
        offset = page_num * page_size
        paginated_url = (
            f"{url}{separator}{size_param}={page_size}&{page_param}={offset}"
        )
        page_data = fetcher_fn(paginated_url)

        if not page_data:
            return

        yield page_data

        if len(page_data) < page_size:
            return


# ---------------------------------------------------------------------------
# Main fetch function
# ---------------------------------------------------------------------------


def fetch_api_data(
    source: str,
    endpoint: str,
    params: dict | None = None,
    output_dir: str | None = None,
    fetcher: Callable[[str], Any] | None = None,
) -> Any:
    """Fetch data from a known API.

    Handles API key lookup from env vars (EIA_API_KEY, etc.).
    Saves response to output_dir if provided.

    Args:
        source: API source name ('bsee', 'eia', 'imo').
        endpoint: API endpoint path.
        params: Optional query parameters.
        output_dir: If given, save response JSON here.
        fetcher: Optional callable(url) → parsed JSON. Defaults to requests.get.

    Returns:
        Response data (parsed JSON dict/list).
    """
    if source not in _API_REGISTRY:
        raise ValueError(f"Unknown source '{source}'")

    registry_entry = _API_REGISTRY[source]

    # Resolve API key from environment if applicable
    api_key: str | None = None
    env_var = registry_entry.get("auth_env_var")
    if env_var:
        api_key = os.environ.get(env_var)

    url = build_api_url(source, endpoint, params=params, api_key=api_key)

    if fetcher is None:
        fetcher = _default_fetcher

    result = fetcher(url)

    if output_dir is not None:
        _save_response(result, source, endpoint, output_dir)

    return result


def _default_fetcher(url: str) -> Any:
    """Default HTTP fetcher using requests."""
    try:
        import requests  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError("requests is required: uv add requests") from exc

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def _save_response(data: Any, source: str, endpoint: str, output_dir: str) -> Path:
    """Persist API response to a JSON file."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    # Build a filesystem-safe filename
    safe_endpoint = endpoint.replace("/", "_").replace("\\", "_")
    filename = f"{source}_{safe_endpoint}.json"
    dest = out_path / filename
    dest.write_text(json.dumps(data, indent=2))
    return dest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """Command-line interface for fetch_from_api."""
    parser = argparse.ArgumentParser(
        description="REST API fetcher for BSEE, EIA, and IMO GISIS"
    )
    parser.add_argument("--source", choices=list(_API_REGISTRY.keys()), help="API source")
    parser.add_argument("--endpoint", help="Endpoint path")
    parser.add_argument(
        "--params",
        default="",
        help="Query params as key=value,key=value",
    )
    parser.add_argument("--output-dir", help="Directory to save response JSON")
    parser.add_argument("--max-pages", type=int, default=1, help="Max pages to fetch")
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="Print API registry and exit",
    )

    args = parser.parse_args()

    if args.list_sources:
        registry = get_api_registry()
        print(json.dumps(registry, indent=2))
        return

    if not args.source or not args.endpoint:
        parser.error("--source and --endpoint are required unless --list-sources is set")

    params: dict | None = None
    if args.params:
        pairs = [p.strip() for p in args.params.split(",") if "=" in p]
        params = dict(kv.split("=", 1) for kv in pairs)

    if args.max_pages > 1:
        # Use pagination
        api_key: str | None = None
        env_var = _API_REGISTRY[args.source].get("auth_env_var")
        if env_var:
            api_key = os.environ.get(env_var)
        base_url = build_api_url(args.source, args.endpoint, params=params, api_key=api_key)
        all_records: list = []
        for page in paginate_results(
            _default_fetcher,
            base_url,
            max_pages=args.max_pages,
        ):
            all_records.extend(page if isinstance(page, list) else [page])

        if args.output_dir:
            _save_response(all_records, args.source, args.endpoint, args.output_dir)
        else:
            print(json.dumps(all_records, indent=2))
    else:
        result = fetch_api_data(
            args.source,
            args.endpoint,
            params=params,
            output_dir=args.output_dir,
        )
        if not args.output_dir:
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
