"""robots.txt integration in safe_request() — #1707 / #2348 plan v3 §A.

ABOUTME: Asserts the scanner consults robots.txt per destination netloc, caches
the parser, skips disallowed fetches (returning None without calling requests.get),
treats an unreachable robots.txt as DENY (fail-closed), and honors the doc-driven
owner-override set for KEEP-directive sources whose robots.txt refuses us.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gtm" / "job-market-scanner.py"
SPEC = importlib.util.spec_from_file_location(
    "job_market_scanner_robots", SCRIPT_PATH
)
module = importlib.util.module_from_spec(SPEC)
sys.modules["job_market_scanner_robots"] = module
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


def _reset_robots_cache():
    module._ROBOTS_CACHE.clear()


def _mock_parser(allow: bool):
    p = MagicMock()
    p.can_fetch.return_value = allow
    p.read.return_value = None
    return p


def test_robots_parser_cached(monkeypatch):
    _reset_robots_cache()
    monkeypatch.setattr(module, "_OWNER_OVERRIDE_SOURCES", set())

    parser = _mock_parser(allow=True)
    factory = MagicMock(return_value=parser)
    monkeypatch.setattr(module.urllib.robotparser, "RobotFileParser", factory)

    module._get_robots_parser("www.indeed.com")
    module._get_robots_parser("www.indeed.com")
    module._get_robots_parser("www.indeed.com")

    assert factory.call_count == 1
    assert parser.read.call_count == 1


def test_robots_disallow_blocks_fetch(monkeypatch):
    _reset_robots_cache()
    monkeypatch.setattr(module, "_OWNER_OVERRIDE_SOURCES", set())

    parser = _mock_parser(allow=False)
    monkeypatch.setattr(
        module.urllib.robotparser, "RobotFileParser", MagicMock(return_value=parser)
    )
    with patch.object(module.requests, "get") as mock_get:
        with patch.object(module.time, "sleep"):
            response = module.safe_request(
                "https://www.indeed.com/jobs?q=x",
                source="indeed",
            )
    assert response is None
    mock_get.assert_not_called()


def test_robots_unreachable_fails_closed(monkeypatch):
    _reset_robots_cache()
    monkeypatch.setattr(module, "_OWNER_OVERRIDE_SOURCES", set())

    parser = MagicMock()
    parser.read.side_effect = RuntimeError("boom")
    monkeypatch.setattr(
        module.urllib.robotparser, "RobotFileParser", MagicMock(return_value=parser)
    )

    with patch.object(module.requests, "get") as mock_get:
        with patch.object(module.time, "sleep"):
            response = module.safe_request(
                "https://www.indeed.com/jobs?q=x",
                source="indeed",
            )
    assert response is None
    mock_get.assert_not_called()


def test_owner_override_bypasses_disallow(monkeypatch):
    _reset_robots_cache()
    monkeypatch.setattr(module, "_OWNER_OVERRIDE_SOURCES", {"linkedin"})

    parser = _mock_parser(allow=False)
    monkeypatch.setattr(
        module.urllib.robotparser, "RobotFileParser", MagicMock(return_value=parser)
    )

    ok_response = MagicMock()
    ok_response.status_code = 200
    ok_response.headers = {}
    ok_response.raise_for_status.return_value = None

    with patch.object(module.requests, "get", return_value=ok_response) as mock_get:
        with patch.object(module.time, "sleep"):
            response = module.safe_request(
                "https://www.linkedin.com/jobs/search/",
                source="linkedin",
            )
    assert response is ok_response
    assert mock_get.call_count == 1


def test_owner_override_bypasses_unreachable_robots(monkeypatch):
    _reset_robots_cache()
    monkeypatch.setattr(module, "_OWNER_OVERRIDE_SOURCES", {"linkedin"})

    parser = MagicMock()
    parser.read.side_effect = RuntimeError("network gone")
    monkeypatch.setattr(
        module.urllib.robotparser, "RobotFileParser", MagicMock(return_value=parser)
    )

    ok_response = MagicMock()
    ok_response.status_code = 200
    ok_response.headers = {}
    ok_response.raise_for_status.return_value = None

    with patch.object(module.requests, "get", return_value=ok_response) as mock_get:
        with patch.object(module.time, "sleep"):
            response = module.safe_request(
                "https://www.linkedin.com/jobs/search/",
                source="linkedin",
            )
    assert response is ok_response
    assert mock_get.call_count == 1


def test_robots_allow_proceeds(monkeypatch):
    """Baseline: when robots allows, request proceeds normally (no override needed)."""
    _reset_robots_cache()
    monkeypatch.setattr(module, "_OWNER_OVERRIDE_SOURCES", set())

    parser = _mock_parser(allow=True)
    monkeypatch.setattr(
        module.urllib.robotparser, "RobotFileParser", MagicMock(return_value=parser)
    )

    ok_response = MagicMock()
    ok_response.status_code = 200
    ok_response.headers = {}
    ok_response.raise_for_status.return_value = None

    with patch.object(module.requests, "get", return_value=ok_response) as mock_get:
        with patch.object(module.time, "sleep"):
            response = module.safe_request(
                "https://boards.example.com/jobs",
                source="example-board",
            )
    assert response is ok_response
    assert mock_get.call_count == 1
