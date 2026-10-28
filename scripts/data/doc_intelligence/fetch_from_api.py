# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
"""REST API document fetcher for BSEE Data Center, EIA API, and IMO GISIS.

Handles auth (API keys via env vars), pagination, and rate limiting.
"""

import argparse
import json
import math
import os
import re
from collections.abc import Callable, Generator
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

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
    return deepcopy(_API_REGISTRY)


class SourceContextError(ValueError):
    """A stable validation code that never includes supplied source values."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _plain_text(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and all(character.isprintable() for character in value)
    )


def validate_source_context(
    source: str,
    endpoint: str,
    params: dict | None = None,
    api_key: str | None = None,
) -> None:
    """Validate request syntax/types without environment, filesystem or network I/O.

    Contract: docs/document-intelligence/source-context-validation.md, issue #3445.
    Endpoints are literal relative segments; one leading slash remains accepted
    for compatibility with build_api_url. Registry endpoints are examples, not an
    exhaustive capability allowlist. No API availability or authorization is proved.
    """
    if not isinstance(source, str) or source not in _API_REGISTRY:
        raise SourceContextError("UNKNOWN_SOURCE")
    if (
        not isinstance(endpoint, str)
        or re.fullmatch(r"/?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", endpoint) is None
        or any(segment in {".", ".."} for segment in endpoint.split("/"))
    ):
        raise SourceContextError("INVALID_ENDPOINT")
    if params is not None:
        if not isinstance(params, dict):
            raise SourceContextError("INVALID_PARAMS")
        for key, value in params.items():
            if not _plain_text(key):
                raise SourceContextError("INVALID_PARAMS")
            if isinstance(value, str):
                # Empty query values are valid; control characters are not.
                valid = all(character.isprintable() for character in value)
            else:
                valid = type(value) in (int, bool) or (
                    type(value) is float and math.isfinite(value)
                )
            if not valid:
                raise SourceContextError("INVALID_PARAMS")
        try:
            # Apply the runtime encoder's representability checks in every path.
            urlencode(params)
        except (ValueError, TypeError, UnicodeError, OverflowError) as exc:
            raise SourceContextError("INVALID_PARAMS") from exc
    if api_key is not None and not _plain_text(api_key):
        raise SourceContextError("INVALID_API_KEY")


def source_status(
    source: str,
    endpoint: str,
    params: dict | None = None,
    api_key: str | None = None,
) -> dict:
    """Offline preflight only: I/O validation is always explicitly deferred.

    requirements_satisfied means syntax/type preconditions only. routable_now
    remains false until execution performs I/O; this function neither reads
    credentials nor claims server access, response validity or capability support.
    """
    try:
        validate_source_context(source, endpoint, params=params, api_key=api_key)
    except SourceContextError as exc:
        return {
            "syntax_validation": "FAILED",
            "requirements_satisfied": False,
            "routable_now": False,
            "io_validation": "NOT_EVALUATED",
            "reason_codes": [exc.code],
        }
    return {
        "syntax_validation": "PASSED",
        "requirements_satisfied": True,
        "routable_now": False,
        "io_validation": "NOT_EVALUATED",
        "reason_codes": ["IO_VALIDATION_DEFERRED"],
    }


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
        SourceContextError: If the shared source syntax/type contract fails.
    """
    validate_source_context(source, endpoint, params=params, api_key=api_key)

    base_url = _API_REGISTRY[source]["base_url"]
    # Preserve the registry base path when appending the validated endpoint.
    if not base_url.endswith("/"):
        base_url += "/"
    # A single leading slash remains accepted by the source contract.
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
    validate_source_context(source, endpoint, params=params)

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
        import requests
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
    parser.add_argument("--source", help="API source")
    parser.add_argument("--endpoint", help="Endpoint path")
    parser.add_argument(
        "--status",
        action="store_true",
        help="Validate syntax offline; defer I/O checks",
    )
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

    params: dict | None = None
    try:
        if args.params:
            pairs = [pair.strip().split("=", 1) for pair in args.params.split(",")]
            if any(len(pair) != 2 or not pair[0].strip() for pair in pairs):
                raise SourceContextError("INVALID_PARAMS")
            params = dict(pairs)
        if args.status:
            print(json.dumps(source_status(args.source, args.endpoint, params=params)))
            return
        validate_source_context(args.source, args.endpoint, params=params)
    except SourceContextError as exc:
        parser.error(exc.code)

    try:
        if args.max_pages > 1:
            # Use pagination
            api_key: str | None = None
            env_var = _API_REGISTRY[args.source].get("auth_env_var")
            if env_var:
                api_key = os.environ.get(env_var)
            base_url = build_api_url(
                args.source, args.endpoint, params=params, api_key=api_key
            )
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

    except SourceContextError as exc:
        parser.error(exc.code)


if __name__ == "__main__":
    main()
