# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest", "requests"]
# ///
"""Tests for fetch_from_api.py — REST API fetcher for BSEE/EIA/IMO."""
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Allow import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from fetch_from_api import (
    build_api_url,
    fetch_api_data,
    get_api_registry,
    paginate_results,
)


# ---------------------------------------------------------------------------
# build_api_url
# ---------------------------------------------------------------------------


def test_build_bsee_url():
    url = build_api_url("bsee", endpoint="Production", params={"year": "2024"})
    assert "data.bsee.gov" in url
    assert "year=2024" in url


def test_build_eia_url_includes_api_key():
    url = build_api_url("eia", endpoint="petroleum/summary", api_key="test123")
    assert "api.eia.gov" in url
    assert "api_key=test123" in url


def test_build_imo_url():
    url = build_api_url("imo", endpoint="ships/search")
    assert "gisis.imo.org" in url
    assert "ships/search" in url


def test_build_unknown_source_raises():
    with pytest.raises(ValueError, match="Unknown source"):
        build_api_url("unknown", endpoint="test")


def test_build_url_with_multiple_params():
    url = build_api_url("bsee", endpoint="WellProduction", params={"year": "2024", "state": "LA"})
    assert "year=2024" in url
    assert "state=LA" in url


def test_build_url_no_params():
    url = build_api_url("bsee", endpoint="Production")
    assert "data.bsee.gov" in url
    assert "Production" in url


# ---------------------------------------------------------------------------
# get_api_registry
# ---------------------------------------------------------------------------


def test_get_api_registry():
    registry = get_api_registry()
    assert "bsee" in registry
    assert "eia" in registry
    assert "imo" in registry
    assert "base_url" in registry["bsee"]


def test_registry_has_auth_info():
    registry = get_api_registry()
    for source, info in registry.items():
        assert "auth_type" in info, f"{source} missing auth_type"
        assert "base_url" in info, f"{source} missing base_url"


def test_registry_eia_has_api_key_env():
    registry = get_api_registry()
    assert registry["eia"]["auth_type"] == "api_key"
    assert "auth_env_var" in registry["eia"]
    assert registry["eia"]["auth_env_var"] == "EIA_API_KEY"


def test_registry_has_endpoints():
    registry = get_api_registry()
    for source, info in registry.items():
        assert "endpoints" in info, f"{source} missing endpoints"
        assert isinstance(info["endpoints"], list)


# ---------------------------------------------------------------------------
# paginate_results
# ---------------------------------------------------------------------------


def test_paginate_stops_on_empty():
    call_count = 0

    def mock_fetcher(url):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return [{"id": i} for i in range(100)]
        return []  # empty = stop

    pages = list(
        paginate_results(
            mock_fetcher,
            "https://example.com/api",
            page_size=100,
            max_pages=10,
        )
    )
    assert len(pages) == 2
    assert call_count == 3


def test_paginate_stops_on_max_pages():
    def mock_fetcher(url):
        return [{"id": 1}] * 100

    pages = list(
        paginate_results(
            mock_fetcher,
            "https://example.com/api",
            page_size=100,
            max_pages=3,
        )
    )
    assert len(pages) == 3


def test_paginate_stops_on_partial_page():
    def mock_fetcher(url):
        return [{"id": 1}] * 50  # less than page_size

    pages = list(
        paginate_results(
            mock_fetcher,
            "https://example.com/api",
            page_size=100,
            max_pages=10,
        )
    )
    assert len(pages) == 1


def test_paginate_url_includes_offset_param():
    received_urls = []

    def mock_fetcher(url):
        received_urls.append(url)
        return [{"id": 1}] * 100

    pages = list(
        paginate_results(
            mock_fetcher,
            "https://example.com/api",
            page_size=100,
            max_pages=2,
            page_param="offset",
            size_param="length",
        )
    )
    assert len(pages) == 2
    assert "offset=0" in received_urls[0] or "offset=0" in received_urls[0]
    assert "length=100" in received_urls[0]
    # Second page should have offset=100
    assert "offset=100" in received_urls[1]


def test_paginate_yields_page_data():
    def mock_fetcher(url):
        return [{"id": 42}]

    pages = list(
        paginate_results(
            mock_fetcher,
            "https://example.com/api",
            page_size=100,
            max_pages=1,
        )
    )
    assert pages[0] == [{"id": 42}]


# ---------------------------------------------------------------------------
# fetch_api_data
# ---------------------------------------------------------------------------


def test_fetch_api_data_calls_fetcher():
    captured = {}

    def mock_fetcher(url):
        captured["url"] = url
        return {"data": "test"}

    result = fetch_api_data("bsee", "Production", fetcher=mock_fetcher)
    assert "url" in captured
    assert result == {"data": "test"}


def test_fetch_api_data_includes_api_key_from_env():
    captured = {}

    def mock_fetcher(url):
        captured["url"] = url
        return {"data": "ok"}

    with patch.dict(os.environ, {"EIA_API_KEY": "envkey123"}):
        fetch_api_data("eia", "petroleum/summary", fetcher=mock_fetcher)

    assert "api_key=envkey123" in captured["url"]


def test_fetch_api_data_saves_to_output_dir(tmp_path):
    def mock_fetcher(url):
        return {"result": [1, 2, 3]}

    fetch_api_data("bsee", "Production", output_dir=str(tmp_path), fetcher=mock_fetcher)

    saved_files = list(tmp_path.glob("*.json"))
    assert len(saved_files) == 1
    content = json.loads(saved_files[0].read_text())
    assert content == {"result": [1, 2, 3]}


def test_fetch_api_data_returns_parsed_json():
    def mock_fetcher(url):
        return [{"id": 1}, {"id": 2}]

    result = fetch_api_data("eia", "petroleum/summary", fetcher=mock_fetcher)
    assert isinstance(result, list)
    assert len(result) == 2
