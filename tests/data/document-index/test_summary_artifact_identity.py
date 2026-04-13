#!/usr/bin/env python3
# ABOUTME: TDD tests for summary-artifact identity normalization (#2246)
# ABOUTME: Proves Phase B writers and Phase C readers agree on canonical filename keying

"""
Tests for normalized summary-artifact identity between Phase B and Phase C.

The canonical contract:
- Records with content_hash → filename is {content_hash}.json
- Records without content_hash → filename is sha256(path)[:16].json (deterministic fallback)

Both Phase B producers and Phase C consumer must agree on the same key.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts" / "data" / "document-index"


def _import_hyphenated(module_name: str, file_name: str):
    """Import a module from a file with hyphens in the name."""
    spec = importlib.util.spec_from_file_location(module_name, SCRIPTS_DIR / file_name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


phase_b_extract = _import_hyphenated("phase_b_extract", "phase-b-extract.py")
phase_c_classify = _import_hyphenated("phase_c_classify", "phase-c-classify.py")


# ── Fixtures ────────────────────────────────────────────────────────────────


SAMPLE_CONTENT_HASH = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
SAMPLE_PATH = "/mnt/data/standards/API-RP-2A.pdf"
SAMPLE_RECORD_WITH_HASH = {
    "content_hash": SAMPLE_CONTENT_HASH,
    "path": SAMPLE_PATH,
    "source": "og_standards",
}
SAMPLE_RECORD_NO_HASH = {
    "path": SAMPLE_PATH,
    "source": "og_standards",
}
SAMPLE_RECORD_EMPTY_HASH = {
    "content_hash": "",
    "path": SAMPLE_PATH,
    "source": "og_standards",
}


# ── Test: Phase B extract key derivation is canonical ───────────────────────


class TestSummaryKeyCanonical:
    """summary_key_for must return raw content_hash when available."""

    def test_content_hash_record_returns_raw_hash(self):
        """Key for record with content_hash must be the raw content_hash itself."""
        key = phase_b_extract.summary_key_for(SAMPLE_RECORD_WITH_HASH)
        assert key == SAMPLE_CONTENT_HASH, (
            f"Expected raw content_hash '{SAMPLE_CONTENT_HASH}', "
            f"got '{key}' — Phase B extract is hashing the hash"
        )

    def test_fallback_without_content_hash_is_deterministic(self):
        """Key for record without content_hash must be deterministic from path."""
        key1 = phase_b_extract.summary_key_for(SAMPLE_RECORD_NO_HASH)
        key2 = phase_b_extract.summary_key_for(SAMPLE_RECORD_NO_HASH)
        assert key1 == key2, "Fallback key must be deterministic"
        assert len(key1) > 0, "Fallback key must not be empty"

    def test_fallback_with_empty_content_hash_uses_path(self):
        """Empty content_hash should fall back to path-based key."""
        key = phase_b_extract.summary_key_for(SAMPLE_RECORD_EMPTY_HASH)
        # Must not be empty-string hash — should fall back to path
        empty_sha = hashlib.sha256(b"").hexdigest()
        assert key != empty_sha, "Empty content_hash must fall back to path-based key"
        assert len(key) > 0


# ── Test: claude-worker and Phase C agree on filename ───────────────────────


class TestCrossPhaseFilenameAgreement:
    """Phase B claude-worker writes {sha}.json; Phase C reads {sha}.json."""

    def test_claude_worker_file_resolvable_by_phase_c(self, tmp_path):
        """A summary written by claude-worker must be findable by Phase C get_summary."""
        # Simulate what claude-worker does: write {content_hash}.json
        sha = SAMPLE_CONTENT_HASH
        summary_data = {
            "sha256": sha,
            "discipline": "marine",
            "summary": "Mooring analysis standard",
            "keywords": ["mooring"],
        }
        (tmp_path / f"{sha}.json").write_text(json.dumps(summary_data))

        # Phase C should find it
        summaries_cache = {}
        result = phase_c_classify.get_summary(summaries_cache, tmp_path, SAMPLE_PATH, sha)
        assert result is not None, "Phase C must find summary written by claude-worker"
        assert result["discipline"] == "marine"

    def test_phase_b_extract_file_resolvable_by_phase_c(self, tmp_path):
        """A summary written by phase-b-extract must be findable by Phase C get_summary."""
        # Phase B extract writes a summary
        record = SAMPLE_RECORD_WITH_HASH.copy()
        key = phase_b_extract.summary_key_for(record)
        phase_b_extract.write_summary(tmp_path, key, record, "sample text", "pdftotext", None)

        # Phase C should find it using the record's content_hash
        summaries_cache = {}
        sha = record["content_hash"]
        result = phase_c_classify.get_summary(summaries_cache, tmp_path, record["path"], sha)
        assert result is not None, (
            f"Phase C cannot find summary written by Phase B extract. "
            f"Phase B wrote key='{key}', Phase C looked for sha='{sha}'"
        )


# ── Test: fallback key matches across phases ────────────────────────────────


class TestFallbackKeyAgreement:
    """When content_hash is missing, all phases must agree on the fallback key."""

    def test_phase_b_extract_fallback_file_retrievable(self, tmp_path):
        """Summary for no-hash record written by Phase B must be retrievable."""
        record = SAMPLE_RECORD_NO_HASH.copy()
        key = phase_b_extract.summary_key_for(record)
        phase_b_extract.write_summary(tmp_path, key, record, "sample text", "direct", None)

        # The file must exist on disk
        expected_file = tmp_path / f"{key}.json"
        assert expected_file.exists(), f"Summary file not written at {expected_file}"

        # Verify it's loadable
        data = json.loads(expected_file.read_text())
        assert data["path"] == SAMPLE_PATH

    def test_fallback_key_differs_from_content_hash_key(self):
        """Fallback key (from path) must differ from content_hash key."""
        key_with_hash = phase_b_extract.summary_key_for(SAMPLE_RECORD_WITH_HASH)
        key_no_hash = phase_b_extract.summary_key_for(SAMPLE_RECORD_NO_HASH)
        assert key_with_hash != key_no_hash, (
            "Records with and without content_hash must produce different keys"
        )
