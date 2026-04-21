"""Tests for GTM job market scanner deduplication and request compliance.

ABOUTME: Covers #1708 and #1707 by validating dedup keys include stable
posting identifiers and request handling respects Retry-After/backoff hooks.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gtm" / "job-market-scanner.py"
SPEC = importlib.util.spec_from_file_location("job_market_scanner", SCRIPT_PATH)
job_market_scanner = importlib.util.module_from_spec(SPEC)
sys.modules["job_market_scanner"] = job_market_scanner
assert SPEC and SPEC.loader
SPEC.loader.exec_module(job_market_scanner)


def test_job_id_changes_for_different_urls():
    base = job_market_scanner.job_id(
        title="Senior Offshore Engineer",
        company="Acme Energy",
        location="Houston, TX",
        source="indeed",
        url="https://jobs.example.com/123",
        posted_date="2026-04-01",
    )
    changed_url = job_market_scanner.job_id(
        title="Senior Offshore Engineer",
        company="Acme Energy",
        location="Houston, TX",
        source="indeed",
        url="https://jobs.example.com/456",
        posted_date="2026-04-01",
    )
    assert base != changed_url


def test_job_id_changes_for_different_post_dates():
    earlier = job_market_scanner.job_id(
        title="Senior Offshore Engineer",
        company="Acme Energy",
        location="Houston, TX",
        source="indeed",
        url="https://jobs.example.com/123",
        posted_date="2026-04-01",
    )
    repost = job_market_scanner.job_id(
        title="Senior Offshore Engineer",
        company="Acme Energy",
        location="Houston, TX",
        source="indeed",
        url="https://jobs.example.com/123",
        posted_date="2026-04-08",
    )
    assert earlier != repost


def test_job_id_changes_for_different_sources():
    indeed_id = job_market_scanner.job_id(
        title="Senior Offshore Engineer",
        company="Acme Energy",
        location="Houston, TX",
        source="indeed",
        url="https://jobs.example.com/123",
        posted_date="2026-04-01",
    )
    linkedin_id = job_market_scanner.job_id(
        title="Senior Offshore Engineer",
        company="Acme Energy",
        location="Houston, TX",
        source="linkedin",
        url="https://jobs.example.com/123",
        posted_date="2026-04-01",
    )
    assert indeed_id != linkedin_id


def test_safe_request_respects_retry_after_header():
    first = MagicMock()
    first.raise_for_status.side_effect = job_market_scanner.requests.HTTPError("429")
    first.status_code = 429
    first.headers = {"Retry-After": "7"}

    second = MagicMock()
    second.raise_for_status.return_value = None
    second.status_code = 200
    second.headers = {}

    with patch.object(job_market_scanner.requests, "get", side_effect=[first, second]) as mock_get:
        with patch.object(job_market_scanner.time, "sleep") as mock_sleep:
            response = job_market_scanner.safe_request(
                "https://boards.example.com/jobs",
                source="example-board",
            )

    assert response is second
    assert mock_get.call_count == 2
    assert any(call.args[0] == 7 for call in mock_sleep.call_args_list)


def test_safe_request_rejects_disallowed_source():
    with patch.object(job_market_scanner.requests, "get") as mock_get:
        response = job_market_scanner.safe_request(
            "https://unknown.example.com/jobs",
            source="unknown-board",
        )
    assert response is None
    mock_get.assert_not_called()


def test_safe_request_rejects_url_outside_source_allowlist():
    with patch.object(job_market_scanner.requests, "get") as mock_get:
        response = job_market_scanner.safe_request(
            "https://evil.example.com/jobs",
            source="indeed",
        )
    assert response is None
    mock_get.assert_not_called()


def test_update_cumulative_index_migrates_legacy_job_ids(tmp_path, monkeypatch):
    cumulative_path = tmp_path / "cumulative-index.json"
    monkeypatch.setattr(job_market_scanner, "CUMULATIVE_PATH", cumulative_path)

    legacy_key = job_market_scanner.legacy_job_id(
        "Senior Offshore Engineer", "Acme Energy", "Houston, TX"
    )
    cumulative_path.write_text(
        job_market_scanner.json.dumps(
            {
                "jobs": {
                    legacy_key: {
                        "title": "Senior Offshore Engineer",
                        "company": "Acme Energy",
                        "location": "Houston, TX",
                        "source": "indeed",
                        "search_keyword": "offshore engineer",
                        "alignment_score": 88,
                        "first_seen": "2026-03-25",
                        "last_seen": "2026-03-25",
                        "seen_count": 1,
                    }
                },
                "scan_history": [],
                "company_history": {},
            }
        )
    )

    result = {
        "meta": {"total_jobs": 1, "total_unique_companies": 1},
        "jobs": [
            {
                "title": "Senior Offshore Engineer",
                "company": "Acme Energy",
                "location": "Houston, TX",
                "source": "indeed",
                "url": "https://www.indeed.com/viewjob?jk=123",
                "posted_date": "2026-04-01",
                "search_keyword": "offshore engineer",
                "alignment_score": 90,
            }
        ],
    }

    updated = job_market_scanner.update_cumulative_index(result, "2026-04-02")
    assert len(updated["new_jobs"]) == 0
    assert len(updated["returning_jobs"]) == 1
    cumulative = job_market_scanner.load_cumulative_index()
    assert legacy_key not in cumulative["jobs"]
    new_key = job_market_scanner.job_id(
        "Senior Offshore Engineer",
        "Acme Energy",
        "Houston, TX",
        source="indeed",
        url="https://www.indeed.com/viewjob?jk=123",
        posted_date="2026-04-01",
    )
    assert cumulative["jobs"][new_key]["seen_count"] == 2
