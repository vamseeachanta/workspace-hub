# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "beautifulsoup4", "requests"]
# ///
"""Tests for end_to_end_online_extraction pipeline."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.data.doc_intelligence.end_to_end_online_extraction import (
    create_pipeline_config,
    run_pipeline,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _empty_config(tmp_path: Path) -> dict:
    return {
        "seed_urls": [],
        "allowed_domains": [],
        "output_dir": str(tmp_path),
        "domain": "test",
        "deduplicate": True,
        "archive": False,
        "batch_size": 10,
    }


# ---------------------------------------------------------------------------
# run_pipeline — report structure
# ---------------------------------------------------------------------------


def test_run_pipeline_returns_report(tmp_path):
    config = _empty_config(tmp_path)
    report = run_pipeline(config)
    assert "urls_found" in report
    assert "fetched" in report
    assert "extracted" in report
    assert "deduplicated" in report
    assert "errors" in report


def test_run_pipeline_empty_seeds_zero_urls(tmp_path):
    config = _empty_config(tmp_path)
    report = run_pipeline(config)
    assert report["urls_found"] == 0
    assert report["fetched"] == 0


def test_run_pipeline_errors_is_list(tmp_path):
    config = _empty_config(tmp_path)
    report = run_pipeline(config)
    assert isinstance(report["errors"], list)


# ---------------------------------------------------------------------------
# run_pipeline — error handling
# ---------------------------------------------------------------------------


def test_pipeline_report_tracks_errors(tmp_path):
    config = {
        "seed_urls": ["not-a-url"],
        "allowed_domains": [],
        "output_dir": str(tmp_path),
        "domain": "test",
        "deduplicate": False,
        "archive": False,
        "batch_size": 10,
    }
    # Should not raise — fault tolerant
    report = run_pipeline(config)
    assert isinstance(report["errors"], list)


def test_pipeline_does_not_raise_on_bad_seed(tmp_path):
    config = {
        "seed_urls": ["http://this-host-does-not-exist-xyz.invalid/doc.pdf"],
        "allowed_domains": [],
        "output_dir": str(tmp_path),
        "domain": "test",
        "deduplicate": False,
        "archive": False,
        "batch_size": 10,
    }
    mock_fetcher = MagicMock()
    mock_fetcher.fetch.side_effect = Exception("network error")
    # Must not raise
    report = run_pipeline(config, fetcher=mock_fetcher)
    assert isinstance(report, dict)


# ---------------------------------------------------------------------------
# run_pipeline — with mocked URLs found
# ---------------------------------------------------------------------------


def test_pipeline_counts_urls_found(tmp_path):
    config = {
        "seed_urls": ["https://example.com/index.html"],
        "allowed_domains": [],
        "output_dir": str(tmp_path),
        "domain": "structural",
        "deduplicate": True,
        "archive": False,
        "batch_size": 10,
    }

    with patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction.crawl_seed_urls",
        return_value=["https://example.com/a.pdf", "https://example.com/b.pdf"],
    ), patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction.create_queue",
    ), patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction.process_queue",
    ), patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction._collect_fetched_files",
        return_value=[],
    ):
        report = run_pipeline(config)

    assert report["urls_found"] == 2


def test_pipeline_fetched_count_matches_files(tmp_path):
    doc_path = tmp_path / "doc.pdf"
    doc_path.write_bytes(b"%PDF fake")

    config = {
        "seed_urls": ["https://example.com/"],
        "allowed_domains": [],
        "output_dir": str(tmp_path),
        "domain": "structural",
        "deduplicate": False,
        "archive": False,
        "batch_size": 5,
    }

    with patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction.crawl_seed_urls",
        return_value=["https://example.com/doc.pdf"],
    ), patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction.create_queue",
    ), patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction.process_queue",
    ), patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction._collect_fetched_files",
        return_value=[str(doc_path)],
    ), patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction.extract_document",
        return_value={"sections": [], "tables": [], "figure_refs": []},
    ):
        report = run_pipeline(config)

    assert report["fetched"] == 1


# ---------------------------------------------------------------------------
# create_pipeline_config
# ---------------------------------------------------------------------------


def test_create_pipeline_config(tmp_path):
    seed_file = tmp_path / "seeds.txt"
    seed_file.write_text("https://example.com\nhttps://other.org\n")
    config = create_pipeline_config(str(seed_file), str(tmp_path / "out"))
    assert len(config["seed_urls"]) == 2
    assert config["output_dir"] == str(tmp_path / "out")


def test_create_pipeline_config_filters_blank_lines(tmp_path):
    seed_file = tmp_path / "seeds.txt"
    seed_file.write_text("https://a.com\n\n  \nhttps://b.com\n")
    config = create_pipeline_config(str(seed_file), str(tmp_path / "out"))
    assert len(config["seed_urls"]) == 2


def test_create_pipeline_config_kwargs(tmp_path):
    seed_file = tmp_path / "seeds.txt"
    seed_file.write_text("https://a.com\n")
    config = create_pipeline_config(
        str(seed_file),
        str(tmp_path / "out"),
        domain="naval",
        category="structural",
        subcategory="fatigue",
        archive=True,
        batch_size=5,
    )
    assert config["domain"] == "naval"
    assert config["category"] == "structural"
    assert config["subcategory"] == "fatigue"
    assert config["archive"] is True
    assert config["batch_size"] == 5


def test_create_pipeline_config_defaults(tmp_path):
    seed_file = tmp_path / "seeds.txt"
    seed_file.write_text("https://a.com\n")
    config = create_pipeline_config(str(seed_file), str(tmp_path / "out"))
    assert "domain" in config
    assert "deduplicate" in config
    assert "archive" in config
    assert "batch_size" in config


# ---------------------------------------------------------------------------
# run_pipeline — archive flag
# ---------------------------------------------------------------------------


def test_pipeline_archive_flag_calls_manifest_to_archive(tmp_path):
    config = {
        "seed_urls": [],
        "allowed_domains": [],
        "output_dir": str(tmp_path),
        "domain": "test",
        "category": "pipeline",
        "subcategory": "wall_thickness",
        "deduplicate": True,
        "archive": True,
        "batch_size": 10,
    }

    with patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction.crawl_seed_urls",
        return_value=[],
    ), patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction.manifest_to_archive",
    ) as mock_archive:
        run_pipeline(config)
        # With zero documents, archive should still be called on merged manifest
        mock_archive.assert_called_once()


def test_pipeline_no_archive_skips_manifest_to_archive(tmp_path):
    config = _empty_config(tmp_path)
    config["archive"] = False

    with patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction.crawl_seed_urls",
        return_value=[],
    ), patch(
        "scripts.data.doc_intelligence.end_to_end_online_extraction.manifest_to_archive",
    ) as mock_archive:
        run_pipeline(config)
        mock_archive.assert_not_called()
