"""Tests for fetch_queue_manager — TDD: tests written before implementation."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import yaml
import pytest

from scripts.data.doc_intelligence.fetch_queue_manager import (
    create_queue,
    get_domain_stats,
    process_queue,
)


# ---------------------------------------------------------------------------
# create_queue
# ---------------------------------------------------------------------------


def test_create_queue_from_url_list(tmp_path):
    urls = [
        "https://example.com/doc1.pdf",
        "https://example.com/doc2.pdf",
        "https://other.org/page.html",
    ]
    queue_path = tmp_path / "queue.yaml"
    create_queue(urls, queue_path)
    data = yaml.safe_load(queue_path.read_text())
    assert len(data["documents"]) == 3
    assert all(d["status"] == "pending" for d in data["documents"])


def test_create_queue_sets_domain(tmp_path):
    urls = ["https://example.com/doc.pdf"]
    queue_path = tmp_path / "queue.yaml"
    create_queue(urls, queue_path)
    data = yaml.safe_load(queue_path.read_text())
    assert data["documents"][0]["domain"] == "example.com"


def test_create_queue_deduplicates_urls(tmp_path):
    urls = ["https://example.com/doc.pdf", "https://example.com/doc.pdf"]
    queue_path = tmp_path / "queue.yaml"
    create_queue(urls, queue_path)
    data = yaml.safe_load(queue_path.read_text())
    assert len(data["documents"]) == 1


def test_create_queue_empty_url_list(tmp_path):
    queue_path = tmp_path / "queue.yaml"
    create_queue([], queue_path)
    data = yaml.safe_load(queue_path.read_text())
    assert data["documents"] == []
    assert "created_at" in data


def test_create_queue_has_created_at(tmp_path):
    queue_path = tmp_path / "queue.yaml"
    create_queue(["https://example.com/"], queue_path)
    data = yaml.safe_load(queue_path.read_text())
    assert "created_at" in data
    # Verify it's parseable as ISO datetime
    datetime.fromisoformat(data["created_at"])


def test_create_queue_atomic_write(tmp_path):
    """Queue file should be written atomically (no .yaml.tmp left behind)."""
    urls = ["https://example.com/doc.pdf"]
    queue_path = tmp_path / "queue.yaml"
    create_queue(urls, queue_path)
    assert queue_path.exists()
    assert not (tmp_path / "queue.yaml.tmp").exists()


# ---------------------------------------------------------------------------
# get_domain_stats
# ---------------------------------------------------------------------------


def test_get_domain_stats():
    queue = {
        "documents": [
            {"url": "https://a.com/1", "domain": "a.com", "status": "pending"},
            {"url": "https://a.com/2", "domain": "a.com", "status": "completed"},
            {"url": "https://b.com/3", "domain": "b.com", "status": "pending"},
        ]
    }
    stats = get_domain_stats(queue)
    assert stats["a.com"]["pending"] == 1
    assert stats["a.com"]["completed"] == 1
    assert stats["b.com"]["pending"] == 1


def test_get_domain_stats_no_documents():
    stats = get_domain_stats({"documents": []})
    assert stats == {}


def test_get_domain_stats_missing_documents_key():
    stats = get_domain_stats({})
    assert stats == {}


def test_get_domain_stats_failed_status():
    queue = {
        "documents": [
            {"url": "https://a.com/1", "domain": "a.com", "status": "failed"},
            {"url": "https://a.com/2", "domain": "a.com", "status": "pending"},
        ]
    }
    stats = get_domain_stats(queue)
    assert stats["a.com"]["failed"] == 1
    assert stats["a.com"]["pending"] == 1
    assert stats["a.com"]["completed"] == 0


def test_get_domain_stats_mixed_statuses():
    queue = {
        "documents": [
            {"url": "https://x.io/a", "domain": "x.io", "status": "pending"},
            {"url": "https://x.io/b", "domain": "x.io", "status": "completed"},
            {"url": "https://x.io/c", "domain": "x.io", "status": "failed"},
        ]
    }
    stats = get_domain_stats(queue)
    assert stats["x.io"] == {"pending": 1, "completed": 1, "failed": 1}


# ---------------------------------------------------------------------------
# process_queue (mock fetcher — no real network calls)
# ---------------------------------------------------------------------------


def _make_fake_fetcher(content: bytes = b"<html>ok</html>", content_type: str = "text/html"):
    """Return a fake fetcher whose fetch() returns a FetchResult-like object."""
    result = MagicMock()
    result.content_bytes = content
    result.content_type = content_type
    result.status_code = 200
    fetcher = MagicMock()
    fetcher.fetch.return_value = result
    return fetcher


def test_process_queue_marks_completed(tmp_path):
    urls = ["https://example.com/doc.html"]
    queue_path = tmp_path / "queue.yaml"
    create_queue(urls, queue_path)

    output_dir = tmp_path / "output"
    fake_fetcher = _make_fake_fetcher()

    process_queue(queue_path, output_dir, fetcher=fake_fetcher)

    data = yaml.safe_load(queue_path.read_text())
    assert data["documents"][0]["status"] == "completed"
    assert "output_path" in data["documents"][0]
    assert "fetched_at" in data["documents"][0]


def test_process_queue_saves_content_to_output_dir(tmp_path):
    urls = ["https://example.com/doc.html"]
    queue_path = tmp_path / "queue.yaml"
    create_queue(urls, queue_path)

    output_dir = tmp_path / "output"
    fake_fetcher = _make_fake_fetcher(content=b"hello world")

    process_queue(queue_path, output_dir, fetcher=fake_fetcher)

    data = yaml.safe_load(queue_path.read_text())
    saved_path = Path(data["documents"][0]["output_path"])
    assert saved_path.exists()
    assert saved_path.read_bytes() == b"hello world"


def test_process_queue_skips_completed(tmp_path):
    queue_path = tmp_path / "queue.yaml"
    queue = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "documents": [
            {
                "url": "https://example.com/done.html",
                "domain": "example.com",
                "status": "completed",
                "output_path": str(tmp_path / "done.html"),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        ],
    }
    import yaml as _yaml
    queue_path.write_text(_yaml.dump(queue))

    output_dir = tmp_path / "output"
    fake_fetcher = _make_fake_fetcher()

    process_queue(queue_path, output_dir, fetcher=fake_fetcher)

    # fetch should never have been called since the item was already completed
    fake_fetcher.fetch.assert_not_called()


def test_process_queue_marks_failed_on_error(tmp_path):
    urls = ["https://example.com/bad.html"]
    queue_path = tmp_path / "queue.yaml"
    create_queue(urls, queue_path)

    output_dir = tmp_path / "output"
    broken_fetcher = MagicMock()
    broken_fetcher.fetch.side_effect = RuntimeError("network error")

    process_queue(queue_path, output_dir, fetcher=broken_fetcher)

    data = yaml.safe_load(queue_path.read_text())
    doc = data["documents"][0]
    assert doc["status"] == "failed"
    assert "error" in doc


def test_process_queue_none_fetch_result_marks_failed(tmp_path):
    """If fetcher returns None (robots.txt blocked), mark as failed."""
    urls = ["https://example.com/blocked.html"]
    queue_path = tmp_path / "queue.yaml"
    create_queue(urls, queue_path)

    output_dir = tmp_path / "output"
    blocking_fetcher = MagicMock()
    blocking_fetcher.fetch.return_value = None

    process_queue(queue_path, output_dir, fetcher=blocking_fetcher)

    data = yaml.safe_load(queue_path.read_text())
    assert data["documents"][0]["status"] == "failed"


def test_process_queue_creates_output_dir(tmp_path):
    urls = ["https://example.com/doc.html"]
    queue_path = tmp_path / "queue.yaml"
    create_queue(urls, queue_path)

    output_dir = tmp_path / "nested" / "output"
    assert not output_dir.exists()

    fake_fetcher = _make_fake_fetcher()
    process_queue(queue_path, output_dir, fetcher=fake_fetcher)

    assert output_dir.exists()
